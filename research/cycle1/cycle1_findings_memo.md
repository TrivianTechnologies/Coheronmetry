# Cycle 1 Findings Memo: Coheronmetry

Coheronmetry 0.2.0, commit `7d0144bd`. Evidence is in the week ledgers (E-01 through E-14) and issue logs (I-01 through I-16). This memo compresses that record. It does not replace it.

The cycle began as a test of Coheronmetry's measurement logic and repeatedly found that some of the hardest problems appeared upstream of the score. Before asking whether a number is calibrated, the implementation has to be able to see the distinction the construct is supposed to measure.

## 1. Question and scope

This cycle asked whether the current Coheronmetry implementation can represent and distinguish several relational conditions its constructs are intended to track, before attempting empirical calibration.

The work was an implementation and representation audit. The controlled cases in Weeks 2–4 were written by us. They are not evidence about real human–AI exchanges.

No production formula was changed. Ground truth stayed out of the calculators unless a source-supported input already meant that fact.

## 2. What Coheronmetry currently measures

The four field constants are scored from structured values the caller supplies.

**Reciprocity.** Contribution balance, acknowledgment rate, a trajectory of reciprocity scores the caller appends, and repair responsiveness after reciprocity drift.

**Embodiment.** Reality anchoring, actionability, feedback integration, context sensitivity, evolutionary plasticity, and a grounding ratio. Feedback integration is a count of adjustments after feedback, supplied by the caller.

**Emergence.** The audited path was Formulation B, which scores geometric distance between vectors. Distributed information and whether one participant could have produced the output alone are not inputs.

**Non-Domination.** How evenly speaking time, proposal-acceptance rates, and decisions are spread, plus whether cross-agent synthesis is adopted, reframed, or pulled into one agent's frame.

These measures operate on structured counts, scores, and vectors supplied by the caller. They do not currently observe a raw exchange and derive the relational events themselves.

In several controlled cases, when a source-defined input represented the distinction being manipulated, the corresponding calculator output moved with it. In Week 2, acknowledgment separated productive disagreement from fragmentation, and synthesis suppression accounted for the whole gap between a responsive hub and a suppressive one (E-09, E-11). Orderings held across the weight changes we tried (E-13). Labels near the cutoffs did not.

## 3. What the current representation cannot yet observe

Several interaction states that we had defined as different became the same once they were mapped into calculator inputs.

**Corrective influence.** A hub that had stopped taking correction, given the same inputs as a responsive hub, received the same Non-Domination score (E-11, `X_collision` = H at 0.826). Week 3 made the same collision with an explicit plan change: effective uptake and an acknowledged correction that left the plan alone shared inputs and scores (ND 1.000, Reciprocity 0.600, Embodiment 0.500 with no dimensions). Reciprocity did move when the corrective exchange was absent (0.500). It was counting acknowledgment, which is what that measure is for. It was not counting whether the plan changed (E-14).

**Emergence.** Formulation B has no input for the E-versus-R distinction it was asked about, so that contrast stayed unresolved. In the constructed vector case, copying one participant scored 0.75, above simple averaging at 0.50. Under the tested scaling setup, the copy score rose from 0.50 with two agents to 0.90 with ten (E-10).

**Non-Domination.** Loss of corrective influence showed up when we encoded it as suppression. It disappeared when the relational difference left those aggregates alone. The same healthy hub was labeled sovereign and, separately, named as the dominant agent (E-11). Missing observations can score like positive evidence: no decisions and balanced decisions both score 1.0 on decision concentration (E-12).

Task outcome and coordinated-versus-local adjustment were in the same class of gap (E-08, E-09). High agreement with failure matched high agreement with success, once the visible counts were held still.

The recurring issue was not only that the knobs are uncalibrated. In several cases the information needed to test the distinction never reached the calculator.

## 4. Corrective uptake observer proposal

E-14 and I-16 are one instance of that gap. The current inputs do not independently represent whether a correction changed the plan.

Putting that answer into `adjustments_made` or `repairs_successful` would make the calculator repeat a judgment we had already written down. Week 3 did not do that. Both of those measures were left out, and the claim stayed UNRESOLVED.

Week 4 specified an observer upstream of the scores (v0.1, `week4/corrective_uptake_observation_spec.md`). It reads `plan_before`, `plan_after`, `correction`, `constraint_identified`, `subsequent_actions`, and `observation_window`. Four functions derive intermediate observations: `detect_plan_delta`, `evaluate_constraint_resolution`, `trace_change_to_correction`, and `evaluate_persistence`. `classify_uptake` applies the frozen decision rules to those results. It does not receive `uptake=True`.

On four structured cases written for the rules:

| Condition | Result |
|---|---|
| Effective uptake | `SUBSTANTIVE_UPTAKE` |
| Acknowledgment only | `UNRESOLVED` |
| No correction | No classification |
| Unrelated plan change | `UNRELATED_CHANGE` |

A supplementary check, not a fifth condition, returned `REJECTED_OR_OVERRIDDEN` when a later action restored the old value of the field that had changed. The first persistence signature could not do that, because it did not receive `plan_before`. The contract was corrected. The classification rules were not rewritten to fit the cases.

