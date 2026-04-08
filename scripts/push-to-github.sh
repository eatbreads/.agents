#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "当前目录不是 Git 仓库: ${REPO_ROOT}" >&2
  exit 1
fi

REMOTE_NAME="${REMOTE_NAME:-origin}"
BRANCH_NAME="${BRANCH_NAME:-$(git rev-parse --abbrev-ref HEAD)}"
COMMIT_MESSAGE="${1:-chore: update .agents skills}"

if ! git remote get-url "${REMOTE_NAME}" >/dev/null 2>&1; then
  echo "未找到远端 ${REMOTE_NAME}" >&2
  exit 1
fi

echo "仓库目录: ${REPO_ROOT}"
echo "远端: ${REMOTE_NAME}"
echo "分支: ${BRANCH_NAME}"

if [[ -n "$(git status --short)" ]]; then
  echo "检测到未提交改动，开始提交..."
  git add .
  git commit -m "${COMMIT_MESSAGE}"
else
  echo "没有新的工作区改动，跳过提交。"
fi

echo "推送到 ${REMOTE_NAME}/${BRANCH_NAME} ..."
git push "${REMOTE_NAME}" "HEAD:${BRANCH_NAME}"

echo "完成。"
