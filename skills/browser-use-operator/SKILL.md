---
name: browser-use-operator
description: "Operate real websites through the local `browser-use` CLI on this machine. Use when Codex should open pages, keep a named browser session alive, inspect interactive page state, click indexed elements, upload local files, hand off login to the user, continue after login, or automate real web workflows such as creator backends, dashboards, and repetitive browser tasks. Prefer this skill over ad hoc browser-use usage when the task depends on stable session handling, headed browsing, or site-specific interaction debugging."
---

# Browser Use Operator

## Overview

Use the local `browser-use` setup on this machine instead of inventing one-off browser automation commands.

Prefer real execution over theory:

1. open a named session
2. inspect the current page with `state`
3. act with `click`, `input`, `upload`, or `eval`
4. re-read state after every important transition
5. close the session when the task is complete

## Machine Assumptions

This environment already has a working `browser-use` command in PATH after:

```bash
source ~/.bashrc
```

If `browser-use` is unexpectedly missing, use the `lark-cli-path-fix` style diagnosis pattern:

- verify `browser-use --help`
- verify `~/.bashrc` is loaded
- fall back to explicit path invocation if needed

## Quick Start

### Headed interactive session

Use this for login-required sites and user handoff:

```bash
source ~/.bashrc
browser-use --headed --session mysite open https://example.com
```

### Read current page state

Use after every major action:

```bash
source ~/.bashrc
browser-use --json --session mysite state
```

### Continue after login

After the user logs in manually, re-open or read state from the same session:

```bash
source ~/.bashrc
browser-use --session mysite open https://example.com/protected
browser-use --json --session mysite state
```

### Close when done

```bash
source ~/.bashrc
browser-use --session mysite close
```

## Workflow

### 1. Start with the right session mode

Choose one:

- `--headed` for sites that need manual login, captchas, visual confirmation, or user handoff
- default headless mode for quick checks and low-risk scripted actions
- `--profile Default` only when you explicitly want a real Chrome profile path

Use stable session names like:

- `xhs`
- `feishu`
- `admin-check`

Do not create a new session for every single command if the workflow belongs to one site visit.

### 2. Use `state` as the source of truth

Do not guess element indices.

Always read:

```bash
browser-use --json --session NAME state
```

Use the returned `_raw_text` to inspect:

- visible text
- indexed interactive elements like `[5447]<a /> 发布`
- whether login succeeded
- whether the page actually transitioned

Re-read state after:

- login
- navigation
- uploads
- tab changes
- clicks that should reveal a form

### 3. Act with the smallest reliable command

Preferred order:

1. `click INDEX` when the target is visible and indexed
2. `input INDEX "text"` for normal inputs
3. `upload INDEX /abs/path/file.png` for file inputs
4. `eval "..."` for rich text editors, JS-only interactions, or hard-to-index elements

Use `eval` sparingly, but it is the right tool for:

- contenteditable editors
- extracting hidden link targets
- filling custom editors that `input` cannot reach

### 4. Expect site transitions to be messy

Real sites often behave like this:

- clicking does not visibly navigate
- the target opens in a new tab
- the page needs a few seconds before `state` reflects the change
- main site login does not carry into creator/admin subdomains

When that happens:

1. read state again
2. inspect actual `href` or button behavior with `eval`
3. open the target URL directly if needed
4. verify again

### 5. Hand off cleanly to the user

If a site requires a human login:

- open in `--headed`
- stop at the login page
- ask the user to complete login
- resume from the same session after they confirm

Do not attempt to bypass captchas or authentication barriers.

## Common Patterns

### Open site, wait for manual login, continue

```bash
source ~/.bashrc
browser-use --headed --session site open https://example.com
browser-use --json --session site state
```

After the user says login is done:

```bash
source ~/.bashrc
browser-use --session site open https://example.com/next-page
browser-use --json --session site state
```

### Upload an image or file

1. switch to the correct page mode
2. inspect `state` and find the `input type=file`
3. upload using an absolute path

```bash
source ~/.bashrc
browser-use --session site upload 9010 /abs/path/file.png
```

### Fill rich text with `eval`

Use for editors like:

- `contenteditable=true`
- custom React editors
- form fields where `input` does not persist

See [references/common-flows.md](references/common-flows.md) for patterns.

## Decision Rules

- Prefer `source ~/.bashrc` before every browser-use command in shell execution.
- Prefer `--json state` for debugging instead of trying random clicks.
- Prefer direct URL open when site navigation is clearly implemented as a link target.
- Prefer user handoff for login instead of trying to automate credentials.
- Prefer leaving the final “publish” or other irreversible action to explicit user confirmation unless the user clearly asks to proceed.

## Common Pitfalls

- `wait` is subcommand-based, not sleep-based. Use `wait text ...` or `wait selector ...`, not `wait 5`.
- `--json` must appear before the subcommand, not after it.
- session continuity matters; do not accidentally switch session names mid-flow.
- some sites need direct navigation to backend URLs even after a front-page click.
- uploads may succeed before the page visually refreshes; re-read state after a short pause.

## References

- Read [references/common-flows.md](references/common-flows.md) for concrete command patterns and troubleshooting.
