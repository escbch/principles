# Adaptive loop

A shared principle for all my apps (Personal Coach, Nutrition, Financial
helper, and later ones). Each app helps me decide, records what I did and what
happened, and learns from my own data over time. It proposes, I decide.

## The loop

```text
Decide → Act → Record → Measure → Learn → Propose → (Decide)
```

1. **Decide:** I choose what to do. Fixed, explainable rules give the default
   (the *baseline policy*).
2. **Act and record:** the app stores what was planned and what actually
   happened, separately, as they were at the time.
3. **Measure:** one clear **outcome** per cycle, available as soon as possible
   (e.g. "workout felt +0.5 RPE harder than planned", "hungry before dinner",
   "spent 12 % over budget").
4. **Learn:** describe first (groups, averages), then small models with
   uncertainty.
5. **Propose:** the app suggests a change with its reason and how sure it is.
   I accept or reject it explicitly.

## Rules

- **Deterministic core.** Validation, calculations and safety rules are fixed,
  tested code. Models and AI only propose or explain, through the same
  validated actions a person uses. Nothing changes silently.
- **Planned, actual and observed stay separate.** Plans, records of what I did,
  and outside signals (watch, bank feed) are different kinds of data. Outside
  signals inform analysis; they are not evidence of what I did unless I decide
  so.
- **Historical integrity.** Store inputs and results as they were. Later rule or
  formula changes don't rewrite the past.
- **One change at a time.** A deliberate experiment states its question before
  it starts (e.g. "cardio after lifting instead of separate days") and its
  outcome afterwards.
- **Small, honest models first.** Personal data is small (tens to hundreds of
  points). Prefer interpretable models such as Bayesian linear regression with
  sensible priors from the literature, show credible intervals and sample
  sizes, and say "too little data" when it is.
- **Beat the baseline before trusting a model.** Compare its predictions
  against the fixed rules on later data. A model that doesn't beat them only
  informs.
- **Explicit decisions are data.** Record which proposals I accepted or
  rejected, and why, so the loop can learn from my choices too.

## Stages, per app

1. Fixed rules and warnings (known good practice).
2. Descriptive comparisons from my own records.
3. Personal effect estimates with uncertainty.
4. Proposals based on those estimates, explicitly accepted.
5. Optional: choosing the next experiment automatically (e.g. a bandit),
   still only as a proposal.

## Examples

| App | Decision | Outcome | Context |
|---|---|---|---|
| Personal Coach | block programming, cardio placement | effort deviation per workout, e1RM trend | sleep, HRV, resting HR (Garmin) |
| Nutrition | meal plan, macros | hunger, weight trend, training performance | training load, sleep |
| Financial helper | budget split, savings rule | monthly over or under budget | income changes, one-off costs |

## Not wanted

- Black-box automation that changes plans, meals or money on its own.
- Models trained on too little data presented as certain.
- Collecting data "just in case" without a question it answers.
