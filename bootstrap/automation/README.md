# Automation: build, review, fix, pull request

Runs `ready-for-agent` work packages without me switching models or pasting
prompts. One **orchestrator** session works through a list of tickets. For
each ticket it starts a **builder** session on one repository, then a
**reviewer** session with a fresh context on a stronger model, sends the
findings back to the builder once, and the builder opens the pull request.
I merge.

| File | Read by | Purpose |
|---|---|---|
| [`orchestrator.md`](orchestrator.md) | the session I start | the loop, the stop rules, how to wait |
| [`builder.md`](builder.md) | one session per ticket | build, hand over for review, fix once, open the pull request |
| [`reviewer.md`](reviewer.md) | one session per ticket | check the branch against the ticket and the standards; findings only |

This differs from [`../WORKFLOW.md`](../WORKFLOW.md) in one point: the builder
does not run `/code-review` on its own diff. The reviewer session replaces it.

## Why two stages, not three

Every handoff between sessions costs a fixed amount: the new session reads the
ticket, `AGENTS.md` and the files again. For the mechanical steps inside a
ticket (branch, copies, running tests) that costs more than a smaller model
saves, so the builder does them. A separate cheap session is worth it only for
a standalone chore across repositories, such as updating a checked copy
everywhere.

## Models (a judgement; change them in the orchestrator's start message)

| Role | Model | Effort |
|---|---|---|
| Builder | `claude-sonnet-5-5` | default |
| Reviewer | `claude-opus-5-5` | medium |
| Orchestrator | whatever the session runs on; it does little | |

## Start it

Start one session with the repositories of the tickets attached, and say:

```text
Read escbch/principles bootstrap/automation/orchestrator.md and follow it.
Tickets, in order: <owner/repo#n>, <owner/repo#n (stacked on #m)>, …
Project handoff: <path or issue comment that holds the project's rules>.
```

## First run (2026-11-16)

One ticket, escbch/site#54 (a static page: 11 files, about 100 lines changed
beside two copied files):

| Step | Model | Time | Context used | Cost |
|---|---|---|---|---|
| Build, hand over | `claude-sonnet-5-5` | 2 min | | |
| Review | `claude-opus-5-5`, medium | 2 min | 112,000 tokens | 0.96 USD |
| Fix once, open the pull request | the builder again | 1 min | 136,000 tokens in total | 0.91 USD in total |

- The reviewer confirmed all five acceptance criteria, reproduced every
  command, and found one spacing defect the builder's measurements had not
  shown. The builder fixed it and opened the pull request.
- Both children reported by themselves; the scheduled check was not needed.
- Reading the role file and the handoff from a repository worked; the start
  messages stayed short.

## Limits

- A session that finishes cleanly may not report back. The orchestrator checks
  on its children; it does not only wait.
- A child session sees only its own repository. What it needs from another one
  (a map's decisions, a review document) must be in the ticket, in the project
  handoff, or readable without credentials.
- The orchestrator never merges and never works around a stop rule. When it
  stops, it says why and what is waiting.
- All sessions draw on one usage limit. The default is one ticket at a time.
