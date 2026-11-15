# API contracts: response models and the generated client

Learned in Vacation Planner (2026-11). A FastAPI backend publishes its OpenAPI
schema; the frontend generates its types from it, and CI fails when the two
differ. A booking reference had to be left out of answers for people who may
not see it, not sent as `null`.

## What happened

- A wrap `model_serializer` on the response model removed the field neatly at
  runtime, and every test passed.
- But a serializer replaces the model's serialization schema with the
  serializer's return type. Its return was `Any`, so the published schema
  lost the whole model: the regenerated contract showed 235 deleted lines, and
  the client's type became `unknown`.
- What worked: build the response model from explicit fields only, leave out
  the hidden one, and answer with `response_model_exclude_unset=True` on each
  route. The schema keeps the field as optional; a test checks that it is
  absent for the people who may not see it.

## Rules

- **Read the contract diff after changing a response model.** Regenerate the
  schema and the client types and look at the size of the diff: a model
  change that deletes a large part of the schema broke it, even when every
  test passes.
- **Keep response models plain.** Prefer fields and validators. A
  `model_serializer` (or a `json_schema_extra` that rewrites the model)
  changes what the schema says; use one only with a precise return type, and
  check the generated schema.
- **Hide a field per caller by leaving it unset**, not by setting it to
  `null`: build the model from explicit fields and answer with
  `response_model_exclude_unset=True`. Test that the field is absent, on the
  list and on the single read.
- **Add fields, don't change them**, so existing screens keep working
  (see `ui-building.md` → Boundaries).

## Not wanted

- A response type that the generated client sees as `unknown` or `any`.
- Hiding sensitive values by sending `null`: the key itself tells that a value
  exists, and the client type then claims it always may.
