# Week 3 Issue / Patch Log

Coheronmetry 0.2.0, commit `7d0144bd`. No patches applied. IDs continue from `week2/week2_issue_patch_log.md`.

## I-16 — Substantive plan change has no measurement input

- **Issue:** once a valid correction has been acknowledged, a later change in what the plan actually says still has nowhere to go in the current API. Extends I-03 and I-07. Source check: `design.md` §4.
- **Evidence:** E-14.
- **Impact:** what is missing is a rule for observing that the plan's substance changed, not a new coefficient.
- **Week 4 follow-up:** The candidate observation layer is frozen for Cycle 1 as v0.1 (`../week4/corrective_uptake_observation_spec.md`). It says how a plan-substance change could be derived, upstream of the calculators, from `plan_before`, `plan_after`, the correction, the named constraint, later actions, and a fixed window. No core field was added. Two representation questions stay open. Acknowledgment-only cannot be told from an ignored correction, because the inputs have no acknowledgment evidence, so an unchanged plan is not labeled `ACKNOWLEDGED_ONLY` or `REJECTED_OR_OVERRIDDEN`. Matching the requested change is content alignment, not causation. The first `evaluate_persistence()` signature lacked `plan_before`, so reversion could not be judged. The contract now takes `plan_before`. That was an interface correction, not a change to the classification rules, and it is not an uptake label.
- **Recommended action:** do not add a core field yet, and do not pass uptake through `repairs_successful` or `adjustments_made`. The open questions are whether acknowledgment evidence may be added to the input list, and what would count as attribution rather than alignment. Try the rule on material that was not written to fit it before promoting it.
- **Patch status:** do not patch yet.

N's reciprocity label flips between 0.500 and 0.600 because 0.60 is the cutoff. That is I-15, on an acknowledgment count. It does not get its own issue. It is not evidence about uptake.
