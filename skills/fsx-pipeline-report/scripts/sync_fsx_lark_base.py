#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


SUMMARY_FIELDS = [
    {"name": "流水线标题", "type": "text"},
    {"name": "流水线 ID", "type": "text"},
    {"name": "日期", "type": "text"},
    {"name": "最近运行 ID", "type": "text"},
    {"name": "运行状态", "type": "text"},
    {"name": "失败步骤数", "type": "number"},
    {"name": "阻塞步骤数", "type": "number"},
    {"name": "首个失败步骤", "type": "text"},
    {"name": "流水线链接", "type": "text"},
    {"name": "是否需要关注", "type": "text"},
]

DETAIL_FIELDS = [
    {"name": "日期", "type": "text"},
    {"name": "流水线标题", "type": "text"},
    {"name": "流水线 ID", "type": "text"},
    {"name": "运行 ID", "type": "text"},
    {"name": "运行状态", "type": "text"},
    {"name": "失败步骤", "type": "text"},
    {"name": "失败状态", "type": "text"},
    {"name": "任务链接", "type": "text"},
]


def run_json(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)
    return json.loads(proc.stdout)


def ensure_table(base_token: str, table_name: str, as_identity: str) -> str:
    tables = run_json(
        [
            "lark-cli",
            "base",
            "+table-list",
            "--as",
            as_identity,
            "--base-token",
            base_token,
        ]
    )["data"]["items"]
    for table in tables:
        if table["table_name"] == table_name:
            return table["table_id"]
    created = run_json(
        [
            "lark-cli",
            "base",
            "+table-create",
            "--as",
            as_identity,
            "--base-token",
            base_token,
            "--name",
            table_name,
        ]
    )
    return created["data"]["table"]["id"]


def ensure_fields(base_token: str, table_id: str, fields: list[dict], as_identity: str) -> None:
    existing = run_json(
        [
            "lark-cli",
            "base",
            "+field-list",
            "--as",
            as_identity,
            "--base-token",
            base_token,
            "--table-id",
            table_id,
        ]
    )["data"]["items"]
    existing_names = {item["field_name"] for item in existing}
    for field in fields:
        if field["name"] in existing_names:
            continue
        body = json.dumps(field, ensure_ascii=False)
        for attempt in range(1, 9):
            proc = subprocess.run(
                [
                    "lark-cli",
                    "base",
                    "+field-create",
                    "--as",
                    as_identity,
                    "--base-token",
                    base_token,
                    "--table-id",
                    table_id,
                    "--json",
                    body,
                ],
                text=True,
                capture_output=True,
            )
            if proc.returncode == 0:
                time.sleep(2)
                break
            combined = (proc.stdout or "") + (proc.stderr or "")
            if "800004135" in combined or "limited" in combined:
                time.sleep(min(3 * attempt, 15))
                continue
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            raise SystemExit(proc.returncode)
        else:
            raise SystemExit(f"failed to create field {field['name']}")


def delete_default_table(base_token: str, as_identity: str) -> None:
    tables = run_json(
        [
            "lark-cli",
            "base",
            "+table-list",
            "--as",
            as_identity,
            "--base-token",
            base_token,
        ]
    )["data"]["items"]
    for table in tables:
        if table["table_name"] == "数据表":
            run_json(
                [
                    "lark-cli",
                    "base",
                    "+table-delete",
                    "--as",
                    as_identity,
                    "--base-token",
                    base_token,
                    "--table-id",
                    table["table_id"],
                    "--yes",
                ]
            )


def clear_table(base_token: str, table_name: str, as_identity: str) -> None:
    while True:
        listed = run_json(
            [
                "lark-cli",
                "base",
                "+record-list",
                "--as",
                as_identity,
                "--base-token",
                base_token,
                "--table-id",
                table_name,
                "--limit",
                "200",
            ]
        )["data"]["record_id_list"]
        if not listed:
            return
        for record_id in listed:
            run_json(
                [
                    "lark-cli",
                    "base",
                    "+record-delete",
                    "--as",
                    as_identity,
                    "--base-token",
                    base_token,
                    "--table-id",
                    table_name,
                    "--record-id",
                    record_id,
                    "--yes",
                ]
            )


def upsert_rows(base_token: str, table_name: str, rows: list[dict], field_names: list[str], as_identity: str) -> None:
    for row in rows:
        payload = {key: row.get(key) for key in field_names}
        run_json(
            [
                "lark-cli",
                "base",
                "+record-upsert",
                "--as",
                as_identity,
                "--base-token",
                base_token,
                "--table-id",
                table_name,
                "--json",
                json.dumps(payload, ensure_ascii=False),
            ]
        )
        time.sleep(0.1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync FSX report artifacts to Feishu Base.")
    parser.add_argument("--base-token", required=True, help="Existing Feishu Base token.")
    parser.add_argument(
        "--artifact-dir",
        default="artifacts",
        help="Directory containing summary/detail JSON generated by fetch_fsx_pipeline_report.py",
    )
    parser.add_argument(
        "--as",
        dest="as_identity",
        choices=["user", "bot"],
        default="user",
        help="Identity to use for lark-cli operations. Default: user",
    )
    args = parser.parse_args()

    artifact_dir = Path(args.artifact_dir).resolve()
    summary_rows = json.loads((artifact_dir / "fsx_pipeline_report_summary.json").read_text())
    detail_rows = json.loads((artifact_dir / "fsx_pipeline_report_details.json").read_text())

    summary_table_id = ensure_table(args.base_token, "汇总信息", args.as_identity)
    detail_table_id = ensure_table(args.base_token, "失败步骤明细", args.as_identity)
    ensure_fields(args.base_token, summary_table_id, SUMMARY_FIELDS, args.as_identity)
    ensure_fields(args.base_token, detail_table_id, DETAIL_FIELDS, args.as_identity)
    delete_default_table(args.base_token, args.as_identity)
    clear_table(args.base_token, "汇总信息", args.as_identity)
    clear_table(args.base_token, "失败步骤明细", args.as_identity)
    upsert_rows(
        args.base_token,
        "汇总信息",
        summary_rows,
        [
            "流水线标题",
            "流水线 ID",
            "日期",
            "最近运行 ID",
            "运行状态",
            "失败步骤数",
            "阻塞步骤数",
            "首个失败步骤",
            "流水线链接",
            "是否需要关注",
        ],
        args.as_identity,
    )
    upsert_rows(
        args.base_token,
        "失败步骤明细",
        detail_rows,
        [
            "日期",
            "流水线标题",
            "流水线 ID",
            "运行 ID",
            "运行状态",
            "失败步骤",
            "失败状态",
            "任务链接",
        ],
        args.as_identity,
    )
    print(
        json.dumps(
            {
                "base_token": args.base_token,
                "summary_count": len(summary_rows),
                "detail_count": len(detail_rows),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
