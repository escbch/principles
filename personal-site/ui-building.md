# Building UI

How I design and build screens in all my apps (Personal Coach, Nutrition,
Financial helper, News briefing, and later ones). Learned while building
Personal Coach's load views and charts (2026-10). Nothing here depends on the
domain: swap the examples for each app's own data.

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
   drawn as a sliver, or chips that wrap badly.

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

- Building before the open questions are answered.
- Colour as the only carrier of meaning, or values that only show on hover.
- Screens that recalculate domain numbers.
- Legends and labels with more detail than the reader needs.
