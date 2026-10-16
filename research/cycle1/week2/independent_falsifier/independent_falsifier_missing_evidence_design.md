# Independent Falsifier — Missing Evidence vs. Positive Evidence

> This falsifier was derived from cross-scenario observations of default-value behavior in the implementation and was not one of the four scenarios proposed by the PI.

Coheronmetry 0.2.0, commit `7d0144bd`. Synthetic, dimension-level only (measure classes called directly; no composite, no transcript).

## 1. Question

Can a dimension score distinguish **explicit positive evidence** from **absence of relevant observational evidence**?

## 2. Rationale

Scenarios 1–4 repeatedly hit default values that fire when a count is zero or an input is omitted (S1: Embodiment 0.5 with no feedback events; S2: proposal-acceptance 0.5 at zero mean; S3: persistence 0.5 when `previous_output=None`). This test isolates that default semantics as its own question, independent of any coordination construct.

The target claim is not that missing evidence should receive any particular numeric value, but that a high dimension score should be distinguishable from a state in which there is no relevant observational evidence.

## 3. Ground truth (metadata only, never a calculator input)

| Label | Meaning |
|---|---|
| positive | the dimension's positive behavior was observed |
| absent | the behavior never occurred / was not observed |
| negative | the dimension's negative behavior was observed |

## 4. Test A — Decision Concentration (`non_domination.py:240–258`)

Agents a1–a4; `total_decisions = sum(decisions_by_agent)`.

| Condition | Ground truth | `decisions_by_agent` |
|---|---|---|
| A_balanced | positive | 1, 1, 1, 1 |
| A_none | absent | 0, 0, 0, 0 |
| A_concentrated | negative | 4, 0, 0, 0 |

## 5. Test B — Emergence Suppression (`non_domination.py:303–323`)

`syntheses_reframed = 0`, `dominant_agent_framing = 0.0` at baseline.

| Condition | Ground truth | attempts | adopted |
|---|---|---|---|
| B_positive | positive | 4 | 4 |
| B_none | absent | 0 | 0 |
| B_failed | negative | 4 | 0 |

## 6. Pre-registered predictions and sensitivity

Hand-derived from the code. Test B scores use the baseline framing value f = 0.

| Condition | Score | Why |
|---|---|---|
| A_balanced | 1.0 | HHI = 0.25 = 1/n |
| A_none | **1.0** | `total_decisions == 0` → HHI 0.0 → score 1.0 |
| A_concentrated | 0.0 | HHI = 1.0; `authoritarian_agent = a1` |
| B_positive | 1.0 | baseline f = 0: clamp(1 − 0 − 0 + 0.5) |
| B_none | **1.0** | `attempts == 0` → adoption default 0.5 → clamp(0.5 + 0.5) |
| B_failed | 0.5 | clamp(0 + 0.5) |

Prediction: absent = positive in both tests; in Test B, absent > negative.

Sensitivity (pre-registered, no tuning):

- **Attempts / decisions 0 → 1 (discontinuity).** A: one decision by a1 → 1.0 drops to 0.0 and `authoritarian_agent = a1`. B: one attempt, not adopted → 1.0 drops to 0.5; one attempt, adopted → stays 1.0. A single observation can move the score by the full or half range.
- **Framing sweep on Test B, f ∈ {0, 0.5, 1.0}.** positive 1.0 / 1.0 / 1.0; none 1.0 / 0.75 / 0.5; failed 0.5 / 0.25 / 0.0. The tie between absent and positive holds only at f = 0; at f > 0, separation comes from positive saturating at the clamp, not from any representation of missing evidence.
- **Optional representation probe.** Compare the registered-agent zero-count representation `{a1:0, a2:0, a3:0, a4:0}` with `{}` only as a secondary API-semantics check. This probe is not part of the primary falsification criterion.

## 7. Falsification criterion

If an absent-evidence condition scores the same as its positive-evidence counterpart (|Δ| < 1e-9) in either test, then for that tested dimension the current representation and default semantics **fail to discriminate explicit positive evidence from absence of relevant evidence**. The verdict is per dimension and does not generalize to untested dimensions. A label flip or a large jump under the 0 → 1 sensitivity is recorded as a finding, not tuned away.

---

*Revision note (2026-09-25, after the run):* wording of §1, the §3 ground-truth meanings, the §6 framing note, and the scope sentence in §7 were clarified. Conditions, inputs, predicted values, sensitivity items and the |Δ| < 1e-9 criterion are unchanged from the version that was run.
