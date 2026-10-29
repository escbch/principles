# Issue tracker: GitHub

Issues and specs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`; `gh` does this automatically when run inside a clone.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view <number> --comments` and `gh pr diff <number>` for the diff.
- **List external PRs for triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE`.
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so resolve a bare issue number by checking the PR first and then the issue.

## When a skill says “publish to the issue tracker”

Create a GitHub issue.

## When a skill says “fetch the relevant ticket”

Run `gh issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: an issue labelled `wayfinder:map`, holding the User story, Destination, Notes, Decisions-so-far, Fog and Work packages body (`.github/ISSUE_TEMPLATE/map.md`).
- **Child ticket**: an issue linked to the map as a GitHub sub-issue. Where sub-issues are unavailable, add it to the map’s task list and put `Part of #<map>` in the child. Use a `wayfinder:<type>` label.
- **Blocking**: use GitHub’s native issue dependencies. Where unavailable, use a `Blocked by: #<n>` line.
- **Frontier query**: select the first open, unblocked, unassigned child in map order.
- **Claim**: assign the issue to the current user.
- **Resolve**: comment with the answer as `## Decision (<date>)` (Rule, Example, Consequence, Rejected), close the issue, and append a dated line linking it to the map’s Decisions-so-far.

## Work packages

Built from a map once its part has no fog left (`/to-tickets`, `/to-spec`).

- **Create**: use `.github/ISSUE_TEMPLATE/work-package.md`; first line `Part of #<map>`; link as a sub-issue of the map.
- **Order**: native issue dependencies (`Blocked by`); list them in build order under the map’s **Work packages**.
- **Ready**: label `ready-for-agent` only when the template’s checklist passes.
