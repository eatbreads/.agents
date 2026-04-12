"""固定单条流水线看护脚本。

流程：
1. 使用写死的服务账号密钥换取 cloud JWT
2. 调 GetPipeline 获取最新 run_id
3. 调 GetPipelineRun 判断最新 run 是否已结束
4. 已结束则复用 bits_pipeline_report.run_report 生成报告产物
5. 未结束则打印 SKIP，不生成新产物
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import bits_pipeline_report
from config_loader import load_local_config, require_config


CONFIG = load_local_config()
PIPELINE_ID = str(CONFIG["single_pipeline_id"])
BITS_SA_SECRET = require_config(CONFIG, "bits_sa_secret")
USERNAME = require_config(CONFIG, "username")
DOMAIN = str(CONFIG["domain"])
DEFAULT_OUTPUT_DIR = str(SCRIPT_DIR)
CLOUD_JWT_URL = "https://cloud.bytedance.net/auth/api/v1/jwt"
GET_PIPELINE_URL_TEMPLATE = f"{bits_pipeline_report.BASE_URL}/api/v1/pipelines/open/{{pipeline_id}}"
GET_PIPELINE_RUN_URL_TEMPLATE = f"{bits_pipeline_report.BASE_URL}/api/v1/pipelines/open/runs/{{run_id}}"


def exchange_secret_for_jwt(secret: str) -> str:
    req = urllib.request.Request(
        CLOUD_JWT_URL,
        headers={"Authorization": f"Bearer {secret}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        jwt = resp.headers.get("X-Jwt-Token")
        if not jwt:
            raise RuntimeError("JWT exchange succeeded but X-Jwt-Token header is missing")
        return jwt


def fetch_openapi_json(url: str, cloud_jwt: str) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "accept": "application/json, text/plain, */*",
            "user-agent": "Aime-Agent/1.0",
            "x-jwt-token": cloud_jwt,
            "username": USERNAME,
            "domain": DOMAIN,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_watch_for_pipeline(
    pipeline_id: str,
    cloud_jwt: str,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    write_files: bool = True,
) -> Dict[str, Any]:
    pipeline_payload = fetch_openapi_json(GET_PIPELINE_URL_TEMPLATE.format(pipeline_id=pipeline_id), cloud_jwt)
    last_run_id = bits_pipeline_report.extract_last_run_id(pipeline_payload)
    if not last_run_id:
        raise RuntimeError(f"GetPipeline succeeded but no last_run_id was found for pipeline {pipeline_id}")

    run_payload = fetch_openapi_json(
        GET_PIPELINE_RUN_URL_TEMPLATE.format(run_id=last_run_id),
        cloud_jwt,
    )
    pipeline_run = run_payload.get("pipeline_run") if isinstance(run_payload, dict) else None
    if not isinstance(pipeline_run, dict):
        raise RuntimeError(f"GetPipelineRun returned unexpected payload for run {last_run_id}")

    run_status = (
        pipeline_run.get("run_status")
        or pipeline_run.get("runStatus")
        or pipeline_run.get("status")
        or pipeline_run.get("state")
    )
    if not bits_pipeline_report.is_finished_run_status(run_status):
        result = {
            "pipeline_id": pipeline_id,
            "run_id": last_run_id,
            "status": "SKIP",
            "run_status": run_status,
            "message": (
                f"SKIP pipeline={pipeline_id} latest_run_id={last_run_id} "
                f"status={run_status!r} because the latest run is not finished"
            ),
        }
        print(result["message"])
        return result

    os.environ["AIME_USER_CLOUD_JWT"] = cloud_jwt
    report_data = bits_pipeline_report.run_report(
        pipeline_id,
        last_run_id,
        dry_run=False,
        output_dir=output_dir,
        include_stats=bits_pipeline_report.DEFAULT_INCLUDE_STATS,
        write_files=write_files,
    )
    return {
        "pipeline_id": pipeline_id,
        "run_id": last_run_id,
        "status": "OK",
        "run_status": run_status,
        "report_data": report_data,
    }


def run_watch(output_dir: str = DEFAULT_OUTPUT_DIR) -> Dict[str, Any]:
    cloud_jwt = exchange_secret_for_jwt(BITS_SA_SECRET)
    return run_watch_for_pipeline(PIPELINE_ID, cloud_jwt, output_dir=output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="监控固定单条 pipeline 的最新已结束 run，并生成统计产物。")
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="产物输出目录，默认写到当前 scripts 目录。",
    )
    args = parser.parse_args()

    try:
        run_watch(output_dir=args.output_dir)
    except urllib.error.HTTPError as exc:
        print(f"ERROR: HTTP {exc.code} while watching pipeline {PIPELINE_ID}: {exc}")
        raise SystemExit(1) from exc
    except Exception as exc:
        print(f"ERROR: failed to watch pipeline {PIPELINE_ID}: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
