# {{PROJECT}} — Repository Instructions

<!-- Init: fill every placeholder, delete sections marked "if", and delete
these comments. Keep this file short; judgement calls about code go in
CODING_STANDARDS.md. -->

## Context loading

For implementation work, read:

1. the work package, including comments and linked decisions;
2. the closest applicable `AGENTS.md`;
3. the relevant implementation and tests;
4. docs and ADRs the work package links.

Read `GLOSSARY.md` when domain terms are involved.

Don't read `docs/vision.md`, `docs/<domain>.md` or `docs/architecture.md` by
default for a `ready-for-agent` work package. Read only relevant sections when
it links them, or when the change affects product direction, domain behavior,
historical meaning or system boundaries.

For shaping (maps, decisions, work packages): `docs/vision.md` for direction,
`docs/<domain>.md` for domain behavior, `docs/architecture.md` for boundaries,
and the relevant ADRs.

## Repository-wide invariants

- <Rule that must never break, e.g. "Keep planned and recorded data separate.">
- <The <layer> owns domain rules and validation; <other layers> consume its
  contracts and don't reproduce those rules.>
- <…three to six in total.>

<!-- If the project calls LLMs or models: -->
- Deterministic validation and calculations stay independent of LLM behavior.
  Models only propose, through the same validated actions as a person. Tests
  never need a live model.

<!-- If the project records outcomes, analyses trends or proposes changes: -->
## Adaptive loop

This project follows
[`{{PRINCIPLES}}` → `learnings/adaptive-loop.md`](https://github.com/{{PRINCIPLES}}/blob/main/learnings/adaptive-loop.md):
decide → act → record → measure → learn → propose; the user decides. Fixed,
tested rules are the baseline; a model must beat them before its proposals are
trusted.

## Commands

Run before considering a change complete:

```sh
<format check>
<lint>
<type check / build>
<tests>
```

## Workflow

How work is shaped and built:
[`{{PRINCIPLES}}` → `bootstrap/WORKFLOW.md`](https://github.com/{{PRINCIPLES}}/blob/main/bootstrap/WORKFLOW.md).
These conventions override the skills where they differ.

- **Maps** (`/wayfinder`): use `.github/ISSUE_TEMPLATE/map.md`. A map starts
  with the **User story** and **Destination**.
- **Decisions** (`/wayfinder`, `/grill-with-docs`): record a resolution as
  `## Decision (<date>)` with **Rule**, **Example**, **Consequence** and
  **Rejected**, and add a dated line to the map's *Decisions so far*.
- **Work packages** (`/to-tickets`, `/to-spec`): use
  `.github/ISSUE_TEMPLATE/work-package.md`: requirements, implementation
  guidance, testing guidelines. Name files and services, state each rule
  exactly with a worked example, list the test commands. Label
  `ready-for-agent` only when it passes the checklist in the template.
- **Implementation:** one work package, one branch `feature/<issue>-<slug>`,
  one PR. A stacked PR states its base and merge order.
- **Review:** before opening a PR, run `/code-review` against the base branch.
  Fix what you agree with; list the rest in the PR.
- **PR body:** `.github/pull_request_template.md`, not `/pr`.

## Agent behavior

- Prefer explicit, typed, small, reviewable changes. Preserve existing behavior
  unless the work package changes it.
- No speculative abstractions or dependencies without a stated need.
- If a domain rule is ambiguous, don't invent behavior. Build the unambiguous
  part and report the rest under `Needs user decision`.
- Never merge. Never push to `main`; it takes changes only through PRs. Commit
  or push only when asked. Never commit secrets or `.env`.

After implementation, report:

1. files changed;
2. tests run (with counts);
3. lint result;
4. migrations created;
5. manual steps required;
6. unresolved domain decisions.

## Cross-project learnings

From [`{{PRINCIPLES}}` → `learnings/`](https://github.com/{{PRINCIPLES}}/tree/main/learnings):

<!-- Init: one line per learning that applies to this project, e.g.: -->
- [`ui-building.md`](https://github.com/{{PRINCIPLES}}/blob/main/learnings/ui-building.md):
  read before shaping or building a screen.
- [`ci-speed.md`](https://github.com/{{PRINCIPLES}}/blob/main/learnings/ci-speed.md):
  read before changing CI workflows.

When you learn something that applies beyond this repository, propose it as a
new or updated file in `{{PRINCIPLES}}/learnings/` through a pull request
there, following its `README.md`. Mention it in your report.

## Agent skills

### Issue tracker

Issues and work packages are tracked in GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Triage uses the five default canonical labels. See `docs/agents/triage-labels.md`.

### Domain docs

This repository uses a single-context domain-doc layout. See `docs/agents/domain.md`.
