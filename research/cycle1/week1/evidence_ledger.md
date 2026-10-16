# Evidence Ledger

Coheronmetry 0.2.0, commit `7d0144bd`. Status is relative to the adapter and synthetic logs used; see each source.

| ID | Date | Claim or construct | Test | Result | Status | Source |
|---|---|---|---|---|---|---|
| E-01 | 2026-09-17 | Implementation matches documented algebra | Existing suite, unmodified | 91 passed | Implementation consistency only | `test_results.txt` |
| E-02 | 2026-09-22 | Non-Domination separates legitimate hub influence from domination | Week 2 Test 1: structure × regime, rho sweep | Structure effect 0.44 > domination effect 0.38; responsive hub 0.48 < covert dominator 0.54; ordering flips under single-weight changes | Falsified for this adapter; weight-sensitive | `week2/results/test1/` |
| E-03 | 2026-09-22 | Non-Domination detects loss of corrective influence | Week 2 Test 1: correction-deaf hub | ND gap 0.008 (AUC 0.58) while ground truth drops 0.90 → 0.10 | Falsified; no input channel | `week2/results/test1/` |
| E-04 | 2026-09-22 | ND rises with hub responsiveness | Week 2 Test 1: rho sweep | Monotonic 0.10 → 0.48, capped by structural penalty | Supported directionally | `week2/results/test1/summary_rho_sweep.csv` |
| E-05 | 2026-09-22 | Relational health reflects coordination quality | Week 2 Test 2: agreement × success | Success has no effect on R or ND; E2 Embodiment inverted (AUC 0.00); agree-fail > disagree-succeed in 36/36 settings | Falsified for this adapter | `week2/results/test2/` |
| E-06 | 2026-09-22 | "A collapsed dependency cannot be hidden by strength elsewhere" | Week 2 independent falsifier | 52/54 fields with one collapsed agent classified BENEFICIAL | Falsified at field level | `week2/results/falsifier/` |
| E-07 | 2026-09-22 | Emergence distinguishes distributed-information synthesis from repetition | Scenario 3 assessment | Not run: inputs are score vectors, outcome fixed by construction | Unresolved; needs content layer | `week2/findings_memo.md` |

> **Week 2 supersession note:** The provisional Week 1 entries E-02–E-07
> reference the originally anticipated `week2/results/` location. Week 2
> experiments were subsequently organized by scenario instead. Their completed
> evidence records and artifact paths are documented in E-08–E-12 in
> `week2/week2_evidence_ledger.md`. E-02–E-07 are retained unchanged as part of
> the Week 1 audit record.
>
> **Week 3 pointer:** Corrective-uptake evidence continues at E-14 in
> `week3/week3_evidence_ledger.md`. The issue log continues at I-16 in
> `week3/week3_issue_patch_log.md`.
