# Common Flows

## 1. Verify installation

```bash
source ~/.bashrc
browser-use doctor
browser-use --help
```

## 2. Open a session and inspect

```bash
source ~/.bashrc
browser-use --headed --session demo open https://example.com
browser-use --json --session demo state
```

## 3. Click an indexed element

Read `state`, find a line like:

```text
[5447]<a />
    发布
```

Then click it:

```bash
source ~/.bashrc
browser-use --session demo click 5447
browser-use --json --session demo state
```

## 4. Upload a local file

Find the indexed file input in `state`:

```text
*[9010]<input type=file ... />
```

Upload:

```bash
source ~/.bashrc
browser-use --session demo upload 9010 /absolute/path/to/file.png
```

Use absolute paths only.

## 5. Fill a normal input

```bash
source ~/.bashrc
browser-use --session demo input 9311 "浏览器AI实测后，我的几点小心得"
```

## 6. Fill a rich text editor with eval

Pattern:

```bash
source ~/.bashrc
browser-use --json --session demo eval "(() => {
  const el = document.querySelector('[contenteditable=\"true\"][role=\"textbox\"]');
  if (!el) return 'no editor';
  const text = '第一段\\n\\n第二段';
  el.focus();
  el.innerHTML = '';
  text.split('\\n').forEach((line) => {
    const p = document.createElement('p');
    if (line) p.textContent = line;
    else p.appendChild(document.createElement('br'));
    el.appendChild(p);
  });
  el.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: text }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
  return el.innerText.slice(0, 80);
})()"
```

Use this when `input` does not persist or the editor is not a normal `<input>`.

## 7. Discover hidden link targets

When a button click does nothing visible, inspect the page:

```bash
source ~/.bashrc
browser-use --json --session demo eval "Array.from(document.querySelectorAll('a,button')).map((el,i)=>({i,text:(el.innerText||el.textContent||'').trim(),href:el.href||'',target:el.target||''})).filter(x=>x.text.includes('发布')||x.text.includes('创作中心')).slice(0,20)"
```

This is useful when:

- the visible entry opens a new tab
- you need to open the backend URL directly

## 8. Known command quirks

- Correct:

```bash
browser-use --json --session demo state
```

- Incorrect:

```bash
browser-use --session demo state --json
```

- Correct:

```bash
browser-use --session demo wait text 发布
```

- Incorrect:

```bash
browser-use --session demo wait 5
```

## 9. Clean up

```bash
source ~/.bashrc
browser-use sessions
browser-use --session demo close
```
