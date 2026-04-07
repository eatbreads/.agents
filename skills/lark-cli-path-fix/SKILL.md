---
name: lark-cli-path-fix
description: "Diagnose and recover environments where `lark-cli` or its `node` runtime cannot be found even though they were installed previously. Use when Codex sees `lark-cli: command not found`, `env: node: No such file or directory`, shell-specific PATH drift between `zsh` and `bash`, project-local Node/npm bin setups, or broken AI agent sessions that fail to load the user's shell init files."
---

# Lark CLI Path Fix

## Overview

Recover a working `lark-cli` invocation when the tool exists on disk but the current shell or agent cannot resolve it.

Prefer using the bundled diagnostic script first, then apply the smallest fix that restores a working command.

## Quick Start

1. Run `scripts/check_lark_cli_env.py`.
2. Compare `bash` and `zsh` resolution for `node`, `npm`, and `lark-cli`.
3. Identify whether the failure is:
   - PATH not loaded in the current shell
   - shell init file mismatch (`.zshrc` vs `.bashrc`)
   - project-local Node/npm bin not exported
   - `lark-cli` present but its `node` interpreter missing from PATH
4. Use a temporary recovery command first.
5. Only then make a persistent shell config change if needed.

## Workflow

### 1. Confirm the symptom

Check the exact failure mode before changing anything:

```bash
bash -lc 'which lark-cli || true; which node || true'
zsh -lic 'which lark-cli || true; which node || true'
```

Common signatures:

- `lark-cli: command not found`
- `env: node: No such file or directory`
- `zsh` can find the command but `bash` cannot
- the CLI exists under a project-local npm bin directory but that path is not exported in the current shell

### 2. Run the diagnostic script

Use:

```bash
python3 scripts/check_lark_cli_env.py
```

The script reports:

- whether `bash` can resolve `node`, `npm`, and `lark-cli`
- whether `zsh -i` can resolve them
- likely install locations under common project-local directories
- likely cause and suggested recovery commands

### 3. Prefer a temporary recovery first

If `zsh -i` works but the current shell does not, prefer one of these short-term fixes:

```bash
zsh -lic 'lark-cli ...'
```

or export the exact directories for the current command:

```bash
export PATH="/path/to/node/bin:/path/to/npm/bin:$PATH"
lark-cli ...
```

This is the safest option inside AI agent sessions because they often do not load the same init files as the user's interactive shell.

### 4. Make a persistent fix only if the user wants it

Typical persistent fix:

- add project-local Node and npm bin paths to the relevant shell init file
- keep the change minimal and explicit
- avoid duplicating PATH lines across many files unless necessary

Example:

```bash
export PATH="/project/.local/node-v24.14.1-darwin-arm64/bin:/project/.local/npm/bin:$PATH"
```

### 5. Verify with a real command

Do not stop at `which lark-cli`. Verify the actual runtime chain:

```bash
zsh -lic 'which node; node -v; which lark-cli; lark-cli --version'
```

If the user's task depends on a Lark operation, verify one real command too, such as:

```bash
zsh -lic 'lark-cli auth status'
```

## Decision Rules

- If `zsh -i` works and `bash` fails: treat it as shell init loading drift, not a missing install.
- If `lark-cli` exists but `node` does not: fix `node` PATH first.
- If both shells fail but files exist under project-local `.local/` directories: export those directories explicitly.
- If nothing exists on disk: this skill is not the right fix path; switch to install/setup instead.
- If the user already has a working `~/.zshrc`, prefer invoking `zsh -lic` over rewriting unrelated shell files.

## References

- Read [references/common-cases.md](references/common-cases.md) for the most common failure patterns and recommended fixes.
