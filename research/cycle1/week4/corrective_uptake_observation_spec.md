# Corrective Uptake Observation Specification

Classification rules frozen 2026-10-05, before `test_corrective_uptake_observer.py`. Those rules were not edited to make the test pass. The same day, after the runner, `evaluate_persistence` gained `plan_before`. The old signature could not check the reversion this section already described. `plan_before` was already an allowed input. No uptake flag was added.

This file is the definition. `test_corrective_uptake_observer.py` is one controlled implementation of it.

This sits outside the calculators. Week 3 (E-14, I-16) found no existing input for "the plan changed because the correction was taken up." This note says what an observer would look at, and how those observations get a label, before anyone adds a field.

Acknowledgment is not uptake. A score does not decide the label.

## 1. Purpose

Given one correction and the plan around it, say whether the plan afterwards changed in substance because of that correction.

The label is an observation. It is not a Coheronmetry score, and it is not filled in from a verdict we already prefer.

## 2. Scope and Non-Goals

In scope: one correction, the plan before it, the plan after it, the constraint the correction named, and what was done in a short window afterwards.

Out of scope:

- Whether the correction was a good idea. Validity is stipulated, as in the Week 3 claim, or left unresolved if nobody stipulated it.
- Repair responsiveness, feedback integration, and every other current calculator input. Those stay unused until this rule exists.
- A weight, a threshold, or a new coefficient.

## 3. Observable Inputs

These are the only materials the functions below may read.

### `plan_before`

The plan as it stood when the correction was offered. What it committed to, not how politely it was phrased.

### `plan_after`

The next plan or decision that counts as the group's plan. Restating the old plan in new words is still the old plan.

### `correction`

What was proposed as the change: who offered it, and which part of the plan it asked to change. "Good point" with no asked-for change is not a correction.

### `constraint_identified`

The constraint the correction says the current plan violates. If validity was stipulated, say so here. If it was not, the field stays empty and the label can come out unresolved.

### `subsequent_actions`

What was actually done after `plan_after`, inside the window: steps taken, decisions, or a later plan that puts `plan_after` back.

### `observation_window`

How far past the correction we agreed to look. One next plan is a legal window. Say which one was used. Do not lengthen it after seeing the label.

## 4. Function contracts

None of these returns "uptake" by itself. `classify_uptake` is the only one that returns a label, and it does that from the other four results by the rules in section 6.

### `detect_plan_delta(plan_before, plan_after) -> PlanDeltaResult`

Inputs: `plan_before`, the structured plan before the correction. `plan_after`, the structured next accepted plan.

Returns: `missing`, true if either plan is unavailable. `changed`, true if at least one commitment field differs. `changes`, those fields with their before and after values.

Rule: compare the commitment fields. A wording-only change is not a difference. In the controlled implementation the fields are already structured, so the comparison is equality of those values, not a reading of free text.

Example: route A becomes route B.

```text
{"missing": false, "changed": true, "changes": {"route": ["A", "B"]}}
```

### `evaluate_constraint_resolution(constraint_identified, plan_after, subsequent_actions) -> ConstraintResolutionResult`

Inputs: the named constraint, the next plan, and the later actions already inside the window.

Returns: `resolved`, `unresolved_constraint`, or `not_applicable`.

Rule: resolved when `plan_after` no longer contains the identified violation and no later action puts that violation back. `unresolved_constraint` when the violation is still there, or a later action restores it. `not_applicable` when no constraint was identified.

### `trace_change_to_correction(correction, plan_before, plan_after, subsequent_actions) -> AttributionResult`

Inputs: the correction, both plans, and the later actions. The controlled implementation compares the plans. It does not read the actions.

Returns: `attributed`, `unrelated`, `unclear`, or `not_applicable`.

Rule: compare the observed plan delta with the change the correction requested. `attributed` means the observed delta matches that requested change. That is content alignment. It does not show that the correction caused the change. If the plan changes on a different field, return `unrelated`. If the requested change lands together with other changes, so the record does not separate the stories, return `unclear`. If there is no plan delta, return `not_applicable`. Whether `attributed` should later be renamed is open, in section 10. The name stays for now.

### `evaluate_persistence(plan_before, plan_after, subsequent_actions, observation_window) -> PersistenceResult`

Inputs: both plans, the later actions, and the window those actions were already limited to.

Returns: `held`, `reverted`, or `not_in_window`.

Rule: find the commitment fields that differ between `plan_before` and `plan_after`. If a later action inside the window puts one of those fields back to its `plan_before` value, return `reverted`. If the changed commitment is still in force through the actions we have, return `held`. If the window is only `plan_after` and there is no later action, return `not_in_window`.

The function does not parse `observation_window`. The caller passes only the actions already inside it.

The first written signature was `evaluate_persistence(plan_after, subsequent_actions, observation_window)`. The runner showed that this cannot judge "restores `plan_before`." The signature above is the correction. Section 6 was not changed to make a case pass.

### `classify_uptake(plan_delta, constraint_resolution, attribution, persistence) -> UptakeClassification`

Inputs: only the four results above. Not the episode name. Not an uptake flag.

Returns: `SUBSTANTIVE_UPTAKE`, `ACKNOWLEDGED_ONLY`, `REJECTED_OR_OVERRIDDEN`, `UNRELATED_CHANGE`, or `UNRESOLVED`.

