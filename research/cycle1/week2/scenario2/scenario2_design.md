# Scenario 2: Disagreement With Successful Coordination

## 1. Question

Can the current calculators distinguish **productive disagreement** from
**fragmentation**? And does disagreement lower the measurements even when
the group coordinates successfully?

The construct distinction under test is:

**agreement level ≠ equality of influence ≠ integration quality**

## 2. Design

| Condition | Agreement | Coordination | Outcome |
|---|---|---|---|
| **C** Convergent | High | Integrated | Success |
| **P** Productive disagreement | Low | Integrated | Success |
| **F** Fragmented | Low | Not integrated, no adjustment | Failure |
| **F′** Fragmented, individually adjusting | Low | Not integrated, each agent adjusts own plan | Failure |

- **P vs C** (primary): both succeed; only agreement differs.
- **P vs F** (primary): same disagreement; only integration differs.
- **F′** plays the role B′ played in Scenario 1: it tests whether Embodiment
  separates P from F because of coordination, or only because of adjustment.

Structure carried over from Scenario 1: K = 3 attempts, outcome judged on
the final attempt, exactly 2 feedback events per condition, synthetic
inputs, and task outcome is ground truth only, never a calculator input.

**Interpretation caution.** Scenario 1 showed the calculators do not see
acceptance *level* (uniform 80% and uniform 20% both score 1.0). So if
agreement is represented only by acceptance level, P = C holds by
construction. That result means the calculators **cannot see** the
disagreement, not that they **correctly decline to penalize** it. P vs C is
informative only where disagreement changes a calculator-visible field
(see the variant `C_x_from_a1`).

## 3. Definitions and Counting Rules

Same as Scenario 1 §3, with these additions and changes:

- **Agreement:** High = 4 of 5 proposals accepted per agent; Low = 1 of 5.
  Acceptance is uniform across agents in the baseline.
- **Acknowledgment (content rule):** an explicit reference to the content of
  another agent's contribution. Bare agreement does not count. Included in
  Scenario 2 because the content rule removes the overlap with verbal
  acceptance that excluded it from Scenario 1, and it is the only
  Reciprocity dimension that can reflect integration.
- **Contributions made (for acknowledgment rate):** 20 proposals + 4
  syntheses = 24.
- **Synthesis in F:** syntheses are attempted but none is adopted.
- **Decision in F:** each agent commits to its own plan (1 each).
- **Adjustment in F′ (rule variation):** a substantive change by an agent to
  **its own** plan counts as an adjustment, because F′ has no shared plan.
  This is the only condition where "the plan" means an individual plan.

## 4. Inputs

**Shared by all conditions:** `turn_counts` 10 each; `participant_count` 4;
`proposals_by_agent` 5 each; `decisions_by_agent` 1 each; `total_decisions`
4; `synthesis_attempts` 4; `syntheses_reframed` 0;
`dominant_agent_framing` 0.0; `contribution_totals` 6 each;
`contributions_made` 24; `feedback_events` 2.

| Input | C | P | F | F′ |
|---|---|---|---|---|
| Outcome (not an input) | Success | Success | Failure | Failure |
| `acceptance_by_agent` (each) | 4 | 1 | 1 | 1 |
| `syntheses_adopted` | 4 | 4 | 0 | 0 |
| `contributions_acknowledged` | 18 | 18 | 2 | 2 |
| `adjustments_made` | 2 | 2 | 0 | 2 |
| `adjustment_magnitude` | 0.5 | 0.5 | 0.0 | 0.5 |

**Dimensions supplied**

