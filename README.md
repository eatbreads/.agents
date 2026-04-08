# Shared `.agents` repository

This repository stores reusable agent skills that are shared across terminals and machines.

## Layout

- `skills/`: shared user-maintained skills
- `secret`: local-only service-account or API secret file for this workspace, for example the default Bits service-account secret used by reporting skills

## Scope

This repository intentionally excludes Codex runtime state such as auth, config, logs, sessions, caches, databases, and system-provided skills.

## Local Secret Convention

Use [secret](/Users/bytedance/Documents/trae_projects/test/.agents/secret) as the default local secret file when a skill in this workspace needs a machine-local credential and no environment variable has been provided.

This file is intentionally gitignored and should stay local to the machine.


.agents/scripts/push-to-github.sh
.agents/scripts/push-to-github.sh "feat: add fsx pipeline report skill"
