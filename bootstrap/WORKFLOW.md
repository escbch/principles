# Workflow

How I build projects with LLM agents. Distilled from Personal Coach, where
hundreds of issues and PRs were shaped with me and built by agents. It is
domain-neutral: any project, app or not.

The process runs on [mattpocock/skills](https://github.com/mattpocock/skills)
([`skills.md`](skills.md) lists which). This file holds only what I add on top:
my conventions, where I differ from the skills, and the templates for them.

## The idea in one paragraph

I decide; agents ask, write and build. Thinking happens in grilling sessions
with me, one question at a time, and every decision is written into GitHub
Issues with a date. The result is a **work package** an agent can build without
me (`ready-for-agent`). Implementation agents load as little context as
possible, never invent rules, review their own diff, and report what they
could not decide. The repository is the memory: `AGENTS.md`, `GLOSSARY.md`,
docs, ADRs and the issue history. No knowledge lives only in a chat.

## Words

| Term | Meaning |
|---|---|
| **User story** | Who wants what and why: *As a … I want … so that …*. Opens every map. |
| **Map** | One issue (`wayfinder:map`) for a goal bigger than one session: user story, destination, notes, decisions so far, fog, work packages. |
| **Destination** | What is true when the map is done, observable by the user. |
| **Fog** | Questions not answered yet. Each becomes a grilling, research or prototype ticket, or is answered in a session. |
| **Decision** | A dated, testable answer: rule, example, consequence, rejected options. |
| **Work package** | A self-contained issue an agent builds in one PR: requirements, implementation guidance, testing guidelines. |
| **`ready-for-agent`** | Label on a work package that passes the checklist below. |
| **Learning** | A lesson that applies beyond one project; lives in `principles/learnings/`. |

## Roles

| Who | Does | Never |
|---|---|---|
| Me (owner) | Chooses direction, answers questions, reads PRs, merges | Writes long specs by hand |
| Shaping agent (with me) | Charts maps, grills me one question at a time with a recommendation, writes decisions and work packages | Decides for me, implements |
| Implementation agent (AFK) | Builds one work package, reviews its diff, opens a PR, reports deviations | Invents domain rules, widens scope, merges |
| Review agent | Checks the diff against `CODING_STANDARDS.md` and the work package, with fresh context | Rewrites the change |
| Outside LLM (chat) | Discovery, second opinions | Is treated as a spec. Its output feeds a grilling session |

## The pipeline

```text
User story → Map → Fog → Decisions → Work packages → Implement → Review → PR → I merge
                                                                              |
     new questions, follow-ups and learnings go back to issues or principles ┘
```

| Step | Skill | What I add |
|---|---|---|
| Set up a repo | [`INIT.md`](INIT.md) | Everything in [`templates/`](templates/), CI, GitHub setup |
| Capture an idea | `/triage` | Sits as `needs-triage` until it becomes a map or a work package |
| Shape a goal | `/wayfinder <goal>` to chart the map, then `/wayfinder #<map>` once per session | Map starts with the **user story**; decision record format |
| One decision or a small change | `/grill-with-docs` | Decisions worth keeping go into an issue in the record format |
| Write work packages | `/to-tickets` (several, with blocking), `/to-spec` (one) | My work package format, not upstream's |
| Build | `/implement #<n>`, `/implement-spec #<n>` | One work package, one branch, one PR |
| Review | `/code-review` against the base branch, **before** the PR | Fix findings, or list the ones left |
| PR | `.github/pull_request_template.md`, not `/pr` | Deviation, review result, needs user decision |
| Look back | `/retro` | Lessons beyond the project go to `principles/learnings/` |

Also useful: `/research` for facts a decision waits on, `/prototype` when "how
should it look or behave" is the question, `/diagnosing-bugs`, `/tdd`,
`/handoff` to continue in a fresh session.

## The map

Template: [`templates/.github/ISSUE_TEMPLATE/map.md`](templates/.github/ISSUE_TEMPLATE/map.md).

```markdown
## User story
As a <who>, I want <what>, so that <why>.

## Destination
## Notes
## Decisions so far
- 2026-10-26: … (link to the decision comment or ticket)
## Fog
## Work packages
1. #385 Agents module. 2. #386 Prompts in the backend. 3. #387 … Blocked by #385 and #386.
```

While there is fog, `/wayfinder` creates child tickets for it (`wayfinder:grilling`,
`research`, `prototype`, `task`) or answers it in a session. When a part of the
map has no fog left, `/to-tickets` writes its work packages. They say
`Part of #<map>`, are linked as sub-issues, use native blocking for order, and
are listed under **Work packages** in build order.

## Decisions

When a question is resolved, the comment has this shape:

```markdown
## Decision (2026-10-07)
**Rule:** … (exact, testable; numbers and thresholds stated)
**Example:** … (a worked case with real values)
**Consequence:** … (what this means elsewhere)
Rejected: … (and why, in one line each)
```

The map's *Decisions so far* gets one dated line linking it. Hard-to-reverse
or surprising decisions also become an ADR in `docs/adr/`.

## Work packages

Template: [`templates/.github/ISSUE_TEMPLATE/work-package.md`](templates/.github/ISSUE_TEMPLATE/work-package.md).
Unlike upstream `/to-spec`, mine are concrete: they name files and services,
state every rule exactly with a worked example, and list the commands that
prove the change. They are built within days, so paths don't go stale.

- **Requirements:** problem, user story slice, definition (rules, edge cases,
  rounding, null cases), acceptance criteria.
- **Implementation guidance:** scope per layer, files and services, what stays
  where, generated files, migrations.
- **Testing guidelines:** what to test at which level, exact commands.
- **Out of scope** and **Context**.

### Checklist: is this `ready-for-agent`?

- [ ] Says `Part of #<map>`; links its decisions.
- [ ] Every rule is exact, with an example and the edge cases.
- [ ] Implementation guidance names the layers, files or services.
- [ ] Acceptance criteria are observable, including doc and glossary updates.
- [ ] Testing guidelines list the tests and the exact commands.
- [ ] Out of scope is listed.
- [ ] An agent could build it without the chat that produced it.

## Implementation

```text
/implement #<n>. Work on branch feature/<n>-<slug>. Run every command the
work package lists, then /code-review against <base>. Open a PR with the PR
template: "Closes #<n>", any deviation, the review result, and anything that
needs my decision. Don't merge.
```

Batches: "Implement #212, #213, #214 in that order, one PR each, stacked where
one needs the previous. State the merge order in each PR."

- **Never invent a domain rule.** Build the unambiguous part; list the rest
  under **Needs user decision**.
- **Report:** files changed, tests run (with counts), lint result, migrations,
  manual steps, unresolved decisions.
- **I merge.** Agents never merge, and commit or push only when asked or when
  the session is set up for it.

## Review before the PR

1. `AGENTS.md` holds what every agent must know: context loading, invariants,
   behavior, pointers. Short.
2. `CODING_STANDARDS.md` holds judgement calls about code, read at review time.
   Anything mechanical becomes a lint rule or CI check instead.
3. Before opening the PR, the agent runs `/code-review` against the base. It
   fixes what it agrees with and lists the rest in the PR.

## LLMs propose; code decides

For anything that works with the user's data, see
[`../learnings/adaptive-loop.md`](../learnings/adaptive-loop.md). For every project:

- **Deterministic core.** Validation, calculations and safety rules are tested
  code. Models only propose or explain, through the same validated actions a
  person uses. Nothing changes silently.
- **Keep intended, actual and observed data separate**; history keeps its
  original meaning.
- **LLM features start outside the app:** export a deterministic document plus
  a fixed prompt ("Copy for AI") first. Call a model from the app only for
  proposals the user accepts explicitly. Tests never need a live model.

## The repository as memory

| File | Holds | Written by |
|---|---|---|
| `AGENTS.md` (root, plus one per area with its own stack) | Context loading, invariants, conventions, pointers | Init, then by hand |
| `CLAUDE.md` | `@AGENTS.md`, so Claude Code loads the same file | Init |
| `CODING_STANDARDS.md` | Judgement calls the reviewer enforces | Me, `/retro` |
| `GLOSSARY.md` | Terms, one or two sentences each, with `_Avoid_` synonyms | `/domain-modeling` (via `/grill-with-docs`, `/wayfinder`) |
| `docs/adr/` | Hard-to-reverse, surprising decisions | `/domain-modeling` |
| `docs/vision.md` | User story, destination, principles, not wanted | Init, then grilling |
| `docs/<domain>.md` | Canonical rules the glossary doesn't cover | Work package PRs |
| `docs/architecture.md` | Data ownership, enforcement, boundaries | When boundaries change |
| `docs/agents/*.md` | Tracker, labels, domain-doc layout for the skills | Init |
| GitHub Issues | Maps, decisions, work packages: the history of *why* | Every session |

## Learnings flow back

When a lesson applies beyond the project (a CI step that took 10 minutes, a UI
rule, a testing trap), the agent proposes it as a file in
[`../learnings/`](../learnings/) through a PR to principles, following
[`../learnings/README.md`](../learnings/README.md). Every project set up
afterwards links it.

## Writing style

- Plain English, short sentences, lists over prose.
- Exact numbers and thresholds ("more than 20 % and at least 2.0 sets").
- A worked example for every rule. Dates on decisions.
- Titles say what the user can do: "Record cardio bouts during a workout", not
  "Cardio bout API".
- Use `GLOSSARY.md` terms, never a synonym it lists under `_Avoid_`.
