# Corrective Influence

Coheronmetry 0.2.0, commit `7d0144bd`. Claim and reading rules fixed on 2026-10-01, before the calculator run. No formula was changed.

Week 2 left this open (E-11, I-03, I-07). A hub that had stopped taking correction could be given the same inputs as a responsive hub, and Non-Domination returned the same score. That is why the claim is here. It does not decide this week's status in advance.

## 1. Question and claim

Can a valid correction that actually changes the plan be told apart, afterwards, from the same correction shrugged off, or from no correction at all?

A valid corrective intervention that receives substantive uptake should produce a distinguishable downstream change in relational state or participant behavior compared with an ineffective or absent correction.

We are looking for a difference we can see. How big it is gets written down when we see it. Something like "Non-Domination must rise by 0.2" is not part of the claim. We do not know the right size yet.

## 2. Definitions

Validity and uptake are facts about the episode. A score does not tell us which is which.

| Term | Meaning |
|---|---|
| Valid corrective intervention | A participant identifies a real constraint that the current plan violates, before that plan is treated as settled. Validity is stipulated. |
| Substantive uptake | The correction changes the subsequent plan or decision in substance. Acknowledgment, restatement, or reframing that leaves the plan unchanged does not count. |
| Ineffective correction | A valid correction is offered and does not receive substantive uptake. It is ignored, overridden, or reframed away. |
| Absent correction | No corrective intervention is offered. |
| Downstream change | A change, after the intervention point, in relational state or in what participants do next. Candidate readouts are relational state, drift, repair, and participant behavior. The test design chooses which readout is primary. |
| Distinguishable | The effective-uptake condition and the comparison condition differ on that pre-registered readout. |
| Expected direction | The direction consistent with the correction having been taken up: the addressed problem is no longer left standing in the same way, or participant behavior shifts with the changed plan. The test design names the direction for its chosen readout before the run. |

The claim needs a comparison. This test has both: an ineffective correction, and no correction. The effective case by itself cannot carry the claim.

## 3. Conditions

Two people: **H** (hub) and **S** (specialist). One stipulated constraint. At the start, every episode is on plan **A**.

| | E effective | I ineffective | N absent |
|---|---|---|---|
| Valid correction raised | yes | yes, same correction | no |
| Acknowledged | yes | yes | no |
| Plan | A → **B** | A → **A** | A → **A** |
| Constraint | resolved | remains | no correction opportunity |
| Substantive plan change | **yes** | **no** | **no** |

E and I both get a spoken acknowledgment. The plan afterwards is what separates them.

## 4. What the source actually counts

Before choosing inputs I looked for a field that already means "the plan changed because the correction was taken up," and that I could fill without pasting that label into the calculator.

There isn't one. If the only way a count moves is that I set it from `uptake = true`, the score is just reading my answer back.

`RepairResponsivenessMeasure` (`reciprocity.py:276-307`) is about reciprocity going out of balance and then coming back. The caller types `imbalances_flagged`, `repairs_initiated`, `repairs_successful`, and `mean_repair_time`. Nothing in the repo computes those from a plan, or from `repair_history`. Zero imbalances scores 0.75, described as the benefit of the doubt when reciprocity has not drifted. That is a different situation from "nobody offered a correction." `DriftType` (`state.py:131-142`) has no "plan violated a constraint" value. `RepairProcess.complete` (`repair.py:187-200`) takes `successful` as an argument. `record_repair` (`state.py:373-380`) then adds 0.05 to trust. `RepairType.CORRECTION_BIAS` (`corrector.py:1-9`) is the system nudging the next agent. It is the other direction from a participant's correction being taken up.

| Candidate | What the code says it is | Why I left it out |
|---|---|---|
| `FeedbackIntegrationMeasure` (`embodiment.py:114-139`) | The caller supplies `adjustments_made` after feedback. | In this claim, a real change to the plan *is* uptake. Filling that count would be filling the label. |
| `AcknowledgmentRateMeasure` (`reciprocity.py:194-212`) | A contribution was explicitly recognized. | E and I both acknowledge. The claim already says that is not uptake. |
| `ExchangeTrajectorymeasure` (`reciprocity.py:223-265`) | Slope of reciprocity scores the caller appends. The class name is spelled that way in the source. | This episode does not produce that series. |
| Non-Domination counts | Airtime, how evenly proposals are accepted, who decides, whether a synthesis is adopted or reframed. | None of these is the substance of the plan. Writing uptake into `decisions_by_agent` or `syntheses_adopted` just renames it. Holding those counts fixed is the Week 2 collision, E-11. |
| `InteractionRecord.interrupted` (`non_domination.py:90-106`) | A turn-level override flag. | No calculator reads it. |
| `RelationalState.update_scores` | Floats the caller stores, plus a repair rate over events the caller recorded. | The floats move when the caller writes them. |