- Non-Domination: all four.
- Reciprocity: contribution balance **and acknowledgment rate** (content rule).
- Embodiment: feedback integration only.
- Emergence: excluded. "Integrating constraints into a solution Z that no
  agent proposed alone" has no input field; formulation B takes `[R, B, E,
  ND]` score vectors, not solution content. Recorded as a construct mismatch
  and deferred to Scenario 3.

## 5. Predictions

Hand-derived, then checked once against the calculators on 2026-09-24; all
values matched.

| | C | P | F | F′ |
|---|---|---|---|---|
| Non-Domination | 1.00 NONE | 1.00 NONE | 0.90 NONE | 0.90 NONE |
| Reciprocity | 0.875 reciprocal | 0.875 reciprocal | 0.542 intermediate | 0.542 intermediate |
| Embodiment | 0.50 intermediate | 0.50 intermediate | 0.00 drifting | 0.50 intermediate |

- **P = C on all three.** Disagreement is invisible, not correctly handled (§2).
- **P vs F separated by Reciprocity** (through acknowledgment) and **by
  Embodiment** (through adjustment). Neither responds to disagreement itself.
- **F stays NONE on Non-Domination (0.90).** Fragmentation is not
  domination; the ND drop comes only from emergence suppression (0.5,
  unadopted syntheses). ND measures equality of influence, not integration.
- **F′ = P on Embodiment, by construction.** The current aggregate input
  (`adjustments_made`, `adjustment_magnitude`) does not encode whether
  adjustments are coordinated at the group level or made independently by
  individual agents. P and F′ differ in that property but supply identical
  inputs. This extends the Scenario 1 A = B′ finding by naming the missing
  representation: the coordination level, target, or ownership of an
  adjustment.
- F and F′ trigger the implementation note "Acknowledgment rate is low"
  (`reciprocity.py:453`).

## 6. Contrasts

| Contrast | Isolates |
|---|---|
| P − C | agreement, both integrated and successful |
| F − P | integration, same disagreement |
| F′ − P | coordinated vs. local adjustment under identical aggregate feedback-integration inputs |
| F′ − F | adjustment, same fragmentation |

Report raw differences and whether any label changes.

## 7. What Counts as a Finding

Same categories as Scenario 1 §7, plus:

- **Apparent disagreement penalty:** P scores lower than C. The responsible
  dimension and input are then inspected to determine whether the decrease
  is attributable to a calculator-visible representation of disagreement or
  to another correlated relational feature. A composite change is never
  interpreted before its responsible dimension and input are identified.
- **Fragmentation blindness:** F or F′ matches P on a calculator.
- **Missing-evidence reward:** removing evidence of integration *raises* a
  score (tested by `F_no_synthesis`).

## 8. Variants and Perturbations

| Variant | Change from baseline | Prediction (checked) |
|---|---|---|
| `F_no_synthesis` | Calculator-level perturbation of F: `synthesis_attempts` 4 → 0, `syntheses_adopted` 0; all other inputs frozen | suppression 0.5 → **1.0**; ND 0.90 → **1.00**. Less integration evidence gives a higher score. |
| `C_x_from_a1` | Behavioral variant of C: converges on a1's plan, acceptance a1 5, others 4 | proposal acceptance 1.0 → 0.898; ND 1.00 → **0.975**, now **below P**; label stays NONE |
| Acknowledgment threshold | vary F's `contributions_acknowledged` 2 → 0, 6, 10 | F crosses `is_reciprocal` (0.6) at 5 of 24 acknowledged (hand-derived: (1 + a/24)/2 ≥ 0.6) |
| `P_zero`, `F_zero` | Calculator-level perturbation of P and F: acceptance 1 → 0 each (still uniform); all other inputs frozen | **Tests the zero-mean/default boundary, not ordinary sensitivity to agreement level.** Proposal acceptance 1.0 → default 0.5 (`non_domination.py:194-195`). Hand-derived: P_zero ND 0.875 NONE; F_zero ND 0.775 **EMERGING** (label flip from NONE) |
| Adjustment magnitude | 0.4 / 0.5 / 0.6 | as Scenario 1: 0.6 turns C, P, F′ grounded |

Thresholds are applied by re-comparing composite scores; the repository is
not modified.

**Two kinds of variant.**

- **Behavioral variant** (`C_x_from_a1`): a complete synthetic condition that
  satisfies every counting rule in §3.
- **Calculator-level perturbation** (`F_no_synthesis`, `P_zero`, `F_zero`):
  an isolated change to Non-Domination inputs only, with all other
  calculator inputs frozen at the parent condition's values. It is not a
  fully re-annotated behavioral condition. In particular, `F_no_synthesis`
  keeps `contributions_made` = 24 and `contribution_totals` = 6 each,
  although 0 syntheses would give 20 under the §3 rule. This isolates the
  implementation's no-evidence behavior on Non-Domination alone.

## 9. Record for Every Run

Same as Scenario 1 §9.
