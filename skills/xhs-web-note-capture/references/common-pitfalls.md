# Common Pitfalls

## 1. Logged-in browser but broken profile page

Symptom:

- profile page loads shell UI
- author board partially renders
- `_raw_text` contains "未连接到服务器"

What worked:

- click refresh if exposed in page state
- reopen the profile from search results
- use the search page or author board as the navigation root instead of insisting on the first broken profile load

## 2. Bare note ID fails on web

Symptom:

- opening `https://www.xiaohongshu.com/explore/<note_id>` shows "当前笔记暂时无法浏览"

Cause:

- many web note pages require the session-specific `xsec_token`

What worked:

- open the author board while logged in
- click the exact post title
- read `location.href`
- reuse the resulting `pc_user` URL with `xsec_token`

## 3. Anchor exists but `href` is blank

Symptom:

- browser DOM inspection finds the title
- the visible title anchor has no usable `href`

What worked:

- click the live title element instead of trying to reconstruct the URL offline
- then read `location.href`

## 4. The useful data is not in visible DOM text

Symptom:

- visible page text is truncated
- image-heavy post has little copy in the DOM

What worked:

- parse `window.__INITIAL_STATE__`
- use:
  - `note.currentNoteId`
  - `note.noteDetailMap[currentNoteId].note`
  - `note.imageList`
  - `note.tagList`
  - `note.interactInfo`

## 5. OCR package install is flaky

Symptom:

- `pip install rapidocr_onnxruntime pillow` stalls or fails
- connection reset during package download

What worked:

- switch to macOS Vision OCR
- compile `scripts/ocr_vision.swift`
- call the binary from the extractor

## 6. OCR quality is imperfect

Reality:

- Chinese long-image OCR is good but not perfect
- there will be some wrong characters or missed lines

Recommendation:

- preserve raw OCR output
- keep original image links and local image paths in markdown
- if the user needs polished prose, do a second cleanup pass after extraction
