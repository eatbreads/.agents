"""Load local runtime config for FSX pipeline watch scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_CONFIG_PATH = SCRIPT_DIR / "local_config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "domain": "pipelines_open;v1",
    "single_pipeline_id": "1073215225602",
    "fixed_pipeline_ids": [
        "1073215225602",
        "656544971778",
        "410812259074",
        "1119183026434",
        "865297825538",
    ],
    "chat_ids": ["oc_fb9b3bb366d930e54f0471362c3b9e8e"],
    "spreadsheet_title_prefix": "FSX 核心流水线每日看护",
    "sheets_identity": "user",
    "im_identity": "bot",
    "viewer_department_ids": [],
}


def load_local_config(path: Path = LOCAL_CONFIG_PATH) -> Dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            config.update({key: value for key, value in data.items() if value not in (None, "")})
    return config


def require_config(config: Dict[str, Any], key: str) -> str:
    value = config.get(key)
    if value in (None, ""):
        raise RuntimeError(
            f"Missing required config {key!r}. "
            f"Please create {LOCAL_CONFIG_PATH} based on local_config.example.json."
        )
    return str(value)


def get_fixed_pipeline_ids(config: Dict[str, Any]) -> List[str]:
    value = config.get("fixed_pipeline_ids")
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return list(DEFAULT_CONFIG["fixed_pipeline_ids"])


def get_viewer_department_ids(config: Dict[str, Any]) -> List[str]:
    value = config.get("viewer_department_ids")
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return []


def get_chat_ids(config: Dict[str, Any]) -> List[str]:
    value = config.get("chat_ids")
    if isinstance(value, list):
        chat_ids = [str(item) for item in value if str(item).strip()]
        if chat_ids:
            return chat_ids

    legacy_value = config.get("chat_id")
    if legacy_value not in (None, ""):
        return [str(legacy_value)]

    return list(DEFAULT_CONFIG["chat_ids"])
