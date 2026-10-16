# Scenario 4: Hub Influence Versus Domination

## 1. Question

Can the current Non-Domination measurement distinguish **legitimate
asymmetric coordination** from **domination** when both contain a highly
influential hub?

**asymmetric influence ≠ loss of corrective influence**

A hub may speak more, integrate specialist recommendations, and make more
final decisions while remaining responsive to correction. Domination is when
other participants lose meaningful corrective influence: valid contributions
are ignored, reframed, or overridden regardless of content.

Round 1 tests **Non-Domination only**, with all four dimensions supplied.

## 2. Setting and Conditions

Participants: **H** (coordinator/hub), **S1–S3** (specialists).

| Condition | Structure | Corrective influence | Role |
|---|---|---|---|
| **D** Distributed | symmetric | preserved | reference |
| **H** Responsive hub | asymmetric toward H | preserved | useful asymmetry |
| **X_s** Suppressive hub | same structure as H | lost; only suppression inputs change | **primary pair with H** |
| **X_full** Dominating hub | same as X_s, plus unequal acceptance | lost | realistic secondary |
| **X_collision** | inputs identical to H | lost (ground truth only) | representation collision |

**Primary contrasts**

- **X_s − H:** same asymmetric structure, different calculator-visible
  suppression. Tests measurement sensitivity.
- **X_collision vs H:** same inputs, opposite ground truth. Tests
  representational adequacy.

**Secondary:** H − D (cost of legitimate asymmetry); X_full − X_s
(added effect of unequal acceptance).

H must stay genuinely asymmetric. It is not made symmetric to score well.

## 3. Ground Truth (metadata only, never calculator inputs)

- **Valid correction:** a specialist identifies a constraint violated by a
  proposed plan before it is finalized. Validity is stipulated.
- **Corrective influence preserved:** valid corrections can substantively
  alter the final plan.
- **Corrective influence lost:** valid corrections are systematically
  ignored, overridden, or reframed so they cannot alter the final plan.

Recorded per condition: `valid_corrections`, `corrections_affecting_decision`,
`corrective_influence_preserved`.

## 4. Inputs

Agent order in every dict: H, S1, S2, S3. `participant_count` 4;
`total_decisions` = sum of `decisions_by_agent`; `synthesis_attempts` 4.

| Input | D | H | X_s | X_full | X_collision |
|---|---|---|---|---|---|
| `turn_counts` | 10, 10, 10, 10 | 20, 10, 10, 10 | same as H | same as H | same as H |
| `proposals_by_agent` | 5, 5, 5, 5 | 8, 4, 4, 4 | same as H | same as H | same as H |
| `acceptance_by_agent` | 4, 4, 4, 4 | 7, 3, 3, 3 | 7, 3, 3, 3 | **8, 1, 1, 1** | 7, 3, 3, 3 |
| `decisions_by_agent` | 1, 1, 1, 1 | 5, 1, 1, 1 | same as H | same as H | same as H |
| `syntheses_adopted` | 4 | 4 | **1** | **1** | 4 |
| `syntheses_reframed` | 0 | 0 | **2** | **2** | 0 |
| `dominant_agent_framing` | 0.0 | 0.0 | **0.5** | **0.5** | 0.0 |
| valid / affecting corrections | 3 / 3 | 3 / 3 | 3 / 0 | 3 / 0 | 3 / 0 |
| corrective influence preserved | True | True | False | False | False |

`dominant_agent_framing` for X_s and X_full is set to 0.5, the lowest value
at which the emergence-suppression score reaches 0 **under these
conditions** (adoption = 1/4, reframing = 2/4). This is not a universal
threshold: with full adoption (as in H), framing 0.5 leaves suppression at
1.0 (§6).

## 5. Predictions

Hand-derived, then checked once against the calculator on 2026-09-24; all
values matched.