## 5. What we actually read out

No existing field is a clean readout of "the plan changed." What we pre-registered is the bundle the source already knows how to score: Non-Domination counts, acknowledgment rate, Embodiment with no dimension measures, and whatever drift and repair records we are willing to write.

If that bundle really carried uptake, E would come out different from I and from N, since only E's plan changed. Section 8 says how to read it if E and I come out the same.

## 6. Mapping, and the scores predicted beforehand

Shared baseline, before the correction: turns 4 and 4; proposals 2 and 2; acceptances 2 and 2; decisions 1 and 1; synthesis attempts 2, adopted 2, reframed 0, framing 0.0; contributions made 4, acknowledged 2.

| What happened | What it may set | E | I | N |
|---|---|---|---|---|
| S speaks the correction | `turn_counts` for S, +1 | 5 | 5 | 4 |
| H speaks the acknowledgment | `turn_counts` for H, +1 | 5 | 5 | 4 |
| The correction is recognized as a contribution | `contributions_made` +1, `contributions_acknowledged` +1 | 3 / 5 | 3 / 5 | 2 / 4 |
| Plan A becomes plan B | nothing | — | — | — |
| Constraint resolved or not | nothing | — | — | — |

Left out, rather than filled from the label: `RepairResponsivenessMeasure`, `FeedbackIntegrationMeasure`, `ExchangeTrajectorymeasure`, `record_drift`, `record_repair`. Embodiment is called with no dimension measures. The signature requires an `agent_id`; every episode uses H.

Worked out by hand from the source:

- Every Non-Domination dimension is 1.0 (the counts are even; suppression is `clamp(1 − 0 − 0 + 0.5) = 1`). Composite **1.0**, level `none`, `is_sovereign` true, `dominant_agent` none. N has turns 4 and 4 instead of 5 and 5. Both splits are even, so the speaking score stays put.
- Acknowledgment: E = I = 3/5 = **0.600**, N = 2/4 = **0.500**. Only that reciprocity dimension is supplied, so the composite equals the rate. E and I clear `is_reciprocal` at 0.6. N does not.
- Embodiment composite **0.500** in every episode.
- Drift count 0 and repair count 0, because the runner never calls `record_drift` or `record_repair`. Empty history means we did not write those records. It does not mean the episode was seen to contain no drift or repair.

## 7. How a result is read

Take these in order. The first one that fits is the status.

**UNRESOLVED.** The current representation cannot express the distinction the claim needs, so the claim cannot be adjudicated. That distinction is substantive uptake versus an ineffective or absent correction, together with a downstream difference in relational state or participant behavior. A metadata label that never enters the measurement does not count as expressing it.

**FAILS.** The scenario has already produced different downstream behavior between effective uptake and the comparison, and either:

- the current measurement still cannot separate those conditions, or
- the measurement separates them in the direction opposite to uptake.

**SURVIVES.** Effective uptake shows the expected downstream difference, and each comparison condition included in the test does not show that same change.

If the episodes never actually differed downstream, the run is not eligible for SURVIVES or FAILS. That is a failed manipulation. It is written down as such, and it is not a verdict on the claim.

Check UNRESOLVED first. If the representation cannot express the distinction, the entry is UNRESOLVED even when the written scenario describes different behavior. That case is not called FAILS.

## 8. How to read this particular test

**E versus I** is the uptake contrast. Same correction, same acknowledgment, different plan afterwards.

**N** is "the exchange never happened." It may score differently because there was no correction to acknowledge. If it does, that shows the calculators noticed the exchange. It does not show they noticed whether the plan changed.

**What the runner is for.** Section 4 is what establishes that no existing input will take plan substance. The runner only shows what the measurements do once we refuse to invent one. Flipping I's plan and constraint, and getting the same inputs back, shows that this mapping ignores plan substance. It does not, on its own, prove the API is incapable of expressing it.

Expected status, on that reading: **UNRESOLVED**. E and I differ in the plan. The mapping we are willing to defend gives them the same inputs and the same measurements.

## 9. Limits

One made-up episode, not a transcript. The calculators see one snapshot. No weight sweep. No formula change.

For each episode the runner keeps the behavioral record, the mapped inputs, the fields we refused, the three calculator outputs, and the drift and repair counts.
