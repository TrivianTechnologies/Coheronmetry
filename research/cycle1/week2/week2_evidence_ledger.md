# Week 2 Evidence Ledger

Coheronmetry 0.2.0, commit `7d0144bd`. Synthetic controlled inputs; ground truth is metadata only; predictions frozen before runs; all pre-registered predictions matched. Status is relative to the current API and input representation. IDs continue from `week1/evidence_ledger.md`.

## E-08 — S1: agreement without successful coordination
- **Construct / claim:** whether high ND / Reciprocity can by themselves discriminate successful from unsuccessful coordination.
- **Contrast:** A (agree, success) vs. B (agree, failure, no adjustment) vs. B′ (agree, failure, adjusts); C/D = low-agreement counterparts.
- **Expected:** outcome invisible to ND and Recip; Embodiment tracks adjustment only.
- **Observed:** A = B′ on all three (ND 1.000, Recip 1.000, Emb 0.500); B − A: Emb −0.50 only. Low agreement costs ND −0.05 via suppression (C − A). Omitted feedback → Emb 0.500 in every condition, vs. 0.000 for zero-valued feedback.
- **Robustness:** adjustment magnitude 0.5 → 0.6 flips A, B′, C intermediate → grounded; ordering unchanged.
- **Status:** interpretation challenged (outcome-blind collision); Emb label placeholder-sensitive.
- **Artifacts:** `scenario1/scenario1_baseline_results.json`, `scenario1/scenario1_sensitivity_results.json`

## E-09 — S2: disagreement with successful coordination
- **Construct / claim:** whether the measurements distinguish productive disagreement from fragmentation, and whether disagreement itself changes the scores when integration is held constant.
- **Contrast:** C (agree, integrated) vs. P (disagree, integrated) vs. F (disagree, fragmented) vs. F′ (fragmented, local adjustment); variants F_no_synthesis, C_x_from_a1, P_zero, F_zero.
- **Expected:** P = C; F − P carried by acknowledgment (Reciprocity), synthesis suppression (ND), and adjustment (Embodiment); F′ = P on Emb.
- **Observed:** P − C = 0 on all three. F − P: ND −0.10, Recip −0.33 (reciprocal → intermediate), Emb −0.50. F′ − P: Emb 0.000.
- **Robustness:** F_no_synthesis raises ND +0.10 (no attempts beats failed attempts). Zero mean acceptance → 0.5 default: P_zero −0.125; F_zero crosses into EMERGING.
- **Status:** supported for encoded proxies. Interpretation challenged: coordinated vs. local adjustment is not distinguished, and success is outcome-blind.
- **Artifacts:** `scenario2/scenario2_baseline_results.json`

## E-10 — S3: emergence from distributed information (Formulation B)
- **Construct / claim:** Formulation B separates emergence from relay or copying.
- **Contrast:** Part A API audit (E vs. R worlds); Part B probes SAME / AVG / COPY_FAR / FAR.
- **Expected:** E/R not identifiable from the signature; COPY_FAR scores as emergence.
- **Observed:** no input carries information distribution or derivability. An exact copy of one participant receives B = 0.75, exceeding the arithmetic aggregation probe AVG = 0.50 (FAR 1.00), and the copied-output score increases with group size from 0.50 at n = 2 to 0.90 at n = 10.
- **Robustness:** `previous_output=None` halves B (COPY_FAR → 0.375). Under the current provisional classifier, COPY_FAR is additionally labeled beneficial at B = 0.75, only 0.05 above the 0.70 cutoff; this categorical label therefore does not carry the falsification claim.
- **Status:** Formulation B does not discriminate copying from the intended novelty construct under the tested representation (score-level evidence). E vs. R remains unresolved because the relevant informational distinction is not represented by the current API.
- **Artifacts:** `scenario3/scenario3_formulation_b_results.json`

## E-11 — S4: hub influence vs. domination
- **Construct / claim:** ND separates legitimate hub influence from domination and detects loss of corrective influence.
- **Contrast:** D (distributed) vs. H (hub, influence preserved) vs. X_s (suppression) vs. X_full (suppression + acceptance) vs. X_collision (influence lost, H-identical inputs).
- **Expected:** X_s − H carried by suppression only; X_collision = H.
- **Observed:** H ND 0.826 NONE / sovereign with `dominant_agent = H`. X_s − H −0.20 (suppression only; → MODERATE, not sovereign). X_full SEVERE. X_collision − H = 0.
- **Robustness:** framing is masked on H (clamp at full adoption) and floors on X_s at f ≥ 0.5 (sovereignty flips between f = 0.25 and 0.5). H is flagged as dominant at 4 of 7 decisions but reaches EMERGING only at 7 of 10.
- **Status:** supported for the encoded suppression proxy. Corrective-influence loss has no dedicated input channel in the tested representation. Interpretation challenged: NONE coexists with `dominant_agent`.
- **Artifacts:** `scenario4/scenario4_baseline_results.json`

## E-12 — Independent falsifier: missing vs. positive evidence
- **Construct / claim:** a high dimension score is distinguishable from having no relevant evidence.
- **Contrast:** positive / absent / negative on Decision Concentration (1,1,1,1 / 0,0,0,0 / 4,0,0,0) and on Emergence Suppression (4/4 / 0 attempts / 0/4).
- **Expected:** absent = positive in both tests.
- **Observed:** Decision Concentration 1.0 / **1.0** / 0.0; Suppression 1.0 / **1.0** / 0.5.
- **Robustness:** 0 → 1 discontinuity. One decision takes Decision Concentration 1.0 → 0.0; one failed attempt takes Suppression 1.0 → 0.5. The Suppression tie holds only at framing 0; separation at f > 0 comes from clamp saturation. The `{}` probe (secondary, excluded from the criterion) also gives 1.0.
- **Status:** falsified (score-only reading of 1.0 as positive evidence); no claim about what value missing evidence should get.
- **Artifacts:** `independent_falsifier/independent_falsifier_missing_evidence_results.json`

## E-13 — Parameter sensitivity: calculator weights and label thresholds
- **Construct / claim:** whether the S1/S2/S4 distinctions are robust to reasonable changes in provisional weights and thresholds. Exploratory, not pre-registered.
- **Contrast:** frozen S1/S2/S4 conditions re-run through their own runners, with one calculator's weights changed at a time: equal weights, or each supplied weight ×0.5, ×0.75, ×1.25, ×1.5 (ND 18 schemes, Recip 10, Emb 6). Threshold margins computed at baseline weights.
- **Expected:** none registered.
- **Observed:**
  - Orderings: S4 D > H = X_collision > X_s > X_full is unchanged in all 18 ND schemes. S1 orderings and the S2 baseline orderings (C, P, F, F′) are unchanged; only the default-driven P_zero moves. No weight change altered another calculator's score.
  - Labels: some flip under a single 25% weight perturbation. X_s MODERATE / not sovereign → EMERGING / sovereign with suppression ×0.75; F Reciprocity intermediate → reciprocal with acknowledgment ×0.75. Other labels also flip within the tested range: X_s with acceptance ×1.5, and X_full SEVERE → MODERATE with decision ×1.5 or suppression ×0.5.
- **Robustness:** threshold margins ≤ 0.05 for H and X_collision (+0.026 above 0.80), X_s (−0.024 below 0.65), F_zero (−0.025) and X_full (−0.042). Embodiment is weight-invariant here because only one dimension is supplied.
- **Status:** supported for directional orderings. Categorical labels for H, X_s, X_full and S2 F are weight- and threshold-sensitive and should not be reported without margins.
- **Artifacts:** `parameter_sensitivity/weight_threshold_sensitivity_results.json`
