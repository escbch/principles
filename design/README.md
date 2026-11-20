# Design: tokens, shared pieces, rules

What every app and the landing page share, in four parts:

| File | Purpose |
|---|---|
| `tokens.css` | The design tokens: neutral scale, semantic colours (error, warning, positive, chart), shape, spacing and the backdrop (`--scrim`), in light and dark. The first line is the version, `/* tokens v2 */`. |
| `components.css` | The shared pieces, built only on the tokens: base rules, app frame and navigation, page header, buttons, links, form fields, list rows and row menu, cards, chips, messages, empty, loading and error states, confirmation. The first line is the version, `/* components v2 */`. |
| `ui-rules.md` | What a stylesheet cannot carry: behaviour, wording, dates and numbers. Read it before shaping or building a screen. |
| `reference.html` | The picture: every shared piece with its rules, in light and dark and with two accents. `example-notes.html` (side list, entry list, entry form) and `example-app.html` (main navigation) show whole frames. Open them from a checkout; they load the files beside them. |
| `icons.svg` | The shared icon set as SVG symbols. |
| `app-tokens.example.css` | An example accent for the reference pages. |
| `accents.css` | The accent of every app as its full token group, light and dark, and two spares. The source an app copies its block from. |
| `capture/` | The script that screenshots and measures every screen of an app the same way, and the check for a change to the shared pieces ([`capture/README.md`](capture/README.md)). |
| `*.sha256` | The pinned checksum of `tokens.css` and of `components.css`, in `sha256sum` format. |

Each app keeps its accent in its own `app-tokens.css`; the values come from
`accents.css`.

Apps hold **checked copies** of `tokens.css` and `components.css` (decided in
[escbch/site#38](https://github.com/escbch/site/issues/38) and
[escbch/site#52](https://github.com/escbch/site/issues/52)): no package, no
submodule, no build coupling. Markup and behaviour stay in each app.

## Changing the tokens or the shared pieces

1. Edit the file here, through a pull request. A change to a shared piece
   comes with its picture: update `reference.html` in the same pull request,
   and `ui-rules.md` if a rule changes. Run `capture/run.reference.cjs` and
   say in the pull request that every line passes.
2. Raise the file's version line (`v1` to `v2`). Any change to the file raises
   it.
3. Run `sha256sum tokens.css > tokens.css.sha256` or
   `sha256sum components.css > components.css.sha256` in this folder.
4. Apps take the new version with their next ticket that touches screens, as
   that ticket's first step; its pull request names the versions it moved from
   and to. There is no pull request that only updates a copy, unless the
   version fixes a defect the owner wants gone at once. Apps may be on
   different versions for a while. A rule in an app that the new version makes
   unnecessary is deleted in the pull request that takes it.

`components.css` holds no colour literal and no app class. A piece only one
app needs stays in that app.

## Updating an app's copy

Each app keeps `tokens.css`, `components.css` and their `.sha256` files next
to its other theme files (for example `frontend/src/theme/`), verbatim, plus:

- a test that fails when a copy's SHA-256 differs from the pinned one, or when
  the pin is not the version line's file;
- a script that fetches the files from `main` of this repository, verifies the
  checksums and overwrites the copies (`node scripts/update-tokens.mjs`, or
  `scripts/update-tokens.sh` where there is no Node). Pass a local folder to
  update from a checkout: `... --from ../principles/design`.

Never edit an app's copy by hand: the test fails, and the next update would
overwrite the edit.

Load order in the app: `tokens.css`, `app-tokens.css`, `components.css`, then
the app's own CSS. Base rules must come before the app's rules in the built
file too.

## What an app's `app-tokens.css` holds

The accent (`--accent`, `--accent-hover`, `--on-accent`, `--offer-ground`,
`--offer-border`, `--focus`) in the same three blocks as `tokens.css` (light,
system dark, explicit dark), and tokens only that app uses. Every app has its
own accent, different from every other app's.

## Theme before first paint under a strict CSP

The apps serve `Content-Security-Policy: default-src 'self'`, which blocks
the inline script that applies the theme and language before the first paint.
Do not weaken the policy. Put the script in a same-origin file and load it with
a plain render-blocking `<script src>` in `<head>` (no `async`, `defer` or
`type="module"`), before the stylesheets. The landing page (`prefs-head.js`)
and Vacation Planner (`public/theme-init.js`) do this.

## Adopting the shared pieces in an app

An app replaces its own rules piece by piece; until a piece is replaced, the
app's rule stays. When a piece is adopted, the app's own rule for it is
deleted in the same pull request. `components.css` styles a few bare elements
(`body`, `h1` to `h3`, `a`, `fieldset`); the app's CSS loads after it and wins
where both set the same thing.

## Accents

`accents.css` holds one block per app (decided in escbch/site#52 on
2026-11-17) and two spares. It is not loaded by any page: an app copies its
block into its `app-tokens.css`. Every group was measured against the token
values in both themes: at least 4.5 to 1 for accent text on surface, raised
surface (`--surface-raised`), ground and tinted ground and for text on the
accent and its hover; at least 3 to 1 for the focus ring on surface and
ground. The six accents in use stay at least 7 apart (OKLab distance times
100) with full, green-weak and red-weak colour vision. A new app takes a
colour that keeps that distance to every accent in use; a spare replaces only the colour named beside it.
