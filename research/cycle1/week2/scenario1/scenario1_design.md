# Scenario 1: Agreement Without Successful Coordination

## 1. Question

Can the current Coheronmetry calculators give a healthy-looking assessment
to a group that agrees highly but fails its shared objective? Specifically,
do they distinguish task success from failure when agreement and other
calculator-visible inputs are held constant?

## 2. Design

| | Task succeeds | Task fails |
|---|---|---|
| **High agreement** | A | B |
| **Low agreement** | C | D |

Probe condition **B′**: high agreement, task fails, but the group makes a
substantive adjustment after every failure. B′ separates *adjusting to
feedback* from *succeeding*, because Embodiment's feedback integration
measures the former (`embodiment.py:133-139`).

- Every condition has **K = 3 attempts**; outcome is judged on the final attempt.
- A and C fail attempts 1–2 and succeed on 3. B, B′, D fail all three.
- So every condition has exactly **2 feedback events**. This avoids the 0.5
  default that zero feedback events would produce (`embodiment.py:135-136`).
- Task outcome is ground truth only. It is **not** passed to any calculator.
- Round 1 uses **synthetic inputs** set directly from Section 4, not
  annotated transcripts. Manipulation checks are therefore satisfied by
  construction, and verbal vs. behavioral acceptance is deferred (the two
  give identical counts here).

## 3. Definitions and Counting Rules

Fixed before any calculator output is examined.

- **Agreement** = proposal acceptance rate. High ≥ 80%, Low ≤ 20%
  (provisional). Acceptance is **uniform across agents**, because the
  proposal-acceptance component scores equality of rates, not their level
  (`non_domination.py:188-198`).
- **Turn:** one message by one agent.
- **Proposal:** a message that explicitly recommends an action or plan.
- **Accepted proposal:** verbal ("I agree") or behavioral (plan is carried
  out). Reported separately in later rounds.
- **Decision:** an explicit commitment to an action or plan.
- **Synthesis:** a contribution combining prior contributions from ≥ 2 agents.
  *Adopted* if used as the group's plan; *reframed* if its substance is
  changed to fit another agent's framing.
- **Feedback event:** a task failure that is followed by another attempt.
- **Adjustment:** a substantive change to the plan after feedback.
  Rephrasing or repeating does not count.
- **Adjustment magnitude:** fraction of plan components changed. Set to
  **0.5** in Round 1 (provisional). Must be set explicitly: the default 0.0
  plus the 0.1 floor caps the score at 0.1 (`embodiment.py:131, 139`).
- **Contribution:** each proposal or synthesis = 1.0.
- **Acknowledgment:** an explicit reference to the *content* of another
  agent's contribution. Bare agreement does not count, to avoid
  double-counting verbal acceptance.

**Healthy-looking** means only the implementation's existing labels:

| Calculator | Label | Rule | Source |
|---|---|---|---|
| Non-Domination | `is_sovereign` | ≥ 0.65 | `non_domination.py:360` |
| Non-Domination | `dominance_level` | ≥ 0.8 NONE / ≥ 0.65 EMERGING / ≥ 0.5 MODERATE / ≥ 0.3 SEVERE / else CRITICAL | `non_domination.py:74-82` |
| Reciprocity | `is_reciprocal` / `is_extractive` | ≥ 0.6 / < 0.35 | `reciprocity.py:341, 345` |
| Embodiment | `is_grounded` / `is_drifting_from_reality` | ≥ 0.6 / < 0.4 | `embodiment.py:307, 312` |

Scores between the two flags are reported as **intermediate**.

## 4. Round 1 Inputs

Agents are `a1`–`a4`.

**Shared by all conditions:** `turn_counts` 10 each; `participant_count` 4;
`proposals_by_agent` 5 each; `decisions_by_agent` 1 each; `total_decisions`
4; `synthesis_attempts` 4; `syntheses_reframed` 0;
`dominant_agent_framing` 0.0; `contribution_totals` 6 each;
`feedback_events` 2.

