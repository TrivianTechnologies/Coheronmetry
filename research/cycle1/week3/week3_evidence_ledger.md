# Week 3 Evidence Ledger

Coheronmetry 0.2.0, commit `7d0144bd`. IDs continue from `week2/week2_evidence_ledger.md`.

## E-14 — Corrective uptake, representation boundary

- **Status:** UNRESOLVED. The Week 4 cases do not change this. They were written to fit the rules, and they are not a test on a real exchange.
- **Result:** E changes the plan and the constraint is resolved. I acknowledges the same correction and the plan stays put. Those two share inputs and scores (ND 1.000, Reciprocity 0.600, Embodiment 0.500 with nothing passed in). N's acknowledgment rate is 0.500. Write-up: `findings.md`.
- **Week 4 follow-up:** The observation specification is frozen for Cycle 1 as v0.1 (`../week4/corrective_uptake_observation_spec.md`). It defines the inputs, the five function contracts, and the classification rules. `test_corrective_uptake_observer.py` implements that spec. It does not receive an uptake flag. On four controlled structured conditions, effective uptake came out `SUBSTANTIVE_UPTAKE`, unrelated plan change came out `UNRELATED_CHANGE`, and no correction was left unclassified. Acknowledgment-only stayed `UNRESOLVED`, because those inputs do not record acknowledgment. A separate branch check, not a fifth condition, got `REJECTED_OR_OVERRIDDEN` when a later action put the changed field back. This shows the rules can be executed. It does not show the observer is reliable on real exchanges. `attributed` means the plan delta matches the requested change, not that the correction caused it.
- **Artifacts:** `design.md`, `run.py`, `results.json`. Week 4: `../week4/corrective_uptake_observation_spec.md`, `../week4/test_corrective_uptake_observer.py`, `../week4/corrective_uptake_test_results.json`.
