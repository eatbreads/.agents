"""Fetch duty oncall users and resolve Feishu mention tags.

This script is intentionally standalone so daily_watch_publish.py can call it
later without coupling the pipeline report flow to the duty API details.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_DUTY_NAME = "fuse-tob-oncall"
DEFAULT_TOKEN_FILE = Path("/data00/home/sunjunhao.39/.agents/secret")
DEFAULT_BASE_URL = "https://paas-gw.byted.org/api/v1/duty_ssr"


class DutyMentionError(RuntimeError):
    """Raised when duty or Feishu user resolution fails."""


def _load_token(token_file: Path) -> str:
    if not token_file.exists():
        raise DutyMentionError(f"Token file not found: {token_file}")
    token = token_file.read_text(encoding="utf-8").strip()
    if not token:
        raise DutyMentionError(f"Token file is empty: {token_file}")
    return token


def _read_json_response(req: urllib.request.Request) -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise DutyMentionError(f"HTTP {exc.code} from duty API: {body[:300]}") from exc
    except urllib.error.URLError as exc:
        raise DutyMentionError(f"Failed to call duty API: {exc}") from exc

    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise DutyMentionError(f"Duty API returned non-JSON body: {body[:300]}") from exc
    if not isinstance(data, dict):
        raise DutyMentionError("Duty API returned JSON that is not an object")
    return data


def fetch_duty(duty_name: str, token: str, base_url: str = DEFAULT_BASE_URL) -> Dict[str, Any]:
    encoded_name = urllib.parse.quote(duty_name.strip(), safe="")
    url = f"{base_url.rstrip('/')}/duty/api/open/duty/{encoded_name}/"
    req = urllib.request.Request(
        url,
        method="GET",
        headers={
            "X-BC-Region-Id": "bytedance",
            "X-Resource-Account": "public",
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    return _read_json_response(req)


def _run_lark_search(username: str) -> Dict[str, Any]:
    completed = subprocess.run(
        [
            "lark-cli",
            "contact",
            "+search-user",
            "--query",
            username,
            "--page-size",
            "10",
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise DutyMentionError(
            f"lark-cli contact search failed for {username}: "
            f"{(completed.stderr or completed.stdout).strip()}"
        )

    text = completed.stdout.strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DutyMentionError(f"lark-cli returned non-JSON for {username}: {text[:300]}") from exc
    if not isinstance(payload, dict):
        raise DutyMentionError(f"lark-cli returned unexpected payload for {username}")
    return payload


def _pick_user(username: str, users: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not users:
        raise DutyMentionError(f"No Feishu user found for duty username: {username}")
    if len(users) == 1:
        return users[0]

    normalized = username.lower()
    for user in users:
        fields = [
            str(user.get("name") or ""),
            str(user.get("email") or ""),
            str(user.get("employee_no") or ""),
            str(user.get("enterprise_email") or ""),
        ]
        if any(normalized in value.lower() for value in fields):
            return user
    return users[0]


def resolve_feishu_user(username: str) -> Dict[str, str]:
    payload = _run_lark_search(username)
    data = payload.get("data")
    users = data.get("users") if isinstance(data, dict) else None
    if not isinstance(users, list):
        raise DutyMentionError(f"Unexpected lark-cli search payload for {username}")

    user = _pick_user(username, [item for item in users if isinstance(item, dict)])
    open_id = str(user.get("open_id") or "")
    name = str(user.get("name") or username)
    if not open_id:
        raise DutyMentionError(f"Feishu user for {username} has no open_id")

    return {
        "username": username,
        "name": name,
        "open_id": open_id,
        "mention": f'<at user_id="{open_id}">{name}</at>',
    }


def _unique_preserve_order(values: Iterable[str]) -> List[str]:
    result: List[str] = []
    seen = set()
    for value in values:
        item = str(value or "").strip()
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def build_mentions(duty: Dict[str, Any]) -> Dict[str, Any]:
    oncall = duty.get("oncall")
    if not isinstance(oncall, dict):
        raise DutyMentionError("Duty API response has no oncall object")

    primary_username = str(oncall.get("primary_user") or oncall.get("primary") or "").strip()
    backup_usernames = oncall.get("backup_users") or oncall.get("backups") or []
    if not isinstance(backup_usernames, list):
        backup_usernames = []

    if not primary_username:
        raise DutyMentionError("Duty API response has no primary oncall user")

    primary = resolve_feishu_user(primary_username)
    backups = [resolve_feishu_user(username) for username in _unique_preserve_order(backup_usernames)]
    all_mentions = [primary, *backups]

    return {
        "duty_id": duty.get("id"),
        "duty_name": duty.get("display_name") or duty.get("name"),
        "status": duty.get("status"),
        "primary": primary,
        "backups": backups,
        "mention_text": " ".join(item["mention"] for item in all_mentions),
        "usernames": [item["username"] for item in all_mentions],
        "open_ids": [item["open_id"] for item in all_mentions],
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch duty oncall users and resolve Feishu mention tags.")
    parser.add_argument("--duty-name", default=DEFAULT_DUTY_NAME, help=f"Duty name. Default: {DEFAULT_DUTY_NAME}")
    parser.add_argument("--token-file", default=str(DEFAULT_TOKEN_FILE), help="Service account token file.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Duty API base URL.")
    parser.add_argument("--output", help="Optional JSON output path. Stdout is always printed.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    token = _load_token(Path(args.token_file))
    duty = fetch_duty(args.duty_name, token, args.base_url)
    result = build_mentions(duty)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DutyMentionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