| Input | A | B | B′ | C | D |
|---|---|---|---|---|---|
| Agreement | High | High | High | Low | Low |
| Outcome (not an input) | Success | Failure | Failure | Success | Failure |
| `acceptance_by_agent` (each) | 4 | 4 | 4 | 1 | 1 |
| `syntheses_adopted` | 4 | 4 | 4 | 1 | 1 |
| `adjustments_made` | 2 | 0 | 2 | 2 | 0 |
| `adjustment_magnitude` | 0.5 | 0.0 | 0.5 | 0.5 | 0.0 |

**Dimensions supplied in Round 1**

- Non-Domination: all four.
- Reciprocity: contribution balance only. Acknowledgment would overlap with
  agreement; exchange trajectory is circular; repair has no defined
  "imbalance" in this task.
- Embodiment: feedback integration only. The other dimensions have no
  counting rule for this task.
- Emergence: excluded. Its inputs are `[R, B, E, ND]` score vectors, which
  needs a separate design.

With one dimension supplied, a calculator's composite equals that
dimension's score.

## 5. Predictions

Derived by hand from the formulas. A one-off check against the calculators
on 2026-09-24 matched every value and label.

| | A | B | B′ | C | D |
|---|---|---|---|---|---|
| Non-Domination | 1.00 NONE | 1.00 NONE | 1.00 NONE | 0.95 NONE | 0.95 NONE |
| Reciprocity | 1.00 reciprocal | 1.00 reciprocal | 1.00 reciprocal | 1.00 reciprocal | 1.00 reciprocal |
| Embodiment | 0.50 intermediate | 0.00 drifting | 0.50 intermediate | 0.50 intermediate | 0.00 drifting |
| Embodiment, feedback omitted | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 |

- **Non-Domination and Reciprocity are blind to outcome**: A = B = B′.
- **Embodiment separates A from B, but B′ = A**: it tracks adjustment, not outcome.
- **Omitting feedback integration** makes all conditions indistinguishable.
- **Known sensitivity:** A's Embodiment score equals the adjustment magnitude.
  Any magnitude ≥ 0.6 turns A from intermediate to grounded.

## 6. Contrasts

| Contrast | Isolates |
|---|---|
| B − A | task outcome, high agreement |
| C − A | agreement, success |
| D − B | agreement, failure |
| B′ − A | task outcome, same adjustment |
| B′ − B | adjustment, same outcome |

Synthetic and deterministic, so no significance testing. Report raw
differences and whether any label changes.

## 7. What Counts as a Finding

- **Outcome blindness:** A and B identical (report exact differences).
- **Directional discrimination:** a score moves in the expected direction.
- **Parameter sensitivity:** a ±20% change to a provisional value flips a
  label or the ordering of conditions.
- **Optional-dimension sensitivity:** omitting a dimension flips a label.
- **Construct mismatch:** a component responds to a different property than
  its name suggests.

A flip is recorded as a finding and is not tuned away.

## 8. Perturbations (one at a time, baseline and ±20% unless listed)

Thresholds are applied by re-comparing the composite score. Formula
constants are changed by subclassing in experiment code, never by editing
the repository.

| Parameter | Baseline | Tested |
|---|---|---|
| Adjustment magnitude | 0.5 | 0.4, 0.6 |
| Low-agreement acceptance | 1/5 each | 2,1,1,0 of 5; 0/5 each |
| Low-agreement syntheses adopted | 1 of 4 | 0, 2 |
| `is_sovereign`, dominance cut-offs | as above | ±20% |
| `is_reciprocal`, `is_extractive` | 0.6, 0.35 | ±20% |
| `is_grounded`, `is_drifting_from_reality` | 0.6, 0.4 | ±20% |
| Non-Domination weights | 0.20/0.25/0.35/0.20 | each ±20%, renormalized (`non_domination.py:407-412`) |
| Suppression framing coefficient, centering offset | 0.5, 0.5 | ±20% (`non_domination.py:322-323`) |
| Feedback-magnitude floor | 0.1 | ±20% (`embodiment.py:139`) |
| Embodiment | feedback supplied | feedback omitted |
| Reciprocity | balance only | + acknowledgment, overlap rule; + acknowledgment, content rule |

## 9. Record for Every Run

Condition; agreement; outcome; perturbation or variant ID; all inputs; all
dimension scores; composite; labels; weights and parameters used; omitted
dimensions; manipulation-check result.