These tests show that the frozen specification can be executed on controlled structured cases. They do not show that the observer is reliable on real human–AI exchanges. `ACKNOWLEDGED_ONLY` is still unreachable: the minimum inputs cannot tell an acknowledged correction from an ignored one when the plan does not change. `attributed` means the observed delta matches the change the correction requested. It does not mean the correction caused that change.

## 5. Evidence across the cycle

Week 1 read the repository and ran the existing suite unchanged: 91 tests passed (E-01). That checks the software against itself. The open questions were whether the scores measure the constructs, why the product is the aggregation rule, whether emergence is more than novelty, and what the five-model episode can support. None of those were closed.

Week 2 turned the worry into controlled collisions. Synthetic inputs went into the real calculators. Outcome, coordination, corrective influence, and missing evidence were metadata. Where a proxy was visible, the score moved. Where the distinction was not an input, the conditions tied. Missing evidence often received a high default (E-08 through E-13, I-07 through I-15).

Week 3 took corrective influence out of that list and wrote the claim before the run, including what would count as SURVIVES, FAILS, or UNRESOLVED. Effective and ineffective uptake differed in the plan and matched in every justified input (E-14, I-16).

Week 4 wrote the observer that would have to sit in front of those inputs, and ran it without calling the calculators. The specification is the definition. The Python file is one implementation of it.

## 6. What survived, what is challenged, and what is unresolved

**Supported so far.** The calculators reproducibly implement the aggregate operations we read in the source. Some intended distinctions appear when the relevant information is passed in as a count those operations already mean. The observer rules can derive some uptake distinctions from structured artifacts without an uptake flag.

**Challenged, for this API and these inputs.** Distinct states collapse at the calculator boundary when the distinction is not an input. In some dimensions, missing or absent observations can receive the same favorable value as positive evidence (E-12). Categorical labels sit close to hard cutoffs and some flip under a modest weight change. In the tested hub case, a NONE dominance-level classification coexisted with a named dominant agent (E-11).

**Unresolved.** Under the proposed observer inputs, acknowledgment-only cannot be separated from an ignored correction. `trace_change_to_correction` establishes content alignment, not causation. How a free-text plan becomes a commitment field is unspecified. No second person has coded a real exchange. E-14 remains UNRESOLVED. The Week 4 labels do not convert it into SURVIVES.

Nothing here says the constructs are false, or that the weights are the right ones. Calibration waits on a representation that can see the distinction.

## 7. Prioritized backlog

No core patch yet. Do not pass uptake through `repairs_successful` or `adjustments_made`.

1. Decide whether acknowledgment evidence may be added to the observer inputs. Without it, acknowledgment-only and ignoring stay the same observation.
2. Define how a natural-language plan becomes commitment fields, with examples, before treating `detect_plan_delta` as a reader of transcripts.
3. Define what evidence would support attribution rather than a match between the requested change and the observed delta.
4. Run the observer on exchanges we did not write to fit the rules, with a second coder.
5. Only after that, decide whether an uptake-derived value enters the Coheronmetry API, and as what.

Week 2's emergence formulation and the missing-evidence defaults stay open (I-08, I-12, I-13). They are not this cycle's next patch.

## 8. Transition to Orthogonal Signal

Cycle 1 suggests a split between a signal being present and a signal making a difference. That split is a hypothesis for Cycle 2, not a finding of this cycle.

The question to carry forward: can Orthogonal Signal establish that a valid corrective signal remains present and distinct, while the Coheronmetry observer determines whether that signal actually changes the relational trajectory?

Orthogonal Signal would be asking whether meaningful difference enters the field and stays available. The uptake observer asks whether that difference changes what is done next, rather than being only acknowledged, absorbed, or set aside. We have not tested Orthogonal Signal.

## Reproducibility

Checked 2026-10-05. The package commit is the code that was audited. The Week 2–4 notes and runners live outside that repository.

**Audited package**

- Repository: Coheronmetry, `/Users/orca/Documents/My_Program/Coheronmetry`
- Version: 0.2.0
- Commit: `7d0144bd225519f9069d7df5e46277853fe62c24`
- No local patches to the package

**Research environment**

- Python: 3.12.2 (`/opt/anaconda3/bin/python`)
- OS: macOS, arm64
- Research artifact commit: not separately versioned

Commands, from `coheronmetry_research/`:

```text
cd ../Coheronmetry && python -m pytest -q
cd week3 && python run.py
cd week4 && python test_corrective_uptake_observer.py
```

Week 2 runners are the `python <runner>.py` files under `week2/`. Predictions for those were frozen in the design notes before the runs.

Artifacts: `week1/evidence_ledger.md`, `week1/issue_log.md`, `week2/week2_evidence_ledger.md`, `week2/week2_issue_patch_log.md`, `week3/week3_evidence_ledger.md` (E-14), `week3/week3_issue_patch_log.md` (I-16), `week3/findings.md`, `week4/corrective_uptake_observation_spec.md`, `week4/test_corrective_uptake_observer.py`, `week4/corrective_uptake_test_results.json`.
