#!/usr/bin/env python3

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import requests


WATCHED_PIPELINES = [
    {"pipeline_id": "1073215225602", "title": "FSX for vePFS/TOS 北京全量流水线"},
    {"pipeline_id": "656544971778", "title": "FSX for NAS/EFS 廊坊全量流水线"},
    {"pipeline_id": "410812259074", "title": "FSProxy for vePFS 全量流水线"},
    {"pipeline_id": "1119183026434", "title": "VePFS 接入点 mgr 故障流水线"},
    {"pipeline_id": "865297825538", "title": "FSProxy for EFS&NAS 全量流水线"},
]

RUN_STATUS_MAP = {
    3: "运行中",
    8: "已结束",
    9: "成功",
}

JOB_STATUS_MAP = {
    4: "阻塞",
    6: "失败",
    9: "成功",
    14: "成功",
}


def load_secret(repo_root: Path) -> str:
    secret = os.environ.get("BITS_SA_SECRET")
    if secret:
        return secret.strip()
    secret_file = repo_root / ".agents" / "secret"
    if secret_file.exists():
        return secret_file.read_text().strip()
    raise SystemExit("missing BITS_SA_SECRET and .agents/secret")


def get_cloud_jwt(secret: str) -> str:
    resp = requests.get(
        "https://cloud.bytedance.net/auth/api/v1/jwt",
        headers={"Authorization": f"Bearer {secret}"},
        timeout=20,
    )
    resp.raise_for_status()
    cloud_jwt = resp.headers.get("X-Jwt-Token")
    if not cloud_jwt:
        raise SystemExit("missing X-Jwt-Token from cloud JWT exchange")
    return cloud_jwt


