# Principles

How I build projects with LLM agents, and what I learned doing it. Anyone may
use it.

| Folder | Holds |
|---|---|
| [`bootstrap/`](bootstrap/) | Set up a new project for this way of working, from one prompt. |
| [`learnings/`](learnings/) | Lessons from real projects that apply beyond the project they came from. |

## Start a new project

Open an agent (Claude Code, Codex, …) in an empty folder, or in an existing
repository, and paste:

```text
Read https://github.com/escbch/principles/blob/main/bootstrap/INIT.md and
follow it to set up this project.
```

The agent interviews you (owner, user story, stack, invariants, commands),
then writes `AGENTS.md`, `GLOSSARY.md`, the docs, issue and PR templates and CI
for your stack, creates the GitHub repository with labels and branch rules,
and opens the first map issue. Nothing is created or pushed before you confirm.

Using your own fork? Replace `escbch/principles` in the prompt; the agent links
your fork from the new project.

## How the work runs afterwards

[`bootstrap/WORKFLOW.md`](bootstrap/WORKFLOW.md): user story and map, decisions,
work packages, implementation, review, and feeding learnings back here.

## License

[MIT](LICENSE): use, copy and adapt freely; keep the copyright notice.
