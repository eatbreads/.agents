"""Bits 流水线测试用例统计脚本

根据给定的流水线 ID (pipelineId) 和运行 ID (runId)，汇总 `test_framework_trigger` 类型 Job 的
用例统计信息，并生成 Overview / Jobs 全量 / TOP10 三个 CSV 以及中间统计 JSON 文件。

用法示例：
    python bits_pipeline_report.py 1052255161090 1130541285378
    python bits_pipeline_report.py --pipeline-id 1052255161090 --run-id 1130541285378
    python bits_pipeline_report.py 1052255161090 1130541285378 --dry-run

可选参数：
    --dry-run  仅打印将要访问的接口和输出文件名，不发起网络请求。

说明：
- 如需访问内网 Bits API，在 AIME 环境中运行脚本时，应将任务配置为 include_secrets=true，
  并在运行环境中提供可用的 JWT（优先使用 AIME_USER_CLOUD_JWT，兼容 AIME_USER_CODE_JWT、
  USER_CLOUD_JWT、IRIS_USER_CLOUD_JWT），脚本会自动尝试多种常见头部传递方式完成鉴权。
"""

import json
import csv
import os
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_URL = "https://bits.bytedance.net"

# 可能可用的 JWT 环境变量名称（不打印、不泄露，只作为鉴权尝试）
POSSIBLE_JWT_ENV_VARS = [
    "AIME_USER_CODE_JWT",
    "AIME_USER_CLOUD_JWT",
    "USER_CLOUD_JWT",
    "IRIS_USER_CLOUD_JWT",
]

TERMINAL_RUN_STATUS_NUMBERS = {3, 8, 9}
TERMINAL_RUN_STATUS_TEXT = {
    "success",
    "succeed",
    "succeeded",
    "failed",
    "fail",
    "canceled",
    "cancelled",
    "timeout",
    "timed_out",
}

# 默认不生成 stats JSON，可通过显式参数或改这个常量打开。
DEFAULT_INCLUDE_STATS = False
OVERVIEW_HEADER = ["运行编号", "流水线ID", "runID", "总用例数", "总失败", "总成功", "总跳过", "总通过率"]
JOBS_HEADER = [
    "jobName",
    "state",
    "failed_case",
    "该节点失败数/总失败数(%)",
    "case_num",
    "该节点失败数/该节点总用例数(%)",
    "succeed_case",
    "skipped_case",
    "jobId",
    "jobRunId",
]


def fetch_json(url: str) -> Any:
    """带多种头部组合重试的通用 JSON GET 封装。"""
    base_headers: Dict[str, str] = {
        "accept": "application/json, text/plain, */*",
        "user-agent": "Aime-Agent/1.0",
    }

    token_envs: List[str] = [name for name in POSSIBLE_JWT_ENV_VARS if name in os.environ]

    attempts: List[Dict[str, str]] = []
    # 无鉴权头尝试
    attempts.append({})

    # 针对每个候选 JWT，尝试多种常见头部名称
    for env_name in token_envs:
        token = os.environ.get(env_name)
        if not token:
            continue
        attempts.append({"Authorization": f"Bearer {token}"})
        attempts.append({"X-Jwt-Token": token})
        attempts.append({"Jwt-Token": token})
        attempts.append({"jwt": token})

    last_err: Optional[Exception] = None

    for extra_headers in attempts:
        headers = dict(base_headers)
        headers.update(extra_headers)
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            return json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_err = e
            # 401/403 时尝试下一个头部组合，其它错误直接抛出
            if e.code in (401, 403):
                continue
            raise
        except Exception as e:  # 例如网络错误
            last_err = e
            continue

    if last_err is not None:
        raise last_err
    raise RuntimeError("fetch_json failed without specific error")


def safe_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None


def extract_last_run_id(pipeline_payload: Any) -> Optional[str]:
    """Best-effort extraction of the latest run id from GetPipeline payload."""
    if not isinstance(pipeline_payload, dict):
        return None

    pipeline_obj = pipeline_payload.get("pipeline")
    candidates: List[Any] = []
    if isinstance(pipeline_obj, dict):
        candidates.append(pipeline_obj.get("last_run_id"))
        nested_pipeline = pipeline_obj.get("pipeline")
        if isinstance(nested_pipeline, dict):
            candidates.append(nested_pipeline.get("last_run_id"))

    for candidate in candidates:
        run_id = safe_int(candidate)
        if run_id is not None:
            return str(run_id)
    return None


