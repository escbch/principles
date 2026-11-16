# Capture: screenshot and measure every screen the same way

One script for "check it in the running app"
([`../../learnings/ui-building.md`](../../learnings/ui-building.md), step 4),
for the screenshots a pull request that changes a screen attaches, and for a
review across apps. It was written for the UI review of 2026-11
([escbch/site#52](https://github.com/escbch/site/issues/52)): 5 apps, 502
screens, all measured alike.

| File | Purpose |
|---|---|
| `shoot.cjs` | Captures each screen at 412 px and 1280 px, light and dark, full page, and measures it. |
| `compare.py` | Prints the measurements of several apps side by side. |
| `run.reference.cjs` | An example, and the check for a change to the shared pieces: captures this repository's reference pages. |

## What it measures, per screen

- horizontal page overflow (`scrollWidth` against the window), at both widths;
- interactive targets under 44 px, with their text and size;
- the different button and field styles (height, radius, font, colours), headings, navigation, page width, tables, lists, dialogs, status and alert texts;
- axe rules in light and dark (needs `axe-core`);
- focus: the first 15 tab stops, and which of them show no indicator;
- console errors, failed requests, and every request to another origin.

Output: `<out>/shots/<name>--<width>--<scheme>.png` and `<out>/measure.json`.

## Use

```sh
cd design/capture
npm ci                      # axe-core; without it the axe rules are skipped
```

Playwright must be resolvable (`require('playwright')`). Where it is installed
globally with its browser, do nothing; elsewhere `npm install --no-save
playwright` and `npx playwright install chromium`.

Write a small run file **outside the app's repository** and call `run()`; the
header of `shoot.cjs` lists every option:

```js
const { run } = require('<path to principles>/design/capture/shoot.cjs')
run({
  app: 'notes',
  base: 'http://127.0.0.1:5173',
  out: '/tmp/notes-shots',
  locale: 'de-DE',
  screens: [
    { name: 'inbox', path: '/' },
    { name: 'inbox-drawer-open', path: '/', prepare: async (page, { viewport }) => { if (viewport.width < 900) await page.getByRole('button', { name: 'Kategorien öffnen' }).click() } },
    { name: 'inbox-empty', path: '/', route: async (page) => page.route('**/api/categories/*/entries', (r) => r.fulfill({ json: [] })) },
    { name: 'inbox-loading', path: '/', route: async (page) => page.route('**/api/categories/*/entries', () => {}), settle: 800 },
    { name: 'inbox-error', path: '/', route: async (page) => page.route('**/api/categories/*/entries', (r) => r.fulfill({ status: 500, body: '{}' })) },
  ],
})
```

Compare apps: `python3 compare.py <out of app 1> <out of app 2> …`.

## Rules

- Run the app locally on seeded or invented data, never on production. Never
  capture real personal or financial data.
- Capture every route, and as separate screens every open state (form, panel,
  menu, drawer), one form after a failed submit, and the empty, loading and
  error state of each list. A width problem often shows only once something is
  open.
- Name screens in English, kebab-case, with the state as a suffix
  (`diary-entry-edit-open`, `plan-error`).
- Look at the screenshots. Do not report a visual finding from `measure.json`
  alone, and do not report one you have not seen.
- Screenshots of private apps never go into this repository; it is public.
  Each app's own repository says where pull-request screenshots live.

## Known limits

- In a full-page screenshot a bar fixed to the bottom is drawn once, at the
  first window's bottom edge, over the content. Crop to the first 915 px to
  see the screen as a phone shows it.
- The headless browser shows native date and time fields in US format whatever
  the language. That is not a finding about the app.
- The tab stop on the calendar button inside a native date field is reported
  as "no focus indicator"; the browser draws its own ring there.
- A very long run can lose its browser. Pass `only: [...]` and run the screens
  in batches of about 8; `measure.json` is merged across runs.
- The focus check only tabs through the first 15 stops of the page at rest. It
  does not test where focus goes when a form opens or closes; check that by
  hand or in a test.