Rule: section 6, first match. With the current inputs, `ACKNOWLEDGED_ONLY` is not reached.

## 5. Classification Labels

### `SUBSTANTIVE_UPTAKE`

The plan's commitment changed, the change is the one the correction asked for, the named constraint is no longer violated, and the change is still in force inside the window.

### `ACKNOWLEDGED_ONLY`

The correction was recognized, and the plan's commitment did not change. This is the Week 3 ineffective case. The minimum inputs cannot show the recognition, so section 6 does not assign this label yet.

### `REJECTED_OR_OVERRIDDEN`

A change that matched the correction was later taken back inside the observation window. Explicit refusal, ignoring, or override may also belong here in principle, but the current minimum inputs do not distinguish refusal or ignoring from acknowledgment when the plan stays unchanged.

### `UNRELATED_CHANGE`

The plan did change, and that change is not the one the correction asked for.

### `UNRESOLVED`

The record is not enough to choose one of the four labels above. Missing plans, an unnamed constraint, or an attribution that could go either way all land here. This is an observation label for one episode. It is the same word as the Week 3 claim status, and it is not that status.

## 6. Classification Logic

Stop at the first rule that applies.

1. If `plan_before` or `plan_after` is missing, or `plan_delta.missing`: `UNRESOLVED`.
2. If `attribution` is `unclear`: `UNRESOLVED`.
3. If the plan did not change: `UNRESOLVED`. The inputs show a correction and an unchanged commitment. They do not show whether anyone acknowledged the correction or ignored it, so they cannot support `ACKNOWLEDGED_ONLY` or `REJECTED_OR_OVERRIDDEN`. See §10.
4. If the plan changed and `attribution` is `unrelated`: `UNRELATED_CHANGE`.
5. If `persistence` is `reverted`: `REJECTED_OR_OVERRIDDEN`.
6. If `constraint_identified` is empty, or a named constraint is still violated: `UNRESOLVED`. Calling this substantive uptake of a valid correction needs that evidence. A plan that moved, while the violation is still there, has not answered the correction.
7. Otherwise the plan changed, the change traces to the correction, the named constraint is no longer violated, and the change was not reverted within the declared window: `SUBSTANTIVE_UPTAKE`.

## 7. Ambiguity and Missing-Evidence Rules

- No plan text, no label other than `UNRESOLVED`. Do not fill the gap with a neutral score.
- An unchanged plan is not upgraded because someone might have said "good point." The current inputs cannot tell that from the correction being ignored, so the label stays `UNRESOLVED`.
- Two plausible stories and one record: `attribution = unclear`, then `UNRESOLVED`. Do not pick the story that makes the episode look like uptake.
- A window chosen after the label is known does not count. Record the window with the inputs.

## 8. Validation Conditions

Use the Week 3 episodes as a check on the rules, not as proof that the rules are the right ones. The plans there were labels ("A", "B"), not real text, so this only checks that the branches fire.

| Episode | What the rules should return |
|---|---|
| E. Correction named a constraint, plan A becomes B, constraint resolved, nothing reverts it | `SUBSTANTIVE_UPTAKE` |
| I. Same correction, plan stays A, constraint remains. Week 3 also had an acknowledgment, which these inputs do not record | `UNRESOLVED`, not `ACKNOWLEDGED_ONLY` |
| N. No correction offered | No classification. The functions are not called. |
| Plan changes for a reason other than the correction | `UNRELATED_CHANGE` |
| Plan changes as asked, then a later action inside the window restores the old commitment | `REJECTED_OR_OVERRIDDEN` |
| `plan_after` was never recorded | `UNRESOLVED` |

A second person, given the same inputs and these rules, should reach the same label. That check is still to be done on a real exchange. The table above does not replace it.

## 9. Relationship to Current Coheronmetry

Nothing here is passed to Non-Domination, Reciprocity, Embodiment, `RepairResponsivenessMeasure`, or `FeedbackIntegrationMeasure`.

Week 3 already showed the tempting shortcut: set `adjustments_made` or `repairs_successful` from the label, and the calculator repeats it. I-16 still stands. No new field until this rule has been tried on material we did not write to fit it.

If a later calculator input is added, it should be computed from these observations. It should not be a column named uptake that the caller types.

## 10. Open Questions

- Whether acknowledgment needs to be represented as an additional observable input. The current minimum input set distinguishes plan change from no plan change, but does not by itself distinguish an acknowledged correction from an ignored correction. Sarasha's list may be exhaustive, or it may allow that evidence to be added. Not decided here, and not added as a field.
- What evidence is sufficient for `trace_change_to_correction()` to support attribution rather than temporal or semantic alignment alone? Matching "the correction asked for B, and the plan became B" does not show that B happened because of the correction. The return value stays `attributed` for now, because that is the word already in use. Renaming it to something like `aligned` is a naming question, not a change made here.
- How long `observation_window` should be when the episode is a real transcript rather than one next plan.
- What counts as "the same commitment" when two wordings are close but not identical. The rule needs examples before anyone codes `detect_plan_delta`.
- Whether a stipulated constraint is enough, or whether the observer also has to be able to show the violation from the plan text.
- Who does the second coding pass, and on what exchanges.
