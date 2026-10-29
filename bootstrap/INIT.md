# Init: set up a project for agent work

Instructions for an agent. The owner pasted something like:

```text
Read https://github.com/escbch/principles/blob/main/bootstrap/INIT.md and
follow it to set up this project.
```

Your job: turn this folder into a repository where the owner works with agents
as described in [`WORKFLOW.md`](WORKFLOW.md). You interview, then write files,
then set up GitHub, then open the first map. **Nothing leaves this machine
before the owner confirms** (phase 4).

In this file, **kit** means the principles repository you were pointed at
(`escbch/principles` unless the URL names a fork). `{{PRINCIPLES}}` in the
templates is its `owner/repo`.

## Phase 0: Get the kit

```sh
git clone --depth 1 https://github.com/<kit>.git "${TMPDIR:-/tmp}/principles-kit"
```

Read, in this order: `bootstrap/WORKFLOW.md`, `bootstrap/skills.md`,
`bootstrap/ci.md`, then every file in `bootstrap/templates/`. Skim the titles
in `learnings/`; you will link the relevant ones.

## Phase 1: Look before asking

Find out what you can without the owner:

- Is this folder empty, a git repository, or an existing project? Read its
  `README`, manifests (`pyproject.toml`, `package.json`, `Cargo.toml`,
  `go.mod`, …), existing CI and docs.
- `git remote -v`; `gh auth status`; `gh api user --jq .login` (the default
  owner).
- Are the skills installed? See `bootstrap/skills.md` for how to check.
  If not, tell the owner the install command and wait; don't install globally
  without a yes.
- Today's date (decisions are dated).

For an existing project, keep what works. Templates fill gaps; they don't
replace a working README, CI or docs. List every conflict for the owner.

## Phase 2: Interview

Rules:

- Ask **one topic per turn**, with your recommendation and the reason. Use a
  multiple-choice tool if you have one.
- Don't ask what the code or Phase 1 already answered; state it and move on.
- Write the owner's answers down in their words; you need them for the map.

Topics, in order:

1. **Repository.** GitHub owner (default: the logged-in `gh` user), repository
   name, public or private, one-line description, language of docs and issues
   (default English).
2. **User story.** Who uses it, what they want to do, and why:
   *As a … I want … so that …*. Then the **destination**: what is true when the
   first useful version exists. Then what is explicitly **not wanted**.
3. **Stack.** Languages, frameworks, database, frontend or not, how it runs
   (container, binary, static site, script), package managers. Recommend one
   from the user story and say why. A non-code project (research, writing) has
   no stack; skip topics 5 and the CI part of phase 3.
4. **Invariants.** Three to six rules that must never break, and which layer
   owns the rules (e.g. "the backend owns validation; the frontend shows its
   results"). Ask whether the project:
   - records outcomes, analyses trends, or proposes changes: then it follows
     the adaptive loop (`learnings/adaptive-loop.md`);
   - calls LLMs: then "code decides, models propose" is an invariant.
5. **Commands.** The commands that prove a change works: format, lint, type
   check, test, build. Propose the standard ones for the stack.
6. **GitHub.** Confirm: create the repository, labels, branch rules on `main`,
   CI, and the first map issue. Anything the owner wants left out.

Then show a numbered summary of every answer and ask: "Is this right?" Fix
until it is. These become the map's first dated decisions.

## Phase 3: Write the files

Copy `bootstrap/templates/` into the project (including the hidden
`.github/`). Fill every `{{…}}` and `<…>` placeholder, except in the files
that stay templates: `.github/ISSUE_TEMPLATE/*`,
`.github/pull_request_template.md` and `docs/adr/0000-template.md`. Delete
sections that don't apply and the `Init:` comments; keep each file short.
Check that nothing is left:
`grep -rnE '\{\{|<[A-Za-z][^>]*>|Init:' --exclude-dir=.github --exclude=0000-template.md .`
(only real HTML or generics in code may remain).

| File | From |
|---|---|
| `AGENTS.md` | Invariants, owning layer, commands, adaptive-loop and LLM sections only if they apply, links to relevant `learnings/` |
| `<area>/AGENTS.md` | `AGENTS.area.md`, only for areas with their own stack (e.g. `backend/`, `frontend/`) |
| `CLAUDE.md` | As is (`@AGENTS.md`) |
| `CODING_STANDARDS.md` | Owning layer, generated files, test rules |
| `GLOSSARY.md` | Header and sections only; add a term only if the owner used it with a clear meaning in the interview |
| `docs/vision.md` | User story, destination, not wanted |
| `docs/adr/0001-<stack>.md` | The stack choice and why, from `docs/adr/0000-template.md` |
| `docs/agents/*.md` | As is; they configure the skills |
| `.github/ISSUE_TEMPLATE/*` | As is |
| `.github/pull_request_template.md` | As is |
| `README.md` | What it is, how to run it, how to run the checks, link to `AGENTS.md` |
| `.gitignore` | For the stack; always ignore `.env` and keep a `.env.example` if there is configuration |

**Walking skeleton.** For a code project, add the smallest program the stack
allows that runs, has one passing test, and passes lint: e.g. one module and
one test, a lockfile, the linter's config. No features, no folders "for
later". CI needs something real to run.

**CI.** Build the workflows from `bootstrap/ci.md` for the chosen stack: one
workflow per area, path filters, concurrency, time limits, caches, pinned
third-party actions. `bootstrap/ci-examples/` shows the rules applied to
Python and Node; use the same shape for any other stack. Add
`.github/dependabot.yml` for GitHub Actions as `ci.md` describes.

Run every command from topic 5 locally. Everything passes before phase 4.

## Phase 4: Confirm, then GitHub

Show the owner the file tree, and the exact GitHub actions you are about to
take. Wait for a yes. Then:

1. `git init -b main` if needed; one commit: `Set up the project for agent work`.
2. Create the repository if it doesn't exist:
   `gh repo create <owner>/<repo> --<public|private> --description "…" --source . --push`.
   Otherwise push `main`.
3. Run `bootstrap/scripts/setup-github.sh <owner>/<repo>` from the kit. It
   creates the labels, sets merge options, and adds the `main` ruleset. A
   private repository on a free plan can't have rulesets; the script says so
   and goes on. Tell the owner.
4. Watch the first CI run (`gh run watch`). Fix until it's green.

After this, `main` takes changes only through pull requests.

## Phase 5: The first map

Open the first map issue with `.github/ISSUE_TEMPLATE/map.md`, label
`wayfinder:map`:

- **User story** and **Destination** from the interview, in the owner's words.
- **Notes:** constraints and context that came up.
- **Decisions so far:** the confirmed summary from phase 2, one dated line each
  (`- <YYYY-MM-DD>: …`), linking the ADR for the stack.
- **Fog:** every open question you noticed, as a list. Don't answer them.
- **Work packages:** empty. They come from `/wayfinder` sessions.

Don't create work packages now.

## Phase 6: Report

Tell the owner:

1. the repository URL and the map issue URL;
2. files created, and anything kept from an existing project;
3. commands run locally, and the CI result;
4. what the GitHub setup could not do (e.g. rulesets on a free private repo);
5. the next step: `/wayfinder #<map>` to work through the fog.
