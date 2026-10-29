# Skills

The workflow runs on [mattpocock/skills](https://github.com/mattpocock/skills).
Install one way per agent; both together load every skill twice.

## Install

- **Claude Code:**
  `claude plugin install mattpocock-skills@claude-plugins-official`
  (updates itself).
- **Any agent, user-wide:** `npx skills@latest add mattpocock/skills -g -y -s '*'`.
  Update with `npx skills@latest update -g -y`.
- **Cloud sessions:** install into the repository instead (drop `-g`), so every
  session has them. Commit the result.

**Check:** the skills are installed if `~/.agents/skills/wayfinder/SKILL.md`,
`~/.claude/skills/wayfinder/SKILL.md` or `.agents/skills/wayfinder/SKILL.md`
exists, or `/wayfinder` is offered as a command.

## Used by the workflow

Install all of them; these are the ones [`WORKFLOW.md`](WORKFLOW.md) relies on.
If one is renamed or removed upstream, update this list and `WORKFLOW.md`.

| Skill | Used for |
|---|---|
| `setup-matt-pocock-skills` | Not needed after Init: `templates/docs/agents/` already holds its output |
| `wayfinder` | Chart a map; work one fog ticket per session |
| `grilling`, `grill-with-docs`, `grill-me` | One question at a time, with a recommendation |
| `domain-modeling` | Writes `GLOSSARY.md` terms and ADRs |
| `to-tickets`, `to-spec` | Write work packages (in the format from `AGENTS.md`) |
| `triage` | Sort incoming ideas with the triage labels |
| `implement`, `implement-spec`, `tdd` | Build a work package |
| `code-review` | Review the diff before the PR |
| `research`, `prototype` | Answer fog that needs facts or a picture |
| `diagnosing-bugs` | Hard bugs |
| `handoff` | Continue in a fresh session |
| `retro` | Look back; send learnings to principles |

## Labels the skills expect

Created by [`scripts/setup-github.sh`](scripts/setup-github.sh):

- triage: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`,
  `wontfix`;
- wayfinder: `wayfinder:map`, `wayfinder:grilling`, `wayfinder:research`,
  `wayfinder:prototype`, `wayfinder:task`.
