# Shared UI rules

The rules every app and the landing page follow, beyond the tokens. Decided
with the owner on 2026-11-16 after a review of all apps
([escbch/site#52](https://github.com/escbch/site/issues/52)). The picture is
[`reference.html`](reference.html); the classes are in
[`components.css`](components.css). This file holds what a stylesheet cannot:
behaviour, wording, dates and numbers.

Scope: the pieces every app has. An app keeps its accent, composes its own
screens and owns its domain pieces (charts, a workout screen, a budget table).
A domain piece is built from the tokens and, where it contains one, from the
shared pieces.

## Frame

- Every app has a top bar (56 px, not sticky) with the app name at its start.
  Its end holds one icon button, "Alle Apps" / "All apps" (a 2 × 2 grid), that
  opens the landing page. The address comes from the app's configuration.
- Main navigation has 2 to 5 fixed places. Under 900 px it is a bar fixed to
  the bottom (icon over label, 56 px plus the phone's safe area). From 900 px
  the same links sit in the top bar as text. More than 5 places: show 4 and
  "Mehr" / "More", at both widths.
- A place's label is one short word. A label that does not fit the bottom
  bar breaks at a syllable with a hyphen ("Einstellun-gen"); it is never cut
  at any letter. This needs `<html lang>`.
- A list the person grows (categories) or an app's sub-sections is a side
  list: a 240 px column from 900 px, a drawer under 900 px, opened by a menu
  button at the bar's start.
- One breakpoint: 900 px. Rules for the phone layout sit inside
  `@media (max-width: 56.24rem)`, never outside a media query.
- The bottom bar hides while a text field has focus (phone layout only).
- Bar and page share one width (1080 px) and one left edge. Forms and running
  text stay 720 px wide (`.measure`). A workspace app (a list beside an
  editor) may use up to 1600 px (`.app-full`). Gutter: 16 px under 900 px,
  24 px from 900 px.
- The drawer closes on Escape, on its backdrop and after a choice. Focus
  returns to the menu button. Nothing behind the open drawer can be reached
  (`inert`).

## Page

- Optional back link above the title: a chevron and the name of the place it
  leads to. No "Zurück zu".
- One `h1` per page, in every state (loading, error, empty). At most one main
  button beside it: the page's add action.
- The browser title is "Seite · App". `<html lang>` follows the chosen
  language. After a route change, focus moves to the `h1`.

## Buttons and links

- One size: at least 44 px high, radius 10 px, weight 600. Width follows the
  text; the main button of a form is full width under 480 px.
- **Main** (filled): exactly one per view or form. Never a selected state,
  never repeated per row.
- **Secondary** (outlined, text in the accent): every other action.
  **Quiet** (text only): the least important action of a row.
- **Destructive** (red outline): only for an action that loses data.
- A selected view or filter is a tinted pill with an accent border
  (`.segmented`), never filled. The control takes links, buttons or radio
  inputs inside labels; the stylesheet hides the radio and shows its focus on
  the pill.
- Order: the main action first, "Abbrechen" after it.
- A disabled button looks disabled, and the reason stands beside it. Prefer an
  enabled button that answers the tap with the reason.
- A link that stands alone is 44 px high (`.link`, `.back-link`). Small links
  exist only inside a sentence. An add action is a button, not a link.

## Forms

- Label above the field, hint below. Field text is 16 px, never smaller
  (smaller text makes iPhones zoom the page on focus).
- Optional fields say "(optional)". There is no star for required fields.
- Short related fields share one line where the row has room for two fields
  (two times 9rem and the gap, about 300 px); below that they stack (amount
  and unit).
- The button that submits a form never has the label of the button that
  opened it. "Eintrag hinzufügen" opens a form; its submit reads "Eintrag
  speichern".
- Validation: the submit button stays enabled and the form is `noValidate`.
  On submit the message appears under its field in the person's words, the
  field gets `aria-invalid` and a red border, and focus moves to the first
  wrong field. No browser bubbles, no silently disabled button.
- The backend answers a refused value with a stable code; it may name the
  field as well. Where it sends the code only, each form maps its codes to
  its fields. That map is display knowledge (which input shows a code), not a
  rule of the domain. The sentence is written in the app's message file, in
  both languages. A server library's own sentence never reaches the screen.
  Example: the code `name_too_long` shows its sentence under the field
  "Name", because the form that has that field says so.
- A failed save shows under the form's buttons, in the error colours, with
  "Erneut versuchen". What was typed stays.
- A form that opens in place replaces the button that opened it, scrolls into
  view and takes focus in its first field. Closing returns focus to that
  button. Escape cancels. The code sets that focus itself: Safari does not
  focus a button on click, so "the element that had focus" is not the button
  there.
- Checkbox and radio: a 20 px box in a 44 px row, one option per line.

## Lists

- A list is one box with divider lines. A row: title, at most one muted line,
  the figure or date at the end. A figure is never cut; a preview of longer
  text may end after two lines.
- A row's date stands at the row's end. A date and time that can be a range
  ("16.11.2026, 07:20 bis 08:00") may stand in the muted line instead,
  because the row's end does not shrink.
- A chip at a row's end does not shrink or break; beside it a title may take
  two lines on a narrow phone. A chip that holds a name a person typed
  carries `.chip-wrap` and may break its text; every other chip stays on one
  line.
- What belongs to a row but does not fit its line stands in `.row-below`
  under it.
- A row carries at most one visible action. The others open from one "…"
  button named "Weitere Aktionen für <Ding>": editing first, deleting last.
- A row that shows a text action uses the variant `.row-wrap`; under 900 px
  the action and "…" stand on a second line.
- The row menu opens in the page under its row, and focus moves to its first
  entry (Enter on "Weitere Aktionen für Haferflocken" puts focus on
  "Bearbeiten"). It closes on Escape (focus
  returns to the "…" button), on a press outside and after an action. One menu
  is open at a time.
- A row that leads somewhere is one link as a whole, at least 56 px high, with
  no button inside it. Its accessible name is its whole visible content, not
  the title alone.
- The accessible name of a control starts with its visible text
  ("Auswählen: Banane", not "Banane wählen").

## Deleting

- What cannot come back asks first, in place of the row or under the button:
  a question that names the thing, one sentence with the consequence (in
  numbers where there is one), a filled red button that repeats the verb, and
  "Abbrechen". Opening it moves focus to it; "Abbrechen" and Escape return
  focus.
- What can come back (archive, trash, untick) happens at once.
- An overlay (native `dialog`) only where the person must answer before
  anything else: leaving unsaved changes, a save conflict.

## States and messages

- The page keeps its header and navigation in every state.
- **Loading:** grey lines in the shape of the content (`.skeleton`) with
  "Wird geladen …" for screen readers. Old content stays during a reload.
- **Load error:** what could not be loaded, what to do, always "Erneut
  versuchen"; the technical detail small. Never the empty text.
- **Empty:** what is empty, one sentence on what to do, the add button. If
  the add button stands on the heading line directly above the block, it is
  not repeated inside.
- **Unknown address, not allowed:** the same block with a link to the app's
  start. No dead ends.
- A message appears where its cause is. No toasts, no bar stuck to the window.
  "Gespeichert" is a quiet line beside the control.
- When an action removes its row from the list (archive, restore, delete), a
  list item with the message stands where the row was. The fifth of nine notes
  is moved to the trash; the fifth item now reads
  "„Router: Portfreigabe“ liegt im Papierkorb."
- A success message stays until the person's next action in the same list or
  section, or until the view, the sort or the filter changes. It is not timed
  and has no close button.
- One message per list or section: a second result replaces the first, also
  when both are failures.
- Colour plus a mark plus words; colour is never the only carrier.
- A part that opens in place always shows that it opens (`.disclosure`).

## Language and theme

- Every app offers German and English. Texts live in a message file per
  language, never inline in a screen; plurals go through the message
  functions.
- Language and theme are chosen once for the site, on the landing page, and
  stored in the browser for the site's domain. Default: the browser's language
  if German or English, else English; the system's theme. Each app applies
  both before its first paint and has no control of its own.
- Every app has its own accent, from one validated set
  ([`accents.css`](accents.css)); the stylesheet never names a colour. The
  focus ring is the same amber in every app.

## Dates and numbers

They follow the app's chosen language, not the browser's, through one function
per kind. No screen formats on its own, and no raw API string reaches it.

| Kind | Deutsch | English |
|---|---|---|
| Date, short (same year) | 16.11. · Mo., 16.11. | 16 Nov · Mon 16 Nov |
| Date, default | 16.11.2026 | 16 Nov 2026 |
| Date, long (a day's heading) | Montag, 16. November 2026 | Monday 16 November 2026 |
| Range | 02.–22.11.2026 | 2–22 Nov 2026 |
| Date and time | 16.11.2026, 07:20 | 16 Nov 2026, 07:20 |
| Month | Oktober 2026 | October 2026 |
| Number with unit | 2.511 kcal · 87,5 kg · 86 % | 2,511 kcal · 87.5 kg · 86% |
| Money | 1.229,07 € · −1.146,87 € | €1,229.07 · −€1,146.87 |

- English is written day first with the 24-hour clock.
- A no-break space stands between a number and its unit. Minus is the minus
  sign (U+2212), not a hyphen.
- A comparison is said in words ("171 € weniger als im Schnitt"), not with a
  sign.
- A number field shows a value the way the screen shows it ("68,50") and
  accepts comma and point.

## Wording

One word per action in every app. German addresses the person as "du". Labels
are capitalised. A button names its thing when a page has several forms
("Wiegung speichern"), otherwise the bare verb. Errors say what happened and
what to do, without codes and without "leider".

| Use | Deutsch | English |
|---|---|---|
| Keep changes | Speichern | Save |
| Leave a form | Abbrechen | Cancel |
| New thing | Hinzufügen · Neue Notiz | Add · New note |
| Change a thing | Bearbeiten | Edit |
| Gone for good | Löschen | Delete |
| Out of a list, the thing stays | Entfernen | Remove |
| Put away, can come back | Archivieren · Wiederherstellen | Archive · Restore |
| After a failure | Erneut versuchen | Retry |
| Loading | Wird geladen … | Loading… |
| Load failed | Die Notizen konnten nicht geladen werden. Prüfe die Verbindung und versuche es erneut. | Couldn’t load the notes. Check your connection and retry. |
| Save failed | Das konnte nicht gespeichert werden. Deine Eingaben sind noch da. | Couldn’t save. What you typed is still here. |
| Saved | Gespeichert | Saved |
| Empty list | Noch keine Notizen. | No notes yet. |
| Confirm a delete | „Technik“ löschen? Das lässt sich nicht rückgängig machen. | Delete “Technik”? This can’t be undone. |
| Unknown address | Diese Seite gibt es nicht. | This page doesn’t exist. |

## Technical

- Load order: `tokens.css`, `app-tokens.css`, `components.css`, then the app's
  own CSS. Base rules must come before feature rules, in the source and in the
  built file.
- Focus ring: 3 px solid `--focus`, offset 2 px. No outline on a heading that
  only receives focus for screen readers.
- Icons: the inline SVG set in [`icons.svg`](icons.svg) (24 px, stroke 2,
  current colour). No emoji and no Unicode marks as controls.
- No web fonts, no assets from another origin.
- An app's installed icon keeps its picture and has the app's accent as its
  ground. The browser's toolbar colour (`theme-color`) is the top bar's
  surface colour, one value for light and one for dark
  (`media="(prefers-color-scheme: dark)"`), never the accent.
- Every app works in Safari (iPhone, iPad, Mac) as well as in Chrome and
  Firefox. A behaviour that differs there is a defect.
- A scroll box (table, wide figure) is reachable by keyboard (`tabindex="0"`
  and a name).
- Page wrappers carry no colour rules; a class name is used for one thing.