| | speak | accept | decide | suppress | ND | level | `is_sovereign` | `dominant_agent` |
|---|---|---|---|---|---|---|---|---|
| D | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | NONE | True | None |
| H | 0.654 | 0.931 | 0.750 | 1.000 | **0.826** | **NONE** | True | **H** |
| X_s | 0.654 | 0.931 | 0.750 | 0.000 | 0.626 | MODERATE | False | H |
| X_full | 0.654 | 0.258 | 0.750 | 0.000 | 0.458 | SEVERE | False | H |
| X_collision | 0.654 | 0.931 | 0.750 | 1.000 | 0.826 | NONE | True | H |

- **Legitimate-asymmetry cost:** H − D = −0.174, label unchanged (NONE), but
  H is only 0.026 above the EMERGING cut-off (0.8). The cost comes from
  speaking (1.000 → 0.654), acceptance (1.000 → 0.931), and decisions
  (1.000 → 0.750), with suppression unchanged. ND registers legitimate
  centralization as structural inequality; it does not classify H as
  domination.
- **Suppression discrimination:** X_s − H = −0.200, NONE → MODERATE, driven
  entirely by emergence suppression (1.0 → 0.0 × weight 0.20).
- **Corrective-influence blindness:** X_collision = H exactly, by
  construction. No Non-Domination input encodes whether a correction was
  valid, who corrected whom, or whether it changed the decision.
- **Cross-field interpretive tension:** H is classified NONE at the
  composite dominance level and `is_sovereign` = True, while
  `dominant_agent` = H because the decision-concentration detector
  independently flags an agent responsible for > 50% of decisions (5/8;
  `non_domination.py:261-268`). These outputs are generated by different
  rules, so this is not necessarily a computational contradiction, but it
  creates an interpretive tension for a responsive, legitimately centralized
  hub.

**Core pre-registered logic.** Round 1 separates two questions. H vs X_s
tests whether Non-Domination responds when loss of corrective influence is
expressed through its existing suppression inputs. H vs X_collision tests
whether the representation independently captures corrective influence
itself. The former can provide evidence of measurement sensitivity; the
latter tests the boundary of what the current aggregate representation can
identify. Neither outcome is pre-labelled as a pass or a failure.

## 6. Sensitivity

| Check | Change | Predicted (checked) |
|---|---|---|
| Framing on X_s | `dominant_agent_framing` 0, 0.25, 0.5, 0.75, 1.0 | suppress 0.25, 0.125, 0, 0, 0; ND 0.676 EMERGING, 0.651 EMERGING, then 0.626 MODERATE ×3. **Floor reached at 0.5**; `is_sovereign` flips at 0.5 |
| Framing on H | same values, adoption 4/4, reframed 0 | **no change at any value**: raw = 1.5 − 0.5f ≥ 1 for all f ∈ [0, 1], clamped to 1 (`non_domination.py:322-323`). At full synthesis adoption, the entire allowed range of `dominant_agent_framing` is masked by the upper clamp |
| Decision asymmetry | H decisions 1–7, specialists fixed at 1 each | ND 0.913, 0.899, 0.875, 0.849, 0.826, 0.805, **0.787 EMERGING at 7**. `authoritarian_agent` = H from 4 onward (4/7 > 0.5) |

Specialists are fixed at 1 each because "remaining decisions split evenly"
is only possible in integers for some H values.

## 7. What Counts as a Finding

- **Legitimate-asymmetry penalty:** H < D despite preserved corrective
  influence. Recorded as ND's response to structural asymmetry, not
  automatically as a false positive.
- **Suppression discrimination:** X_s < H when only suppression inputs change.
- **Corrective-influence blindness:** H = X_collision despite opposite ground
  truth (representation finding).
- **Composite compensation (if observed):** substantially different
  component profiles produce similar composite scores. Not pre-registered as
  an expected result.
- **Threshold / clamp sensitivity:** a modest change moves the dominance
  label, or an input's effect is masked by the upper clamp or saturated at
  the lower floor.
- **Cross-field interpretive tension:** result fields generated by different
  rules support different readings of whether domination is present.

## 8. Record for Every Run

Condition; ground-truth metadata (§3); all inputs; four dimension scores;
composite; `dominance_level`; `is_sovereign`; `requires_immediate_action`;
`dominant_agent`; the three per-dimension detectors (`dominant_speaker`,
`concentrated_in`, `authoritarian_agent`); weights; notes.