def is_finished_run_status(status: Any) -> bool:
    """Return True only for clearly terminal run states."""
    if isinstance(status, str):
        normalized = status.strip().lower()
        if normalized in TERMINAL_RUN_STATUS_TEXT:
            return True
        if normalized in {"created", "pending", "running", "blocked", "waiting"}:
            return False
        status = safe_int(normalized)

    status_num = safe_int(status)
    if status_num is None:
        return False
    return status_num in TERMINAL_RUN_STATUS_NUMBERS


def build_output_paths(
    pipeline_id: str,
    run_id: str,
    output_dir: str = ".",
    include_stats: bool = DEFAULT_INCLUDE_STATS,
) -> Dict[str, str]:
    base = Path(output_dir)
    paths = {
        "overview_csv": str(base / f"overview_{pipeline_id}_{run_id}.csv"),
        "jobs_csv": str(base / f"jobs_{pipeline_id}_{run_id}.csv"),
        "top10_csv": str(base / f"top10_jobs_{pipeline_id}_{run_id}.csv"),
    }
    if include_stats:
        paths["stats_path"] = str(base / f"stats_{pipeline_id}_{run_id}.json")
    return paths


def fetch_job_run_output(job_run_id: Optional[str], run_id: str) -> Optional[Dict[str, Any]]:
    """兜底从 jobRun 详情接口中获取 jobAtom.output。

    需要显式传入 run_id，避免对全局常量的隐式依赖。
    """
    if not job_run_id:
        return None
    url = (
        f"{BASE_URL}/api/v1/p/job_runs/{job_run_id}?needOutputs=true"
        f"&needLogs=false&needTroubleshootRecords=true&pipelineRunId={run_id}"
    )
    try:
        data = fetch_json(url)
    except Exception:
        return None

    candidates: List[Dict[str, Any]] = []
    if isinstance(data, dict):
        candidates.append(data)
        job_run_obj = data.get("jobRun")
        if isinstance(job_run_obj, dict):
            candidates.append(job_run_obj)

    for obj in candidates:
        job_atom = obj.get("jobAtom")
        if isinstance(job_atom, dict):
            output_obj = job_atom.get("output")
            if isinstance(output_obj, dict):
                return output_obj
            if isinstance(output_obj, str) and output_obj.strip():
                try:
                    parsed = json.loads(output_obj)
                except Exception:
                    parsed = None
                if isinstance(parsed, dict):
                    return parsed
    return None


def _job_row_to_csv_dict(job_row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "jobName": job_row.get("jobName", ""),
        "state": job_row.get("state", ""),
        "failed_case": job_row.get("failed_case", 0),
        "该节点失败数/总失败数(%)": f"{job_row.get('fail_share_pct', 0.0):.2f}",
        "case_num": job_row.get("case_num", 0),
        "该节点失败数/该节点总用例数(%)": f"{job_row.get('job_fail_rate', 0.0):.2f}",
        "succeed_case": job_row.get("succeed_case", 0),
        "skipped_case": job_row.get("skipped_case", 0),
        "jobId": job_row.get("jobId", ""),
        "jobRunId": job_row.get("jobRunId", ""),
    }


