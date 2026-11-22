#!/bin/sh
# This repository is public. Fail when a tracked file names another repository
# of the owner: `escbch/<name>` or the short form `<name>#<number>`. Say what
# was decided and when instead ("the UI review of 2026-11").
#   sh scripts/check-references.sh
set -eu
cd "$(dirname "$0")/.."
found=$(git grep -nIE '(^|[^A-Za-z0-9/._-])(escbch/[A-Za-z0-9._-]+|[A-Za-z][A-Za-z0-9-]*#[0-9]+)' -- . ':!scripts/check-references.sh' |
  grep -vE '(escbch/principles|principles#[0-9]+)([^A-Za-z0-9._-]|$)' || true)
if [ -n "$found" ]; then
  printf '%s\n' "$found"
  echo "check-references: the lines above name another repository." >&2
  exit 1
fi
echo "check-references: ok"
