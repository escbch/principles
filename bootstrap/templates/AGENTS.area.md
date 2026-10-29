# {{PROJECT}} — <Area> Instructions

These instructions apply to `<area>/`. Also follow the repository-wide rules in
`../AGENTS.md`.

## Stack and Dependency Direction

<Area> uses <languages, frameworks, tools>.

Prefer this dependency direction:

```text
<entry points> → <validation> → <domain logic> → <persistence>
```

<One or two sentences on what each layer owns and what it must not do.>

## <Data / Migrations / Generated files>

<!-- Rules for things that are hard to undo. Examples: -->

- All schema changes require migrations; never edit merged migrations.
- Never run destructive operations against an unverified database.
- Generated files (<contract>, <schema types>) are regenerated with
  `<command>`, never edited by hand.

## Testing and Linting

Run commands from `<area>/`. Before considering a change complete:

```sh
<test command>
<lint command>
<type check / build command>
```

Tests are organized under `<tests dir>/`:

- `<unit>/`: <what belongs here>.
- `<integration>/`: <what belongs here>.

Add or update tests for behavior changes at the lowest level that proves them.
<Testing rules specific to this area, e.g. "assert user-observable behavior
through accessible roles; mock HTTP only through the shared harness".>
