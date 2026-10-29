# Domain Docs

How the engineering skills should consume this repo’s domain documentation when exploring the codebase.

## Before exploring, read these

- `GLOSSARY.md` at the repository root.
- `GLOSSARY-MAP.md` at the repository root if it exists; read each mapped context relevant to the topic.
- ADRs under `docs/adr/` that affect the area being changed.

If these files do not exist, proceed silently. The `/domain-modeling` skill creates them lazily when terms or decisions are resolved.

## File structure

This is a single-context repository:

```text
/
├── GLOSSARY.md
├── docs/adr/
│   ├── 0001-example-decision.md
│   └── 0002-another-decision.md
└── …
```

## Use the glossary’s vocabulary

When output names a domain concept—in an issue title, proposal, hypothesis, or test—use the term defined in `GLOSSARY.md`. Avoid synonyms the glossary explicitly rejects.

If a required concept is absent, reconsider whether the term belongs to the project or record the gap for `/domain-modeling`.

## Flag ADR conflicts

Surface any conflict with an existing ADR explicitly rather than silently overriding it.

## Domain behavior

`GLOSSARY.md` defines vocabulary. It is not the complete behavioral
specification.

When shaping or implementing changes to domain behavior, historical meaning,
lifecycle rules, calculations, or invariants, read the relevant sections of
`docs/<domain>.md` (if it exists).

For a `ready-for-agent` work package that does not change those rules,
the work package, relevant ADRs, code, and tests are sufficient.
