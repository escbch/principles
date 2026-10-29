# CI for any stack

How to build a project's GitHub Actions from its stack. The rules come from
[`../learnings/ci-speed.md`](../learnings/ci-speed.md); read it first.
[`ci-examples/`](ci-examples/) shows them applied to Python, Node, Playwright
and Docker images in a real project. Use the same shape for Rust, Go or
anything else.

## Every workflow

- **One workflow per area** (`backend-ci.yml`, `frontend-ci.yml`, `e2e.yml`,
  `images.yml`), so a change in one area doesn't run the others.
- **Path filters** on `pull_request` and `push` to `main`: the area's folder,
  minus its `*.md`, plus the workflow file itself. Docs-only changes run
  nothing.
- **`workflow_dispatch`**, so a run can be started by hand.
- **`permissions: contents: read`** at the top. Grant more per job, only where
  needed (`packages: write` to publish images).
- **Concurrency:** `group: ${{ github.workflow }}-${{ github.ref }}` with
  `cancel-in-progress: true`.
- **`timeout-minutes` on every job**: about twice its normal duration (15 for
  checks, 20 for e2e and images).
- **Few jobs.** Each job is billed as at least one minute and repeats checkout
  and setup. Put lint, type check, build and tests in one job, quick checks
  first, so a lint error fails in seconds.
- **Cache dependencies** by lockfile, and install with the locked mode
  (`uv sync --locked`, `npm ci`, `cargo … --locked`, `go mod download`).
- **Pin third-party actions by commit SHA** with the version in a comment
  (`uses: astral-sh/setup-uv@<sha> # v10.1.0`). `actions/*` and `docker/*` may
  use a major tag.
- **Container images from a mirror:** `mirror.gcr.io/library/postgres:18`, not
  `postgres:18`. Docker Hub rate-limits shared runners.
- **Upload reports only on failure**, with `retention-days: 7`.
- **Comment the why** above any step that isn't obvious, like the examples do.

## Branch rules and path filters

Don't make path-filtered workflows *required* status checks: a PR that skips
one waits forever for a check that never runs. The `main` ruleset requires a
pull request, not checks. If required checks are wanted later, add one small
`ci-gate` job that always runs and waits for the others, and require only that.

## Per stack

Pick the lines for the chosen stack. Versions come from the project's own
files (`.python-version`, `.nvmrc`, `rust-toolchain.toml`, `go.mod`), never
hard-coded in the workflow.

| Stack | Setup and cache | Checks, in order |
|---|---|---|
| Python | `astral-sh/setup-uv` with `enable-cache` and `cache-dependency-glob: <area>/uv.lock`; `uv python install` | `uv sync --locked`, `ruff format --check`, `ruff check`, type check if used, `pytest` |
| Postgres / migrations | `services: postgres` from the mirror, health check | Create test DB with `docker exec … psql` (no client install), apply migrations, check model drift (`alembic check`) |
| Node | `actions/setup-node` with `node-version-file: .nvmrc`, `cache: npm` | `npm ci`, generated-contract check, lint, build, test |
| Rust | `dtolnay/rust-toolchain` (reads `rust-toolchain.toml`), `Swatinem/rust-cache` | `cargo fmt --check`, `cargo clippy --locked --all-targets -- -D warnings`, `cargo test --locked` |
| Go | `actions/setup-go` with `go-version-file: go.mod` (caches by default) | `gofmt -l` (fail if output), `go vet ./...`, `golangci-lint` action, `go test -race ./...` |
| Playwright | Install the browser with `npx playwright install chromium --only-shell`, **never** `--with-deps` | Run the journey; upload the report on failure |
| Docker images | `docker/setup-buildx-action` with the BuildKit image from `mirror.gcr.io/moby/buildkit`; `cache-from/to: type=gha` | PRs build and smoke-test only when packaging changes; `main` builds, smoke-tests and pushes `main` and `sha-<short>` tags to GHCR (owner and name lower-case) |
| Static site / docs | The site generator's setup action with cache | Build, link check |

For a stack not in the table: find its official setup action and cache, its
locked install, and its format, lint and test commands. Apply every rule above.

## Dependabot for actions

Pinned SHAs go stale. Add `.github/dependabot.yml`, grouped, so it opens one PR
a month:

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: monthly
    groups:
      actions:
        patterns: ['*']
```

Add the project's own package ecosystems the same way only if the owner wants
dependency PRs.

## After the first run

Read the step timings (`gh run view <id>`). If one step takes most of the time,
fix that one, and if the lesson is new, add it to `learnings/`.
