# Corrective Influence: Findings

Coheronmetry 0.2.0, commit `7d0144bd`. `run.py` against `design.md`. Raw output is `results.json`. Ledger: E-14. Issue: I-16.

## What we expected, and what came out

The episodes did what they were built to do. E moves the plan from A to B and the constraint is resolved. I raises the same correction, acknowledges it, and stays on A. N never has the exchange.

The hand predictions matched. E and I get the same calculator inputs, and the same measurements. That is because the mapping only reads `correction_raised` and `acknowledged`, and those two are the same in E and I. Changing I's plan and constraint and mapping again leaves the inputs alone. So this mapping is ignoring plan substance. The reason we were not willing to map it any other way is the source check in `design.md` §4.

| | E | I | N |
|---|---|---|---|
| Plan actually changed | yes | no | no |
| Non-Domination | 1.000, `none`, sovereign | same as E | same as E |
| Acknowledgment / Reciprocity | 0.600, reciprocal | same as E | 0.500, not reciprocal |
| Embodiment | 0.500, no dimensions passed | same as E | same as E |
| Drift / repair records written | none | none | none |

Drift and repair are 0 because `record_drift` and `record_repair` are never called. We did not ask the system whether the episode contained any, and it did not report that none occurred.

## Status

**UNRESOLVED.**

Section 4 of the design found no existing input for "the correction was taken up" or for the plan change that follows. The run then did the boring half: once we only pass counts the source already means, E and I land on the same inputs and the same scores.

E versus I is the result that matters. The behavior differs. The inputs match. The measurements match. Both are ND 1.000, Reciprocity 0.600, Embodiment 0.500, and Embodiment had no dimensions to compute. Same scores here means the plan change never got into the measurement. It does not mean a calculator saw the plan change and scored it badly.

N is the control where the exchange is missing. Reciprocity is 0.500 there and 0.600 for E and I, so the code can tell that a correction was spoken and acknowledged. E and I share 0.600, so it cannot tell that one of those acknowledgments was followed by a new plan. Reciprocity is counting what it says it counts. An acknowledgment and a real change of plan are different facts, and only the first one is in the input.

ND is 1.000 in all three. Its counts never included the plan. Week 2 already had this kind of collision (E-11). This run does not add a new Non-Domination result.

FAILS would mean the measurement received the contrast and still could not separate it, or separated it backwards. That is not what happened. The contrast stayed in the behavioral record.

## Limits

One made-up episode. One snapshot. Repair responsiveness and feedback integration were left out on purpose, so we would not type the uptake label into them. The zero drift and repair counts are the same choice: those functions were not called. No weight sweep.

## Next

The recommendation is I-16 in `week3_issue_patch_log.md`.
