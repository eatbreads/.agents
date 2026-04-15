"""FSX 固定五条流水线看护 + 飞书发布总控脚本。"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import watch_fixed_pipelines
from config_loader import get_chat_ids, get_viewer_department_ids, load_local_config


CONFIG = load_local_config()
CHAT_IDS = get_chat_ids(CONFIG)
SPREADSHEET_TITLE_PREFIX = str(CONFIG["spreadsheet_title_prefix"])
DEFAULT_OUTPUT_DIR = SCRIPT_DIR
OVERVIEW_FILENAME = "overview_all.csv"
JOBS_FILENAME = "jobs_all.csv"
TOP10_FILENAME = "top10_jobs_all.csv"
SHEETS_IDENTITY = str(CONFIG["sheets_identity"])
IM_IDENTITY = str(CONFIG["im_identity"])
VIEWER_DEPARTMENT_IDS = get_viewer_department_ids(CONFIG)
ENABLE_COCO = False


class PublishError(RuntimeError):
    """Top-level publishing error."""


@dataclass
class ResourceRef:
    token: str
    url: str = ""


def _extract_json_object(text: str) -> Dict[str, Any]:
    stripped = text.strip()
    try:
        data = json.loads(stripped)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        candidate = stripped[start : end + 1]
        data = json.loads(candidate)
        if isinstance(data, dict):
            return data
    raise ValueError(f"Unable to parse JSON object from output: {text[:200]}")


def _run_command(args: Sequence[str], *, parse_json: bool = False) -> Any:
    completed = subprocess.run(
        list(args),
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise PublishError(completed.stderr.strip() or completed.stdout.strip() or "command failed")
    if not parse_json:
        return completed.stdout
    return _extract_json_object(completed.stdout)


def _deep_get(data: Any, keys: Iterable[str]) -> Optional[Any]:
    if isinstance(data, dict):
        for key in keys:
            if key in data and data[key] not in (None, ""):
                return data[key]
        for value in data.values():
            found = _deep_get(value, keys)
            if found not in (None, ""):
                return found
    elif isinstance(data, list):
        for item in data:
            found = _deep_get(item, keys)
            if found not in (None, ""):
                return found
    return None


def run_watch_pipeline(output_dir: Path) -> Dict[str, Any]:
    return watch_fixed_pipelines.run_all_watches(output_dir=str(output_dir))


def _today_prefix(now: Optional[datetime] = None) -> str:
    return (now or datetime.now()).strftime("%Y-%m-%d")


def _time_suffix(now: Optional[datetime] = None) -> str:
    return (now or datetime.now()).strftime("%H%M")


def build_spreadsheet_title(now: Optional[datetime] = None) -> str:
    return f"{SPREADSHEET_TITLE_PREFIX}-{_today_prefix(now)}"


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def create_spreadsheet(now: Optional[datetime] = None) -> ResourceRef:
    payload = _run_command(
        [
            "lark-cli",
            "sheets",
            "+create",
            "--as",
            SHEETS_IDENTITY,
            "--title",
            build_spreadsheet_title(now),
        ],
        parse_json=True,
    )
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        raise PublishError(f"Unexpected spreadsheet create payload: {json.dumps(payload, ensure_ascii=False)}")
    token = str(data.get("spreadsheet_token") or "")
    url = str(data.get("url") or "")
    if not token:
        raise PublishError(f"Spreadsheet created but token missing: {json.dumps(payload, ensure_ascii=False)}")
    return ResourceRef(token=token, url=url)


def get_default_sheet_id(spreadsheet_token: str) -> str:
    payload = _run_command(
        [
            "lark-cli",
            "sheets",
            "+info",
            "--as",
            SHEETS_IDENTITY,
            "--spreadsheet-token",
            spreadsheet_token,
        ],
        parse_json=True,
    )
    data = payload.get("data") if isinstance(payload, dict) else None
    sheets_obj = data.get("sheets") if isinstance(data, dict) else None
    sheets = sheets_obj.get("sheets") if isinstance(sheets_obj, dict) else None
    if isinstance(sheets, list) and sheets:
        sheet_id = str(sheets[0].get("sheet_id") or "")
        if sheet_id:
            return sheet_id
    raise PublishError(f"Failed to resolve default sheet id: {json.dumps(payload, ensure_ascii=False)}")


def build_combined_sheet_values(output_dir: Path, now: Optional[datetime] = None) -> List[List[str]]:
    date_prefix = _today_prefix(now)
    sections = [
        (f"{date_prefix} 总览", output_dir / OVERVIEW_FILENAME),
        (f"{date_prefix} TOP10", output_dir / TOP10_FILENAME),
        (f"{date_prefix} 全量", output_dir / JOBS_FILENAME),
    ]
    combined_rows: List[List[str]] = []
    for index, (title, csv_path) in enumerate(sections):
        combined_rows.append([title])
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            combined_rows.extend(list(csv.reader(f)))
        if index != len(sections) - 1:
            combined_rows.extend([[], [], []])
    return combined_rows


def write_combined_sheet(spreadsheet_token: str, sheet_id: str, values: List[List[str]]) -> Dict[str, Any]:
    return _run_command(
        [
            "lark-cli",
            "sheets",
            "+write",
            "--as",
            SHEETS_IDENTITY,
            "--spreadsheet-token",
            spreadsheet_token,
            "--range",
            f"{sheet_id}!A1",
            "--values",
            json.dumps(values, ensure_ascii=False),
        ],
        parse_json=True,
    )


def grant_department_view_permissions(spreadsheet_token: str, department_ids: Sequence[str]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for department_id in department_ids:
        payload = _run_command(
            [
                "lark-cli",
                "drive",
                "permission.members",
                "create",
                "--as",
                SHEETS_IDENTITY,
                "--params",
                json.dumps(
                    {
                        "token": spreadsheet_token,
                        "type": "sheet",
                        "need_notification": False,
                    },
                    ensure_ascii=False,
                ),
                "--data",
                json.dumps(
                    {
                        "type": "department",
                        "member_type": "opendepartmentid",
                        "member_id": department_id,
                        "perm": "view",
                    },
                    ensure_ascii=False,
                ),
            ],
            parse_json=True,
        )
        results.append(payload)
    return results


def cleanup_local_outputs(output_dir: Path) -> List[str]:
    removed: List[str] = []
    for filename in [OVERVIEW_FILENAME, TOP10_FILENAME, JOBS_FILENAME]:
        path = output_dir / filename
        if path.exists():
            path.unlink()
            removed.append(filename)
    return removed


def _parse_int(value: str) -> int:
    try:
        return int(str(value).replace(",", "").strip())
    except Exception:
        return 0


def _parse_float(value: str) -> float:
    try:
        return float(str(value).replace("%", "").replace(",", "").strip())
    except Exception:
        return 0.0


def build_rule_fallback_report(
    overview_rows: List[Dict[str, str]],
    now: Optional[datetime] = None,
) -> str:
    date_prefix = _today_prefix(now)
    total_case_num = sum(_parse_int(row.get("总用例数", "0")) for row in overview_rows)
    total_failed = sum(_parse_int(row.get("总失败", "0")) for row in overview_rows)
    total_skipped = sum(_parse_int(row.get("总跳过", "0")) for row in overview_rows)
    total_succeed = sum(_parse_int(row.get("总成功", "0")) for row in overview_rows)
    total_pass_rate = (total_succeed / total_case_num * 100) if total_case_num else 0.0

    lines = [
        f"FSX 核心流水线每日看护报告（{date_prefix}）",
        "",
        f"标题：{date_prefix} FSX 客户端与代理流水线运行日报",
        "",
        "总体概览：",
        (
            f"- 本次统计共 {len(overview_rows)} 条流水线参与运行，其中 "
            f"{sum(1 for row in overview_rows if _parse_int(row.get('总失败', '0')) == 0)} 条流水线全部通过，"
            f"{sum(1 for row in overview_rows if _parse_int(row.get('总失败', '0')) > 0)} 条流水线存在失败。"
        ),
        (
            f"- 五条流水线总计执行 {total_case_num:,} 条用例，失败 {total_failed}、成功 {total_succeed}、"
            f"跳过 {total_skipped}，整体通过率 {total_pass_rate:.2f}%。"
        ),
        "",
        "各流水线运行情况汇总：",
    ]

    for row in overview_rows:
        pipeline_name = row.get("pipeline_name", "")
        failed = _parse_int(row.get("总失败", "0"))
        skipped = _parse_int(row.get("总跳过", "0"))
        if failed > 0:
            status = "整体稳定，存在少量失败需跟进。"
        elif skipped > 0:
            status = "本次运行无失败，存在跳过用例。"
        else:
            status = "本次运行全部通过。"
        lines.append(
            (
                f"- `{pipeline_name}`：共 {row.get('总用例数', '0')} 条用例，"
                f"失败 {row.get('总失败', '0')}、成功 {row.get('总成功', '0')}、"
                f"跳过 {row.get('总跳过', '0')}，通过率 {row.get('总通过率', '0')}%，{status}"
            )
        )
    return "\n".join(lines)


def _csv_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_coco_report(output_dir: Path) -> str:
    overview_csv = _csv_text(output_dir / OVERVIEW_FILENAME)
    top10_csv = _csv_text(output_dir / TOP10_FILENAME)
    prompt = (
        "你是 FSX 值班看护播报助手。"
        "请只基于我提供的 overview_all.csv 和 top10_jobs_all.csv 生成一份中文日报。"
        "不要编造 CSV 中不存在的数据，不要读取其他文件，不要做复杂推理。"
        "只输出最终报告正文，不要加解释，不要用 markdown 代码块包裹。"
        "输出必须尽量简短，只保留三段：标题、总体概览、各流水线运行情况汇总。"
        "不要输出重点失败节点分析、原因分析、建议、结尾、额外说明。"
        "总体概览最多 2 条 bullet。"
        "各流水线运行情况汇总中，每条流水线只用 1 条 bullet，总结总用例、失败、成功、跳过、通过率和一句简短状态。"
        "语气简洁，适合直接发飞书群。"
        "如果某条流水线没有失败，就写成全部通过；如果有失败，只写存在少量失败需跟进，不要展开 job 级分析。"
        "格式尽量贴近下面这种风格："
        "FSX 流水线运行日报\\n\\n"
        "标题：FSX 客户端与代理流水线运行日报\\n\\n"
        "总体概览：\\n"
        "- 本次统计共 5 条流水线参与运行，其中 3 条流水线全部通过，2 条流水线存在少量用例失败。\\n"
        "- 各流水线整体质量较高，功能与回归覆盖基本稳定。\\n\\n"
        "各流水线运行情况汇总：\\n"
        "- `流水线名`：共 X 条用例，失败 X、成功 X、跳过 X，通过率 XX.XX%，本次运行全部通过。"
        "\n\n【overview_all.csv】\n"
        f"{overview_csv}"
        "\n\n【top10_jobs_all.csv】\n"
        f"{top10_csv}"
    )
    result = _run_command(
        [
            "coco",
            "-p",
            "--query-timeout",
            "60s",
            prompt,
        ],
        parse_json=False,
    )
    return result.strip()


def compose_final_message(report_text: str, spreadsheet_ref: ResourceRef) -> str:
    parts = [report_text.strip()]
    if spreadsheet_ref.url:
        parts.append(f"表格链接：{spreadsheet_ref.url}")
    elif spreadsheet_ref.token:
        parts.append(f"表格 token：{spreadsheet_ref.token}")
    return "\n\n".join(part for part in parts if part)


def send_group_message(chat_id: str, message: str) -> Dict[str, Any]:
    return _run_command(
        [
            "lark-cli",
            "im",
            "+messages-send",
            "--as",
            IM_IDENTITY,
            "--chat-id",
            chat_id,
            "--text",
            message,
        ],
        parse_json=True,
    )


def send_group_messages(chat_ids: Sequence[str], message: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    success_count = 0

    for chat_id in chat_ids:
        try:
            payload = send_group_message(chat_id, message)
        except Exception as exc:
            results.append(
                {
                    "chat_id": chat_id,
                    "status": "ERROR",
                    "error": str(exc),
                }
            )
            continue

        success_count += 1
        results.append(
            {
                "chat_id": chat_id,
                "status": "OK",
                "message_id": payload.get("message_id"),
            }
        )

    if success_count == 0:
        raise PublishError("Failed to send message to all configured chats.")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="执行 FSX 固定五条流水线看护，创建新的飞书电子表格并发群消息。")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="CSV 产物输出目录。")
    parser.add_argument("--skip-watch", action="store_true", help="跳过重新执行 watch_fixed_pipelines，直接使用当前目录下已有的 3 个 CSV。")
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    now = datetime.now()
    if not args.skip_watch:
        run_watch_pipeline(output_dir)

    for filename in (OVERVIEW_FILENAME, JOBS_FILENAME, TOP10_FILENAME):
        if not (output_dir / filename).exists():
            raise PublishError(f"Missing required CSV file: {output_dir / filename}")

    spreadsheet_ref = create_spreadsheet()
    permission_results: List[Dict[str, Any]] = []
    if VIEWER_DEPARTMENT_IDS:
        permission_results = grant_department_view_permissions(
            spreadsheet_ref.token,
            VIEWER_DEPARTMENT_IDS,
        )
    sheet_id = get_default_sheet_id(spreadsheet_ref.token)
    combined_values = build_combined_sheet_values(output_dir, now)
    write_result = write_combined_sheet(spreadsheet_ref.token, sheet_id, combined_values)

    if ENABLE_COCO:
        try:
            report_text = run_coco_report(output_dir)
        except Exception:
            report_text = build_rule_fallback_report(
                read_csv_rows(output_dir / OVERVIEW_FILENAME),
                now,
            )
    else:
        report_text = build_rule_fallback_report(
            read_csv_rows(output_dir / OVERVIEW_FILENAME),
            now,
        )

    message = compose_final_message(report_text, spreadsheet_ref)
    send_results = send_group_messages(CHAT_IDS, message)
    removed_files = cleanup_local_outputs(output_dir)

    print(
        json.dumps(
            {
                "spreadsheet_token": spreadsheet_ref.token,
                "spreadsheet_url": spreadsheet_ref.url,
                "sheet_id": sheet_id,
                "permission_results": permission_results,
                "write_result": write_result.get("data", {}),
                "removed_files": removed_files,
                "send_results": send_results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
