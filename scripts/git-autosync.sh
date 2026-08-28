#!/usr/bin/env bash
# git-autosync.sh — stage, commit, and push any pending changes.
# Safe to run repeatedly; exits quietly when there is nothing to sync.
set -euo pipefail

cd "$(dirname "$0")/.."

# Pull in remote changes first (rebase to keep history linear).
git fetch origin
git rebase "origin/$(git rev-parse --abbrev-ref HEAD)" 2>/dev/null || true

if [ -z "$(git status --porcelain)" ]; then
  echo "autosync: nothing to commit"
else
  git add -A
  git commit -m "autosync: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "autosync: committed"
fi

git push origin "$(git rev-parse --abbrev-ref HEAD)"
echo "autosync: pushed"
