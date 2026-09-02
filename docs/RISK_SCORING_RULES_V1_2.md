# STATION V — Risk Scoring Rules V1.2

## 1. Purpose

This document makes the V1.2 risk-scoring rules operational for implementation. It does not replace the mathematical methodology; it specifies the event-relation semantics required by the scoring layer and is aligned with the canonical relation catalogue defined by Event Model V1.3.

## 2. Event repetition is event-to-event

Repetition is evaluated between distinct EVENTS, never between timeline updates, versions, publications, or evidence items belonging to the same event.

The calculation context is:

```text
COUNTRY + SUBINDICATOR + EVENT
        ↓
related distinct events
        ↓
ordered by event occurrence time
        ↓
repetition position
        ↓
W_r
```

An event may therefore have a different repetition weight for different countries or subindicators.

## 3. Event relation types

The V1.3 event relation catalogue explicitly distinguishes:

- `same_series`: distinct events belonging to the same recurring or continuing series/phenomenon;
- `escalates`: the event represents an escalation of another distinct event;
- `part_of`: the event is materially part of the same larger phenomenon, when that relationship is analytically justified;
- `caused_by`: there is sufficient evidence of a causal relationship between the events;
- `related_to`: events are related but not sufficiently correlated to establish repetition;
- `preceded_by`: temporal precedence only;
- `followed_by`: temporal succession only;
- `duplicate_of`: the event is a duplicate representation of an existing event.

## 4. Relations that can activate repetition reduction

The following relations may establish repetition:

- `same_series`
- `escalates`
- `part_of`

They activate repetition reduction only when all of the following are true:

1. the events are distinct;
2. they concern the same country for the risk calculation in question;
3. they affect the same subindicator for the risk calculation in question;
4. the relation is sufficiently established in the event-resolution layer;
5. the related event falls within the seven-day calculation context;
6. ordering is based on the underlying event occurrence time, not publication time.

`escalates` may receive a higher base impact because the later event is more severe or intense; the repetition multiplier is applied independently.

## 5. Relations that do not activate repetition by themselves

The following relations do not activate repetition reduction by themselves:

- `related_to`
- `preceded_by`
- `followed_by`
- `caused_by`

They may provide analytical context but are insufficient to infer repeated risk contribution.

## 6. Duplicate events

`duplicate_of` does not represent a new event and therefore must not generate an additional risk contribution.

Duplicate evidence or reporting about an existing event must remain attached to the existing event rather than increase repetition or event pressure.

## 7. Repetition weights

For qualifying distinct events affecting the same country and subindicator, ordered by occurrence time:

| Position | W_r |
|---|---:|
| 1st | 1.00 |
| 2nd | 0.60 |
| 3rd | 0.35 |
| 4th | 0.20 |
| 5th and subsequent | 0.10 |

If correlation is not sufficiently established, `W_r = 1.00`.

No V1 automatic repetition inference may be based solely on text similarity, geographical proximity, temporal proximity, or publication duplication.

## 8. Independent events

Qualitatively distinct and analytically independent events accumulate normally. They are not subject to repetition reduction merely because they occur in the same country, category, or subindicator.

## 9. Calculation order

For every applicable Risk Impact:

```text
I_base
  ↓
Relevance (R)
  ↓
Temporal weight (W_t)
  ↓
Repetition weight (W_r)
  ↓
I_effective = I_base × R × W_t × W_r
  ↓
aggregate effective impacts for the subindicator
  ↓
P = 100 × (1 − exp(−ΣI_effective / 3))
  ↓
subindicator update
```

The repetition rule is applied at RiskImpact level. The saturation constant remains `K = 3.0` in V1.2.
