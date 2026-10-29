---
name: Work package
about: A self-contained piece of work an agent builds in one PR, without the chat
title: "<What the user can do, e.g. 'Record cardio bouts during a workout'>"
labels: enhancement
---

Part of #<map> (<phase or part>). Decided on <YYYY-MM-DD>: <links to the decisions>.

# Requirements

## Problem
<Why this matters, in 2–4 sentences. What exists today that it builds on.>

## User story
As a <who>, I want <the slice this package delivers>, so that <why>.

## Definition
- **<Term>:** <exact rule, including what is excluded>.
- <Calculations: formula, rounding, minimums, null cases and why.>
- <Derived or stored? Which layer owns it?>
- Example: <a worked case with real values>.

## Acceptance criteria
- [ ] <Observable behavior, including edge cases.>
- [ ] `docs/<domain>.md` (<section>) defines <…>; `GLOSSARY.md` gains *<Term>*.

# Implementation guidance

**<Layer 1, e.g. backend>:**
- <File or service to add or change, and what it does.>
- <Migration: what it does; never edit a merged migration.>

**<Layer 2, e.g. frontend>:**
- <What the user sees, with exact texts where they matter.>
- Display only; rules stay in <owning layer>.

<Generated files to regenerate, and with which command.>

# Testing guidelines
- <Level (unit, integration, end-to-end)>: <what to cover, including each rule in the Definition and its edge cases>.
- Run: `<command>`, `<command>`, `<command>`.

# Out of scope
- <What not to build now, and where it goes instead (#<n>).>

# Context
- <Files, services, pages, related issues, ADRs.>

---
<!-- Before labelling ready-for-agent:
- [ ] Says Part of #<map>; links its decisions.
- [ ] Every rule is exact, with an example and the edge cases.
- [ ] Implementation guidance names the layers, files or services.
- [ ] Acceptance criteria are observable, including doc and glossary updates.
- [ ] Testing guidelines list the tests and the exact commands.
- [ ] Out of scope is listed.
- [ ] An agent could build it without the chat that produced it. -->
