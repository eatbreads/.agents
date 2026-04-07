#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
from pathlib import Path


def run(cmd: str):
    p = subprocess.run(
        cmd,
        shell=True,
        text=True,
        capture_output=True,
        executable="/bin/bash",
    )
    return {
        "cmd": cmd,
        "code": p.returncode,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
    }


def find_candidates():
    home = Path.home()
    cwd = Path.cwd()
    candidates = []
    for base in [cwd, home]:
        for rel in [
            ".local/npm/bin/lark-cli",
            ".local/node/bin/node",
            ".local/node-v24.14.1-darwin-arm64/bin/node",
            ".local/node-v24.14.1-darwin-arm64/bin/npm",
        ]:
            p = base / rel
            if p.exists():
                candidates.append(str(p))
    return candidates


def infer(results, candidates):
    bash = results["bash"]
    zsh = results["zsh"]
    def parse(which_stdout: str):
        data = {}
        for line in which_stdout.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
        return data

    bash_map = parse(bash["stdout"])
    zsh_map = parse(zsh["stdout"])
    bash_has_lark = bool(bash_map.get("lark-cli"))
    zsh_has_lark = bool(zsh_map.get("lark-cli"))
    bash_has_node = bool(bash_map.get("node"))
    zsh_has_node = bool(zsh_map.get("node"))

    if zsh_has_lark and not bash_has_lark:
        return {
            "likely_cause": "Interactive zsh loads PATH entries that the current shell session does not.",
            "suggested_fix": "Run lark-cli through `zsh -lic` or export the same PATH entries in the current shell.",
        }
    if zsh_has_lark and not bash_has_node:
        return {
            "likely_cause": "lark-cli is present but its node runtime is missing in the current shell PATH.",
            "suggested_fix": "Export the project-local Node bin before invoking lark-cli.",
        }
    if candidates and not zsh_has_lark and not bash_has_lark:
        return {
            "likely_cause": "Binaries exist on disk but are not exported in either shell PATH.",
            "suggested_fix": "Add the discovered directories to PATH or invoke using explicit absolute paths.",
        }
    if not candidates and not zsh_has_lark and not bash_has_lark:
        return {
            "likely_cause": "No local lark-cli installation was discovered in common paths.",
            "suggested_fix": "Use the install/setup workflow instead of PATH repair.",
        }
    return {
        "likely_cause": "Environment looks mostly healthy; verify the exact command and identity-specific issue.",
        "suggested_fix": "Run a real command such as `lark-cli auth status`.",
    }


def main():
    results = {
        "bash": run(
            "bash -lc 'printf \"node:%s\\n\" \"$(which node 2>/dev/null || true)\"; "
            "printf \"npm:%s\\n\" \"$(which npm 2>/dev/null || true)\"; "
            "printf \"lark-cli:%s\\n\" \"$(which lark-cli 2>/dev/null || true)\"'"
        ),
        "zsh": run(
            "zsh -lic 'printf \"node:%s\\n\" \"$(which node 2>/dev/null || true)\"; "
            "printf \"npm:%s\\n\" \"$(which npm 2>/dev/null || true)\"; "
            "printf \"lark-cli:%s\\n\" \"$(which lark-cli 2>/dev/null || true)\"'"
        ),
    }
    candidates = find_candidates()
    payload = {
        "cwd": os.getcwd(),
        "candidates": candidates,
        "checks": results,
    }
    payload.update(infer(results, candidates))
    print(json.dumps(payload, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