def bits_get(headers: dict, path: str, params=None) -> dict:
    resp = requests.get(
        "https://bits.bytedance.net" + path,
        headers=headers,
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def fmt_date(value: str) -> str:
    if not value:
        return ""
    return value[:10]


def write_markdown(output_path: Path, summary_rows: list, detail_rows: list) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# FSX 需看护流水线运营报表",
        "",
        f"- 生成时间：{now}",
        "- 范围：FSX 值班需看护的 5 条流水线",
        "- 口径：先聚焦“哪天哪条流水线在哪个步骤失败”，暂不展开失败原因分析",
        "",
        "## 汇总信息",
        "",
        "| 日期 | 流水线标题 | 流水线 ID | 最近运行 ID | 运行状态 | 失败步骤数 | 阻塞步骤数 | 首个失败步骤 | 是否需要关注 |",
        "|---|---|---:|---:|---|---:|---:|---|---|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['日期']} | {row['流水线标题']} | {row['流水线 ID']} | "
            f"{row['最近运行 ID']} | {row['运行状态']} | {row['失败步骤数']} | "
            f"{row['阻塞步骤数']} | {row['首个失败步骤']} | {row['是否需要关注']} |"
        )

    lines.extend(
        [
            "",
            "## 失败步骤明细",
            "",
            "| 明细编号 | 日期 | 流水线标题 | 流水线 ID | 运行 ID | 运行状态 | 失败步骤 | 失败状态 | 任务链接 |",
            "|---|---|---|---:|---:|---|---|---|---|",
        ]
    )
    for row in detail_rows:
        lines.append(
            f"| {row['明细编号']} | {row['日期']} | {row['流水线标题']} | {row['流水线 ID']} | "
            f"{row['运行 ID']} | {row['运行状态']} | {row['失败步骤']} | {row['失败状态']} | "
            f"{row['任务链接']} |"
        )
    output_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch FSX watched pipeline report from Bits.")
    parser.add_argument(
        "--repo-root",
        default=str(Path.cwd()),
        help="Workspace root. Used to resolve .agents/secret and artifacts/.",
    )
    parser.add_argument(
        "--output-dir",
        default="/tmp/fsx-pipeline-report",
        help="Directory to store raw JSON, summary JSON, detail JSON, and markdown. Default: /tmp/fsx-pipeline-report",
    )
    parser.add_argument(
        "--username",
        default="sunjunhao.39",
        help="Bits username header value.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    secret = load_secret(repo_root)
    cloud_jwt = get_cloud_jwt(secret)
    headers = {
        "x-jwt-token": cloud_jwt,
        "username": args.username,
        "domain": "pipelines_open;v1",
        "Content-Type": "application/json",
    }

    raw_rows = []
    summary_rows = []
    detail_rows = []

    for pipeline in WATCHED_PIPELINES:
        pipeline_id = pipeline["pipeline_id"]
        meta = bits_get(headers, f"/api/v1/pipelines/open/{pipeline_id}")
        runs = bits_get(
            headers,
            "/api/v1/pipelines/open/runs",
            params={
                "pipeline_id": pipeline_id,
                "page_size": 1,
                "page_num": 1,
                "without_pipeline": "false",
            },
        )
        raw_rows.append({"pipeline": pipeline, "meta": meta, "runs": runs})

        latest = (runs.get("pipeline_runs") or [None])[0] or {}
        run_id = str(latest.get("run_id") or "")
        run_status = RUN_STATUS_MAP.get(
            latest.get("run_status"),
            str(latest.get("run_status") or ""),
        )
        run_date = fmt_date(latest.get("started_at") or latest.get("created_at") or "")
        run_link = latest.get("pipeline_run_url") or (
            f"https://bits.bytedance.net/devops/4082708738/pipeline/detail/{pipeline_id}"
            f"?pipelineID={pipeline_id}&activeTab=0&devops_space_type=server_fe"
        )

        failed_rows = []
        blocked_rows = []
        for job in latest.get("jobs") or []:
            job_state = JOB_STATUS_MAP.get(
                job.get("job_status"),
                str(job.get("job_status") or ""),
            )
            if job_state not in ("失败", "阻塞"):
                continue
            row = {
                "明细编号": "",
                "日期": run_date,
                "流水线标题": pipeline["title"],
                "流水线 ID": pipeline_id,
                "运行 ID": run_id,
                "运行状态": run_status,
                "失败步骤": job.get("job_name") or "",
                "失败状态": job_state,
                "Job Run ID": str(job.get("job_run_id") or ""),
                "任务链接": run_link,
            }
            if job_state == "失败":
                failed_rows.append(row)
            else:
                blocked_rows.append(row)

        summary_rows.append(
            {
                "日期": run_date,
                "流水线标题": pipeline["title"],
                "流水线 ID": pipeline_id,
                "最近运行 ID": run_id,
                "运行状态": run_status,
                "失败步骤数": len(failed_rows),
                "阻塞步骤数": len(blocked_rows),
                "首个失败步骤": failed_rows[0]["失败步骤"] if failed_rows else "",
                "流水线链接": run_link,
                "是否需要关注": "是" if failed_rows or blocked_rows or run_status == "运行中" else "否",
            }
        )
        detail_rows.extend(failed_rows + blocked_rows)

    for idx, row in enumerate(detail_rows, start=1):
        row["明细编号"] = f"NO.{idx:03d}"

    (output_dir / "fsx_pipeline_runs_raw.json").write_text(
        json.dumps(raw_rows, ensure_ascii=False, indent=2)
    )
    (output_dir / "fsx_pipeline_report_summary.json").write_text(
        json.dumps(summary_rows, ensure_ascii=False, indent=2)
    )
    (output_dir / "fsx_pipeline_report_details.json").write_text(
        json.dumps(detail_rows, ensure_ascii=False, indent=2)
    )
    write_markdown(output_dir / "fsx_pipeline_report.md", summary_rows, detail_rows)

    print(
        json.dumps(
            {
                "summary_count": len(summary_rows),
                "detail_count": len(detail_rows),
                "output_dir": str(output_dir),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
