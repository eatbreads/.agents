"""固定五条流水线顺序看护脚本。"""

import argparse
import csv
from pathlib import Path
from typing import Any, Dict, List

import watch_single_pipeline
from config_loader import get_fixed_pipeline_ids, load_local_config


CONFIG = load_local_config()
PIPELINE_IDS = get_fixed_pipeline_ids(CONFIG)


def run_watch_for_pipeline(pipeline_id: str, cloud_jwt: str, output_dir: str) -> Dict[str, Any]:
    return watch_single_pipeline.run_watch_for_pipeline(
        pipeline_id,
        cloud_jwt,
        output_dir=output_dir,
        write_files=False,
    )


def write_aggregate_csvs(report_rows: List[Dict[str, Any]], output_dir: str) -> None:
    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)

    overview_header = [
        "pipeline_name",
        "总用例数",
        "总失败",
        "总成功",
        "总跳过",
        "总通过率",
        "run_seq",
        "pipeline_id",
        "run_id",
    ]
    jobs_header = [
        "pipeline_name",
        *watch_single_pipeline.bits_pipeline_report.JOBS_HEADER,
        "run_seq",
        "pipeline_id",
        "run_id",
    ]

    with open(base / "overview_all.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(overview_header)
        for row in report_rows:
            overview = row["overview_row"]
            writer.writerow(
                [
                    row.get("pipeline_name", ""),
                    overview.get("总用例数", ""),
                    overview.get("总失败", ""),
                    overview.get("总成功", ""),
                    overview.get("总跳过", ""),
                    overview.get("总通过率", ""),
                    row.get("run_seq", ""),
                    row.get("pipeline_id", ""),
                    row.get("run_id", ""),
                ]
            )

    def write_job_file(filename: str, key: str, failed_only: bool = False) -> None:
        with open(base / filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(jobs_header)
            for row in report_rows:
                for job in row.get(key, []):
                    if failed_only:
                        try:
                            failed_case = int(job.get("failed_case", 0))
                        except (TypeError, ValueError):
                            failed_case = 0
                        if failed_case <= 0:
                            continue
                    writer.writerow(
                        [
                            row.get("pipeline_name", ""),
                            *[job.get(col, "") for col in watch_single_pipeline.bits_pipeline_report.JOBS_HEADER],
                            row.get("run_seq", ""),
                            row.get("pipeline_id", ""),
                            row.get("run_id", ""),
                        ]
                    )

    write_job_file("jobs_all.csv", "job_rows")
    write_job_file("top10_jobs_all.csv", "top10_rows", failed_only=True)


def run_all_watches(output_dir: str = watch_single_pipeline.DEFAULT_OUTPUT_DIR) -> Dict[str, Any]:
    cloud_jwt = watch_single_pipeline.exchange_secret_for_jwt(watch_single_pipeline.BITS_SA_SECRET)

    results: List[Dict[str, Any]] = []
    for pipeline_id in PIPELINE_IDS:
        try:
            result = run_watch_for_pipeline(pipeline_id, cloud_jwt, output_dir)
        except Exception as exc:
            result = {
                "pipeline_id": pipeline_id,
                "status": "ERROR",
                "error": str(exc),
            }
            print(f"ERROR pipeline={pipeline_id} error={exc}")
        else:
            if result["status"] == "OK":
                print(f"OK pipeline={pipeline_id} run_id={result.get('run_id')}")
        results.append(result)

    ok_count = sum(1 for item in results if item.get("status") == "OK")
    skip_count = sum(1 for item in results if item.get("status") == "SKIP")
    error_count = sum(1 for item in results if item.get("status") == "ERROR")
    report_rows = [item["report_data"] for item in results if item.get("status") == "OK" and item.get("report_data")]

    write_aggregate_csvs(report_rows, output_dir=output_dir)

    print(
        f"SUMMARY total={len(results)} ok={ok_count} skip={skip_count} error={error_count}"
    )

    return {
        "results": results,
        "ok_count": ok_count,
        "skip_count": skip_count,
        "error_count": error_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="顺序看护五条固定 FSX pipeline，并为已结束的最新 run 生成产物。")
    parser.add_argument(
        "--output-dir",
        default=watch_single_pipeline.DEFAULT_OUTPUT_DIR,
        help="产物输出目录，默认写到当前 scripts 目录。",
    )
    args = parser.parse_args()
    run_all_watches(output_dir=args.output_dir)


if __name__ == "__main__":
    main()
