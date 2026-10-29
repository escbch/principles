# Coding Standards

Read by `/code-review` when it reviews a diff. Implementation agents don't need
to load this file. Keep only judgement calls here: anything a linter, type
checker or CI job can enforce belongs there instead.

## Changes

- Prefer explicit, typed, small, reviewable changes.
- Preserve existing behavior unless the work package changes it. No drive-by
  refactors.
- No speculative abstractions, parameters or dependencies without a need the work
  package states.
- Name things with `GLOSSARY.md` terms; never with a synonym it lists under
  `_Avoid_`.

## Layers

- Domain rules live in <owning layer>. <Other layers> present its contracts and
  don't re-implement its validation or calculations.
- Generated files (<contract, schema types, lockfiles>) change only through
  their generator.

## Tests

- Test behavior at the lowest level that proves it, through public
  interfaces, not internals.
- Every rule in the work package's *Definition* has a test, including its edge cases.
- <Project-specific test rules, e.g. "mock HTTP only through the shared
  harness".>

## Docs

- A change to domain behavior updates `docs/<domain>.md` in the same PR.
- A new or sharpened term updates `GLOSSARY.md`.
