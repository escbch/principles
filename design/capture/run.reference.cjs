/*
 * Example, and the check for a change to the shared pieces: captures the
 * reference pages of this repository.
 *
 *   cd design && python3 -m http.server 5180 --bind 127.0.0.1   # one terminal
 *   cd design/capture && npm ci && node run.reference.cjs        # another
 *
 * Every line of the output must read overflow412=false, small=0/…, axeL=-,
 * axeD=-, focusMissing=0 (or -), ext=0, console=0. One known exception: the
 * screens "reference" and "reference-blue" read small=2/… because the 44 px
 * target of button.chip is a pseudo-element, which the script does not count.
 */
const path = require('node:path')
const { run } = require('./shoot.cjs')

run({
  app: 'reference',
  base: 'http://127.0.0.1:5180',
  out: path.join(__dirname, 'out'),
  locale: 'de-DE',
  only: process.argv.length > 2 ? process.argv.slice(2) : undefined,
  screens: [
    { name: 'reference', path: '/reference.html' },
    { name: 'reference-blue', path: '/reference.html', prepare: async (page) => { await page.selectOption('#accent', 'blue') } },
    { name: 'notes-entries', path: '/example-notes.html' },
    { name: 'notes-drawer', path: '/example-notes.html', skipFocus: true, prepare: async (page, { viewport }) => { if (viewport.width < 900) await page.click('#menu') } },
    { name: 'notes-entry', path: '/example-notes.html#/e/1' },
    { name: 'app', path: '/example-app.html' },
  ],
})
