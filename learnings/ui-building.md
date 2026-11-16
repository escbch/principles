# Building UI

How I design and build screens in all my apps (Personal Coach, Nutrition,
Financial helper, News briefing, and later ones). Learned while building
Personal Coach's load views and charts (2026-10). Nothing here depends on the
domain: swap the examples for each app's own data.

## Shared pieces

Since 2026-11 the pieces every app has (frame and navigation, page header,
buttons, fields, rows, cards, messages, empty, loading and error states) are
shared: [`../design/components.css`](../design/components.css), shown on
[`../design/reference.html`](../design/reference.html), with the rules for
behaviour, wording, dates and numbers in
[`../design/ui-rules.md`](../design/ui-rules.md). Read the rules before
shaping or building a screen. Build a screen from the shared pieces first; add
app CSS only for what the app alone needs.

Learned in a review of five apps (2026-11): 502 screens, 113 findings. The
apps had solved the same six things four or five times (frame, buttons,
fields and validation, rows, error states, deleting), and most findings were
those six again.

## The flow

```text
Talk it through → Decide → Mockup → Small tickets → Check in the real app
```

1. **Talk it through first.** Write the open questions down and answer them
   together. Number the decisions; keep what is still unclear in a short
   "fog" list. No tickets until this round's questions are answered.
2. **Mockup with the app's own styles.** A static page using the real
   stylesheet, at phone width (412 px), sample numbers marked as such, new
   parts outlined. Decide on a picture, not on prose.
3. **Small tickets, in order.** Each ticket brings the API fields it needs and
   the screen on top, with tests, and is merged on green before the next.
4. **Check it in the running app.** Screenshot the real screen at phone width
   on seeded data after every ticket. Tests don't see cut-off text, a glyph
   drawn as a sliver, or chips that wrap badly. Measure the page width
   (`document.documentElement.scrollWidth`) with every form, panel and result
   list open, not only at rest: an overflow often appears only once something
   is open.

## Layout

- Phone first. Wide screens get more room, not a different screen.
- Put the numbers that matter right after the name, so they show without
  scrolling sideways; details follow.
- Tables scroll sideways in their own box, never the page. Leave out a column
  that is empty in every row.
- Long secondary text gets its own line instead of being cut off.
- Chips wrap with a gap, without separator characters.
- Draw small marks (dots, half dots) in CSS; Unicode symbols render
  differently on each device.
- Let fieldsets shrink: `fieldset { min-inline-size: 0 }`. A fieldset's
  default minimum width is its content's, so one input with a button beside it
  can widen a whole phone form past the screen (Vacation Planner, 2026-11: a
  place search pushed a 360 px form to 420 px). Give such inputs
  `flex: 1 1 0; width: 0; min-width: 0`.

- Load base CSS before feature CSS, in the source and in the built file. With
  the base last, its rules beat feature modifiers of the same specificity
  (Financial Helper, 2026-11: a status mark covered the line above it, and
  four button variants never applied).
- A class with a `display` rule overrides the `hidden` attribute. Keep
  `[hidden] { display: none !important }` in the base (landing page, 2026-11:
  a hidden "Log in" link showed while the session was checked).
- Put every rule meant for the phone layout inside its media query (Personal
  Coach, 2026-11: a rule that hides the bottom bar while a field has focus
  also hid the desktop navigation).
- Field text is 16 px or more; smaller text makes iPhones zoom the page on
  focus. A field inside a `label` inherits the label's size unless told
  otherwise.
- A form or message appears where the person tapped: in place of the button
  or row, scrolled into view, with focus. Not at a fixed place on the page
  (Vacation Planner, 2026-11: an edit form opened 3,835 px above the row).
- A row or card that leads somewhere is clickable as a whole. A text link of
  20 px is not a way forward on a phone.

## Charts and colour

- Choose the chart by what the data has to show. "What makes up this total"
  is a stacked bar per row; the same bar works at every level (a whole plan
  split by period, a period split by session, a session split by item).
- Colours come from a small validated palette in a fixed order. A thing keeps
  its colour everywhere; past the palette, the rest share one grey "Other".
- Ordered things (weeks, stages) get one colour from light to dark, not
  different colours. Only about five shades stay tellable apart; past that,
  use one shade. Special cases (a rest or deload period) are grey.
- Check colours with a palette validator against the real background; don't
  judge them by eye.
- Bars in one table share one scale. A target range is a shaded band behind
  the bar.
- Selecting one line highlights it and greys the others.

## Values and words

- Every value is readable without hovering: the table holds the numbers, the
  chart is a visual extra hidden from screen readers, and a tap opens the
  details.
- Add detail to a label only where it is needed, e.g. the day only when two
  items share a name. Don't overload legends.
- Use the domain's own words, the same word for the same thing on every
  screen.
- Problems in a live preview are quiet status messages, never alerts that
  interrupt editing.

## Lists, sorting and filtering

- Default order is by name; ties stay in name order; items without data go
  last.
- When the data behind a sort fails to load, hide the sort and keep the plain
  list working.

## Boundaries

- The backend owns every rule, sum and split; the screen shows and orders what
  it gets. If a screen needs a total, the API provides it.
- New API fields are added, not changed, so existing screens keep working.

## Testing

- Test what a person sees: roles, labels and text, not internals.
- Give background requests a test isn't about standing answers, so each test
  stays about one thing.
- jsdom: `querySelectorAll('a, b')` may not return document order; use
  `:is(a, b)`. For percentages, compute `value * 100 / scale` (not
  `value / scale * 100`) to avoid widths like 14.000000000000002 %.

## Not wanted

- An app-own button, field, row or frame where a shared piece exists.
- A filled button as a selected state, or repeated on every row.
- A server library's own sentence on the screen.
- Building before the open questions are answered.
- Colour as the only carrier of meaning, or values that only show on hover.
- Screens that recalculate domain numbers.
- Legends and labels with more detail than the reader needs.