def build_report_data(pipeline_id: str, run_id: str, run_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build structured report data for a single pipeline run without writing files."""
    pipeline_run = run_data.get("pipelineRun") if isinstance(run_data, dict) else None
    if not isinstance(pipeline_run, dict):
        pipeline_run = run_data if isinstance(run_data, dict) else {}

    pipeline_name: Optional[str] = None
    run_seq: Optional[str] = None

    run_seq = pipeline_run.get("runSeq")
    pipeline = pipeline_run.get("pipeline") or {}
    name_obj = pipeline.get("name") or {}
    if isinstance(name_obj, dict):
        texts = name_obj.get("texts") or {}
        if isinstance(texts, dict):
            pipeline_name = name_obj.get("value") or texts.get("zh") or texts.get("en")
        else:
            pipeline_name = name_obj.get("value")

    jobs = pipeline_run.get("jobs") or []
    if not isinstance(jobs, list):
        jobs = []

    job_stats: List[Dict[str, Any]] = []
    all_jobs: List[Dict[str, Any]] = []

    for job in jobs:
        if not isinstance(job, dict):
            continue

        job_id = job.get("jobId") or job.get("jobID") or job.get("id")
        job_run_id = job.get("jobRunId") or job.get("jobRunID")
        job_name = job.get("jobName")
        if not job_name:
            name_i18n = job.get("jobNameI18n") or {}
            if isinstance(name_i18n, dict):
                texts = name_i18n.get("texts") or {}
                if isinstance(texts, dict):
                    job_name = name_i18n.get("value") or texts.get("zh") or texts.get("en")
                else:
                    job_name = name_i18n.get("value")

        job_atom = job.get("jobAtom") or {}
        if not isinstance(job_atom, dict):
            job_atom = {}

        unique_id = job_atom.get("uniqueId")

        fail_reason = job.get("failReason") or {}
        if not isinstance(fail_reason, dict):
            fail_reason = {}
        fail_message = fail_reason.get("message")

        output_obj = job_atom.get("output")
        output_data: Optional[Dict[str, Any]] = None
        if isinstance(output_obj, dict):
            output_data = output_obj
        elif isinstance(output_obj, str) and output_obj.strip():
            try:
                parsed = json.loads(output_obj)
            except Exception:
                parsed = None
            if isinstance(parsed, dict):
                output_data = parsed

        if unique_id == "test_framework_trigger" and not output_data and isinstance(fail_message, str) and fail_message.strip():
            try:
                parsed = json.loads(fail_message)
            except Exception:
                parsed = None
            if isinstance(parsed, dict):
                output_data = parsed

        if unique_id == "test_framework_trigger" and not output_data:
            jr_output = fetch_job_run_output(str(job_run_id) if job_run_id is not None else None, run_id)
            if isinstance(jr_output, dict):
                output_data = jr_output

        all_jobs.append(
            {
                "jobName": job_name,
                "jobId": job_id,
                "jobRunId": job_run_id,
                "uniqueId": unique_id,
                "has_test_stats": bool(output_data),
            }
        )

        if unique_id != "test_framework_trigger":
            continue
        if not output_data or not isinstance(output_data, dict):
            continue

        case_num = safe_int(output_data.get("case_num"))
        failed_case = safe_int(output_data.get("failed_case"))
        succeed_case = safe_int(output_data.get("succeed_case"))
        skipped_case = safe_int(output_data.get("skipped_case"))
        state = output_data.get("state")

        if case_num is None:
            continue

        if failed_case is None:
            failed_case = 0
        if succeed_case is None:
            succeed_case = 0
        if skipped_case is None:
            skipped_case = 0

        job_stats.append(
            {
                "jobName": job_name or "",
                "jobId": job_id,
                "jobRunId": job_run_id,
                "state": state or "",
                "case_num": case_num,
                "failed_case": failed_case,
                "succeed_case": succeed_case,
                "skipped_case": skipped_case,
            }
        )

    total_case_num = sum(j.get("case_num", 0) for j in job_stats)
    total_failed = sum(j.get("failed_case", 0) for j in job_stats)
    total_succeed = sum(j.get("succeed_case", 0) for j in job_stats)
    total_skipped = sum(j.get("skipped_case", 0) for j in job_stats)
    total_pass_rate = round((total_succeed / total_case_num) * 100, 2) if total_case_num else 0.0

    for j in job_stats:
        case_num = j.get("case_num", 0)
        failed_case = j.get("failed_case", 0)
        j["job_fail_rate"] = round((failed_case / case_num) * 100, 2) if case_num else 0.0
        j["fail_share_pct"] = round((failed_case / total_failed) * 100, 2) if total_failed else 0.0

    job_stats_sorted = sorted(job_stats, key=lambda x: x.get("failed_case", 0), reverse=True)
    top10 = job_stats_sorted[:10]

    stats = {
        "pipeline_name": pipeline_name,
        "pipeline_id": pipeline_id,
        "run_id": run_id,
        "run_seq": run_seq,
        "total_case_num": total_case_num,
        "total_failed": total_failed,
        "total_succeed": total_succeed,
        "total_skipped": total_skipped,
        "total_pass_rate": total_pass_rate,
        "job_stats": job_stats_sorted,
        "top10": top10,
        "all_jobs": all_jobs,
    }
    summary = {
        "pipeline_name": pipeline_name,
        "run_seq": run_seq,
        "total_case_num": total_case_num,
        "total_failed": total_failed,
        "total_succeed": total_succeed,
        "total_skipped": total_skipped,
        "total_pass_rate": total_pass_rate,
        "jobs_count": len(job_stats_sorted),
        "all_jobs_count": len(all_jobs),
    }
    overview_row = {
        "运行编号": run_seq,
        "流水线ID": pipeline_id,
        "runID": run_id,
        "总用例数": total_case_num,
        "总失败": total_failed,
        "总成功": total_succeed,
        "总跳过": total_skipped,
        "总通过率": f"{total_pass_rate:.2f}",
    }

    return {
        "pipeline_id": pipeline_id,
        "pipeline_name": pipeline_name or "",
        "run_id": run_id,
        "run_seq": str(run_seq or ""),
        "overview_row": overview_row,
        "job_rows": [_job_row_to_csv_dict(row) for row in job_stats_sorted],
        "top10_rows": [_job_row_to_csv_dict(row) for row in top10],
        "stats": stats,
        "summary": summary,
    }


def write_report_files(report_data: Dict[str, Any], output_dir: str = ".", include_stats: bool = DEFAULT_INCLUDE_STATS) -> None:
    pipeline_id = str(report_data["pipeline_id"])
    run_id = str(report_data["run_id"])
    output_paths = build_output_paths(
        pipeline_id,
        run_id,
        output_dir=output_dir,
        include_stats=include_stats,
    )
    overview_csv = output_paths["overview_csv"]
    jobs_csv = output_paths["jobs_csv"]
    top10_csv = output_paths["top10_csv"]
    stats_path = output_paths.get("stats_path")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with open(overview_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(OVERVIEW_HEADER)
        overview = report_data["overview_row"]
        writer.writerow([overview.get(col, "") for col in OVERVIEW_HEADER])

    def write_jobs(path: str, rows: List[Dict[str, Any]]) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(JOBS_HEADER)
            for row in rows:
                writer.writerow([row.get(col, "") for col in JOBS_HEADER])

    write_jobs(jobs_csv, report_data["job_rows"])
    write_jobs(top10_csv, report_data["top10_rows"])

    if stats_path:
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(report_data["stats"], f, ensure_ascii=False, indent=2)


def run_report(
    pipeline_id: str,
    run_id: str,
    dry_run: bool = False,
    output_dir: str = ".",
    include_stats: bool = DEFAULT_INCLUDE_STATS,
    write_files: bool = True,
) -> Dict[str, Any]:
    """主流程：拉取流水线运行信息并生成 CSV / JSON 报告。"""
    run_url = f"{BASE_URL}/api/v1/pipelines/runs/{run_id}"
    output_paths = build_output_paths(
        pipeline_id,
        run_id,
        output_dir=output_dir,
        include_stats=include_stats,
    )
    overview_csv = output_paths["overview_csv"]
    jobs_csv = output_paths["jobs_csv"]
    top10_csv = output_paths["top10_csv"]
    stats_path = output_paths.get("stats_path")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if dry_run:
        print("[DRY-RUN] 不会发起网络请求，只展示将要执行的操作。")
        print(f"[DRY-RUN] 将请求流水线运行详情: {run_url}")
        print(f"[DRY-RUN] 概览 CSV: {overview_csv}")
        print(f"[DRY-RUN] Jobs CSV: {jobs_csv}")
        print(f"[DRY-RUN] TOP10 CSV: {top10_csv}")
        if stats_path:
            print(f"[DRY-RUN] 统计 JSON: {stats_path}")
        return

    try:
        run_data = fetch_json(run_url)
    except Exception as e:
        print(f"ERROR: failed to fetch pipeline run: {e}")
        return

    report_data = build_report_data(pipeline_id, run_id, run_data)
    if write_files:
        write_report_files(report_data, output_dir=output_dir, include_stats=include_stats)

    print("OK")
    print(json.dumps(report_data["summary"], ensure_ascii=False))
    return report_data


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "根据 Bits 流水线 ID 和 Run ID 汇总 test_framework_trigger Job 的用例统计，"
            "并生成 Overview / Jobs 全量 / TOP10 CSV 及统计 JSON。"
        )
    )
    parser.add_argument(
        "pipeline_id",
        nargs="?",
        help="流水线 ID (pipelineId)，来自 Bits 流水线详情页 URL。",
    )
    parser.add_argument(
        "run_id",
        nargs="?",
        help="流水线运行 ID (runId)，来自 Bits 流水线运行记录。",
    )
    parser.add_argument(
        "--pipeline-id",
        dest="pipeline_id_opt",
        help="流水线 ID（与位置参数 pipeline_id 二选一）。",
    )
    parser.add_argument(
        "--run-id",
        dest="run_id_opt",
        help="运行 ID（与位置参数 run_id 二选一）。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅打印将要访问的接口和输出文件名，不发起网络请求。",
    )

    args = parser.parse_args()

    if args.pipeline_id and args.pipeline_id_opt and args.pipeline_id != args.pipeline_id_opt:
        parser.error("位置参数 pipeline_id 与 --pipeline-id 不一致。")
    if args.run_id and args.run_id_opt and args.run_id != args.run_id_opt:
        parser.error("位置参数 run_id 与 --run-id 不一致。")

    pipeline_id = args.pipeline_id or args.pipeline_id_opt
    run_id = args.run_id or args.run_id_opt

    if not pipeline_id or not run_id:
        parser.error("必须通过位置参数或 --pipeline-id/--run-id 提供流水线ID和runID。")

    run_report(pipeline_id, run_id, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
