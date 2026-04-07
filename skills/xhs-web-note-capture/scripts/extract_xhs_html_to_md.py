#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


UA = "Mozilla/5.0"


def load_state(html_path: Path) -> dict[str, Any]:
    text = html_path.read_text("utf-8")
    match = re.search(r"window\.__INITIAL_STATE__=(\{.*\})</script>", text, re.S)
    if not match:
        raise RuntimeError(f"failed to find __INITIAL_STATE__ in {html_path}")
    payload = re.sub(r"\bundefined\b", "null", match.group(1))
    return json.loads(payload)


def current_note(state: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    note_state = state["note"]
    note_id = note_state["currentNoteId"]
    note = note_state["noteDetailMap"][note_id]["note"]
    return note_id, note


def ts_to_text(ms: Any) -> str:
    if not ms:
        return ""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(ms) / 1000))


def best_image_url(image: dict[str, Any]) -> str:
    for key in ("urlDefault", "urlPre", "url"):
        value = image.get(key)
        if value:
            return html.unescape(value).replace("\\u002F", "/")
    for item in image.get("infoList", []):
        value = item.get("url")
        if value:
            return html.unescape(value).replace("\\u002F", "/")
    return ""


def sanitize(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "file"


def download(url: str, dst: Path) -> None:
    req = Request(url, headers={"User-Agent": UA, "Referer": "https://www.xiaohongshu.com/"})
    with urlopen(req) as resp:
        dst.write_bytes(resp.read())


def ensure_ocr_binary(skill_dir: Path) -> Path:
    bin_path = skill_dir / "scripts" / "ocr_vision"
    if bin_path.exists():
        return bin_path
    src = skill_dir / "scripts" / "ocr_vision.swift"
    subprocess.run(["swiftc", str(src), "-o", str(bin_path)], check=True)
    return bin_path


def run_ocr(bin_path: Path, image_path: Path) -> str:
    proc = subprocess.run([str(bin_path), str(image_path)], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return f"OCR failed: {proc.stderr.strip() or proc.stdout.strip()}"
    return proc.stdout.strip()


def build_markdown(note_url: str, note: dict[str, Any], images: list[dict[str, str]]) -> str:
    user = note.get("user", {})
    interact = note.get("interactInfo", {})
    tags = [f"#{item['name']}" for item in note.get("tagList", []) if item.get("name")]
    parts = [
        f"# {note.get('title', '').strip()}",
        "",
        f"- 作者：{user.get('nickname', '')}",
        f"- 小红书用户 ID：{user.get('userId', '')}",
        f"- 发布时间：{ts_to_text(note.get('time'))}",
        f"- 最后更新：{ts_to_text(note.get('lastUpdateTime'))}",
        f"- IP 属地：{note.get('ipLocation', '')}",
        f"- 点赞：{interact.get('likedCount', '')}",
        f"- 收藏：{interact.get('collectedCount', '')}",
        f"- 评论：{interact.get('commentCount', '')}",
        f"- 分享：{interact.get('shareCount', '')}",
        f"- 原帖链接：{note_url}",
        "",
        "## 正文",
        "",
        (note.get("desc") or "").strip(),
        "",
        "## 话题",
        "",
        " ".join(tags) if tags else "无",
        "",
        "## 图片 OCR",
        "",
    ]
    for i, info in enumerate(images, start=1):
        parts.extend(
            [
                f"### 图片 {i}",
                "",
                f"- 本地文件：{info['path']}",
                f"- 原图链接：{info['url']}",
                "",
                info["ocr"] or "未识别到清晰文字",
                "",
            ]
        )
    return "\n".join(parts).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", action="append", required=True, help="saved Xiaohongshu note HTML file")
    parser.add_argument("--out-dir", required=True, help="output directory")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    ocr_bin = ensure_ocr_binary(skill_dir)

    for html_file in args.html:
        html_path = Path(html_file).resolve()
        state = load_state(html_path)
        _, note = current_note(state)
        slug = sanitize(note.get("title", html_path.stem)).lower()
        note_url = state.get("global", {}).get("url", "")

        img_dir = out_dir / slug
        img_dir.mkdir(parents=True, exist_ok=True)
        image_rows = []
        for idx, image in enumerate(note.get("imageList", []), start=1):
            url = best_image_url(image)
            if not url:
                continue
            suffix = Path(url.split("?")[0]).suffix or ".jpg"
            local_path = img_dir / f"{idx:02d}{suffix}"
            if not local_path.exists():
                download(url, local_path)
            image_rows.append(
                {
                    "path": str(local_path),
                    "url": url,
                    "ocr": run_ocr(ocr_bin, local_path),
                }
            )

        md = build_markdown(note_url, note, image_rows)
        (out_dir / f"{slug}.md").write_text(md, "utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
