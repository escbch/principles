# Fast CI: install only what's missing

Learned in Personal Coach (2026-10): the Playwright end-to-end job took about
12 minutes, and almost all of it was one install step.

## What happened

- `npx playwright install --with-deps chromium` also runs `apt-get` to install
  system libraries and fonts. On GitHub's Ubuntu runner this meant package
  updates from a slow mirror: 5 to over 10 minutes, different every day.
- A headless test run needs only Chromium's headless shell, and the runner
  image already has the system libraries it uses.
- The fix was one line: `npx playwright install chromium --only-shell`. The job
  went from about 12 minutes to about 1 minute.

## Rules

- **Read the step timings first.** One step usually takes most of the time;
  fix that one.
- **Don't apt-install what the runner already has.** Check the runner image's
  software list before adding system packages or `--with-deps`. Add a package
  only when a run fails without it, by name, with `--no-install-recommends`,
  and without upgrading the rest.
- **Install the smallest thing that works:** one browser, the headless
  variant, not "all".
- **Cap every job** with `timeout-minutes`, so a slow mirror fails fast instead
  of using up minutes.
- **Run only what changed:** `paths:` filters per workflow, and `concurrency`
  with `cancel-in-progress` so a newer push stops the older run.
- **Pull container images from a mirror** (`mirror.gcr.io/library/...`) to
  avoid Docker Hub rate limits.

## Not wanted

- Install steps copied from a tutorial without checking what the runner
  already provides.
- Jobs without a time limit.
