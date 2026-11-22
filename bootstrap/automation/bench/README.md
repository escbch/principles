# Bench: which model for which role

Replays tickets that are already merged, to compare models for the builder
and the reviewer on cost, time and result. Every run starts from the same
frozen snapshot, so two models get the same task.

It covers the two roles that cost most. The orchestrator and the shaper need
real sessions and are compared by hand (see "Not covered").

## What a run does

**`build`** — per case, builder model and repetition:

1. A new repository with the base as its only commit. The merged fix is not
   in its history, and the run has no GitHub credentials.
2. The builder builds from the ticket file and `builder.md`, headless.
3. The ticket's commands run on a copy, with the tests of the real merged
   pull request laid over it.
4. One fixed reviewer (the judge, the same for every arm) reviews the branch.
5. If the judge has findings, the builder fixes once, and the commands run
   again.

Accepted, first pass: the builder handed over, the commands pass and the
judge has no `must-fix`. Accepted: the commands pass after the fix round. The
fix is not reviewed a second time.

**`review`** — per known commit, reviewer model and repetition: the reviewer
reviews a commit in which a real review found defects. A grader model then
marks which of the known defects the review names, and counts `must-fix`
findings beyond them. Those are not always false alarms: read them.

**`report`** — writes `summary.md` and `runs.csv` from all finished runs.

## Prepare the cases

1. Pick six to eight merged tickets of different kinds.
2. Copy [`cases.example.toml`](cases.example.toml) to a folder outside this
   repository and fill it in. `base` is the merge commit's first parent:
   `git rev-parse <merge>^1`.
3. Save each ticket with its comments as a file, and remove the pull
   request's link and anything written after the build began.
4. For `review`: take the commit the builder handed over before the fix
   round, and write one line per defect the real review found. If the branch
   was older than the merge's first parent (the default branch was merged
   in later, or it was stacked), give that review its own `base`:
   `git merge-base <commit> <merge>^1`. A commit the real review passed, with
   an empty `known`, is a control: every `must-fix` on it counts as extra.
5. List as `hidden` only tests that go through what the ticket names (a
   route, a field, a file). A test that calls a function the builder was free
   to name fails every arm.
6. Run `verify` (below) until every line says "as it should".

## Run

```sh
B=bootstrap/automation/bench/bench.py
python3 $B verify ~/bench/cases.toml   # no model: checks pass on the merged commit, hidden tests fail on the base
python3 $B build  ~/bench/cases.toml --builders claude-haiku-5-5,claude-sonnet-5-5,claude-opus-5-5 --judge claude-opus-5-5:medium
python3 $B review ~/bench/cases.toml --reviewers claude-sonnet-5-5,claude-opus-5-5:medium,claude-opus-5-5:high
python3 $B report
```

- Three repetitions by default (`--reps`). One run per model says little: the
  same model on the same ticket differs from run to run.
- Runs go one after the other, arms shuffled inside each repetition. All of
  them draw on one usage limit.
- A finished run is kept. After a stop (two failures in a row, a usage limit,
  Ctrl-C) the same command continues.
- Results land in `~/automation-bench` (`--out <dir>` before the subcommand).
  Keep that folder outside every repository, or the runs read its
  `AGENTS.md`.

## Read the result

- **USD per accepted ticket** is the number to compare builders by: all the
  builder's cost, fix rounds and failed runs included, divided by the tickets
  that were accepted.
- USD is the list price that `claude -p` reports for the tokens used. On a
  subscription nothing is charged; it still compares the arms.
- Compare per case, along a row of the second table. A model that is cheaper
  on the median but fails the hard case shows there.
- Each run's folder holds `steps.json` (every reply, cost and token count),
  the check results and `diff.patch`.

## Limits

- **The runs execute commands on this machine without asking** (`Bash` is
  allowed). Use cases from your own repositories only, and a machine or
  container without secrets you would mind a model reading.
- Headless runs are not desktop sessions: no messages between sessions, no
  push, no pull request, no CI, no screenshots branch. Cost and time are
  close to a real builder's, not equal.
- A ticket that needs a running app with a database works only if the
  builder can start it from the checkout.
- The models may have seen a public repository's merged fix in training.
  Prefer recent tickets and private repositories.
- The grader is a model. Check a few of its verdicts in `steps.json` before
  trusting the "known defects found" column.

## Not covered

- **Orchestrator:** with the best builder and reviewer fixed, run the same
  three tickets once per orchestrator model as real sessions. Count from its
  log: wrong base, a review not forwarded in full, a missed stop rule, and
  its own cost.
- **Shaper or architect:** let each model draft work packages from the same
  decisions, then run `build` on every draft with one builder. Compare the
  `BLOCKED` share, `must-fix` and builder cost, and how much you changed
  before labelling.
