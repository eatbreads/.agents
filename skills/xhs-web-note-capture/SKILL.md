---
name: xhs-web-note-capture
description: Extract Xiaohongshu posts into local markdown from a real logged-in browser session. Use when Codex needs to capture one or more 小红书 posts, hidden text-heavy image posts, or author-board posts that require login, `xsec_token`, browser-state inspection, HTML snapshot parsing, image download, and OCR.
---

# XHS Web Note Capture

## Overview

Capture Xiaohongshu posts from a real browser session, then convert the logged-in note page into local markdown with metadata,正文, image URLs, and OCR text from screenshots.

Prefer this skill when:

- the user wants full post content rather than a short summary
- the post is hidden behind login
- the author board is accessible but direct note URLs are blocked
- much of the content lives inside images

## Workflow

1. Use `browser-use-operator` first.
2. Keep one stable session, usually `xhs`.
3. If login is required, stop and hand off to the user.
4. Avoid guessing note URLs from bare IDs.
5. Enter the note from the logged-in author page or search results so the browser lands on a `pc_user` note URL that includes `xsec_token`.
6. Save the final note HTML with cookies if you need an offline artifact.
7. Parse `window.__INITIAL_STATE__` from the saved HTML.
8. Download `imageList` images and run OCR.
9. Write one markdown file per post.

## Key Rules

- Prefer `browser-use --json --session xhs state` after every important transition.
- Prefer clicking the note title from the logged-in author page over opening `https://www.xiaohongshu.com/explore/<note_id>` directly.
- Treat the `pc_user` note URL with `xsec_token` as the durable fetch URL for `curl`.
- Extract note data from `window.__INITIAL_STATE__.note.noteDetailMap[currentNoteId].note`.
- Use the note page HTML as the source of truth for metadata and image URLs.
- Expect OCR noise; preserve raw OCR output instead of over-cleaning.

## Failure Patterns

- Author profile page shows "未连接到服务器" or incomplete content.
  Fix: refresh, switch to site search, or reopen the profile with a valid `xsec_token`.

- Direct note URL says the note cannot be viewed on web.
  Fix: click through from the logged-in author page to get a `?xsec_token=...&xsec_source=pc_user` URL, then reuse that URL for `curl`.

- State shows the note title on the board, but direct anchor `href` is empty.
  Fix: click the visible title element in the live session, then read `location.href`.

- OCR Python dependencies fail or are slow to install.
  Fix: use the bundled macOS Vision OCR script in `scripts/ocr_vision.swift`.

## Scripts

- `scripts/extract_xhs_html_to_md.py`
  Use to convert one or more saved note HTML files into markdown plus downloaded images.

- `scripts/ocr_vision.swift`
  Compile with `swiftc` and use as the OCR backend on macOS.

## References

- Read [references/common-pitfalls.md](references/common-pitfalls.md) when the browser flow looks inconsistent, the note is blocked on web, or OCR quality is poor.

## Minimal Command Pattern

```bash
source ~/.bashrc
browser-use --headed --session xhs open 'https://www.xiaohongshu.com/'
browser-use --json --session xhs state
```

After login and after clicking into the real note page:

```bash
source ~/.bashrc
browser-use --session xhs eval 'location.href'
```

Save HTML with cookies:

```bash
COOKIE=$(jq -r '.[] | select(.domain|contains("xiaohongshu.com")) | "\(.name)=\(.value)"' xhs_cookies.json | paste -sd '; ' -)
curl -L "$NOTE_URL" -H "cookie: $COOKIE" -H 'user-agent: Mozilla/5.0' -H 'referer: https://www.xiaohongshu.com/' -o note.html
```

Convert to markdown:

```bash
python3 scripts/extract_xhs_html_to_md.py --html note.html --out-dir ./xhs_output
```
