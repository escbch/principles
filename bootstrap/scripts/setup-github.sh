#!/usr/bin/env bash
# Set up a GitHub repository for the agent workflow: labels, merge options,
# and a ruleset that keeps `main` behind pull requests.
#
# Usage: setup-github.sh <owner>/<repo> [--dry-run]
# Needs: gh, logged in with the `repo` scope. Safe to run again.
set -euo pipefail

repo="${1:-}"
dry_run=false
[[ "${2:-}" == "--dry-run" ]] && dry_run=true

if [[ ! "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
  echo "Usage: $0 <owner>/<repo> [--dry-run]" >&2
  exit 2
fi

run() {
  if $dry_run; then
    printf 'would run:'; printf ' %q' "$@"; printf '\n'
  else
    "$@"
  fi
}

echo "== Labels"
# name|colour|description. The skills read these exact names.
labels=(
  "needs-triage|ededed|Maintainer needs to evaluate this issue"
  "needs-info|d876e3|Waiting on reporter for more information"
  "ready-for-agent|0e8a16|Fully specified work package, ready for an AFK agent"
  "ready-for-human|fbca04|Needs a human to implement"
  "wontfix|ffffff|Will not be actioned"
  "wayfinder:map|5319e7|A map: user story, decisions, fog, work packages"
  "wayfinder:grilling|c5def5|Fog answered by grilling the owner"
  "wayfinder:research|c5def5|Fog answered by research"
  "wayfinder:prototype|c5def5|Fog answered by a prototype"
  "wayfinder:task|c5def5|Fog answered by a small task"
)
for entry in "${labels[@]}"; do
  IFS='|' read -r name colour description <<<"$entry"
  run gh label create "$name" --repo "$repo" --color "$colour" \
    --description "$description" --force
done

echo "== Merge options"
# Branches go away after merge; squash and merge commits both allowed.
run gh api --method PATCH "repos/$repo" --silent \
  -F delete_branch_on_merge=true \
  -F allow_squash_merge=true \
  -F allow_merge_commit=true \
  -F allow_rebase_merge=false \
  -F allow_auto_merge=false

echo "== Ruleset for main"
# Pull request required, no force pushes, no deletion. No required status
# checks: path-filtered workflows would leave PRs waiting (see bootstrap/ci.md).
# No bypass: agents use the owner's token, so a bypass would let them push.
ruleset='{
  "name": "main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0,
      "dismiss_stale_reviews_on_push": false,
      "require_code_owner_review": false,
      "require_last_push_approval": false,
      "required_review_thread_resolution": false
    }}
  ]
}'

if $dry_run; then
  echo "would create or update ruleset 'main' on $repo"
  exit 0
fi

if ! existing=$(gh api "repos/$repo/rulesets" --jq '.[] | select(.name == "main") | .id' 2>&1); then
  if grep -q 'Upgrade to GitHub Pro' <<<"$existing"; then
    echo "Skipped: rulesets on a private repository need GitHub Pro or a public repository."
    echo "Until then, agents must not push to main by convention (AGENTS.md says so)."
    exit 0
  fi
  echo "$existing" >&2
  exit 1
fi

if [[ -n "$existing" ]]; then
  gh api --method PUT "repos/$repo/rulesets/$existing" --input - --silent <<<"$ruleset"
  echo "Updated ruleset 'main'."
else
  gh api --method POST "repos/$repo/rulesets" --input - --silent <<<"$ruleset"
  echo "Created ruleset 'main'."
fi
