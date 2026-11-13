# Design tokens

`tokens.css` is the one source of the design tokens that every app and the
landing page share: the neutral scale, the semantic colours (error, warning,
positive, chart), shape and spacing, in light and dark. App accents are not
here; each app keeps them in its own `app-tokens.css`.

Apps hold **checked copies** (decided in
[escbch/site#38](https://github.com/escbch/site/issues/38)): no package, no
submodule, no build coupling.

| File | Purpose |
|---|---|
| `tokens.css` | The tokens. The first line is the version, `/* tokens v1 */`. |
| `tokens.css.sha256` | The pinned checksum, in `sha256sum` format. |

## Changing the tokens

1. Edit `tokens.css` here, through a pull request.
2. Raise the version line (`v1` to `v2`). Any change to the file raises it.
3. Run `sha256sum tokens.css > tokens.css.sha256` in this folder.
4. Open one pull request per app that updates its copy (below).

## Updating an app's copy

Each app keeps `tokens.css` and `tokens.css.sha256` next to its other theme
files (for example `frontend/src/theme/`), verbatim, plus:

- a test that fails when the copy's SHA-256 differs from the pinned one, or when
  the pin is not the version line's file;
- a script that fetches both files from `main` of this repository, verifies the
  checksum and overwrites the copy (`node scripts/update-tokens.mjs`, or
  `scripts/update-tokens.sh` where there is no Node). Pass a local folder to
  update from a checkout: `... --from ../principles/design`.

Never edit an app's copy by hand: the test fails, and the next update would
overwrite the edit. Load order in the app: `tokens.css`, then `app-tokens.css`.

## What an app's `app-tokens.css` holds

The accent (`--accent`, `--accent-hover`, `--on-accent`, `--offer-ground`,
`--offer-border`, `--focus`) in the same three blocks as here (light, system
dark, explicit dark), and tokens only that app uses.
