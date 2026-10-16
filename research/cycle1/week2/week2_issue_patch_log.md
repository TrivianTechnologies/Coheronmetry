# Week 2 Issue / Patch Log

Coheronmetry 0.2.0, commit `7d0144bd`. No patches applied; the repository is unmodified for the audit. IDs continue from `week1/issue_log.md`; E-IDs refer to `week2_evidence_ledger.md`.

Only I-14 is an ordinary implementation bug. I-07 to I-13 are construct / representation semantics questions, and I-15 is a calibration question: the evidence shows a problem, but not yet the correct design, so none of the formulas should change on the basis of Week 2 alone.

## I-07 — Missing observation / representation layer
- **Issue:** several theoretically relevant distinctions have no input channel: task outcome, coordinated vs. local adjustment, corrective influence, and distributed information / derivability. Extends Week 1 I-03, I-04.
- **Evidence:** E-08 (S1 A = B′); E-09 (P = C; F′ = P on Emb); E-10 (E vs. R not identifiable); E-11 (X_collision = H).
- **Impact:** healthy-looking scores can coexist with coordination failure or lost corrective influence; any conclusion about these constructs depends on an unspecified mapping.
- **Recommended action:** write an observation-layer spec (observable events → calculator inputs, counting rules), or declare these constructs out of scope for the field constants.
- **Patch status:** do not patch yet — specification required.

## I-08 — Missing evidence encoded as a score, not as missingness / confidence
- **Issue:** when evidence is absent, calculators return a score (0.5 or 1.0 depending on the path) with no signal that nothing was observed.
- **Evidence:** E-12 (absent = positive in both tests); E-08 (omitted feedback → Emb 0.5 vs. 0.0 for zero-valued feedback); E-09 (zero-mean acceptance → 0.5); E-10 (`previous_output=None` → persistence 0.5).
- **Impact:** a score cannot be read as positive evidence without knowing whether its inputs were observed; the defaults are inconsistent across dimensions.
- **Recommended action:** decide on a missingness / confidence policy (e.g. a separate "not observed" flag or confidence field) before choosing any numeric value. Do not unify defaults to 0.5 now.
- **Patch status:** design decision required.

## I-09 — Decision Concentration: zero decisions scores 1.0
- **Issue:** `total_decisions == 0` → HHI 0.0 → score 1.0, identical to perfectly balanced decisions.
- **Evidence:** E-12 (A_none = A_balanced = 1.0). A single decision drops the score 1.0 → 0.0 and flags that agent as `authoritarian_agent`. `non_domination.py:240–241, 252–256`; related to Week 1 I-01.
- **Impact:** the top score is ambiguous; the first observation causes a full-range jump.
- **Recommended action:** once I-08 is settled, return a missingness signal for zero decisions, or require a minimum count before scoring.
- **Patch status:** candidate semantics / API change after the missingness policy.

## I-10 — Emergence Suppression: zero attempts scores 1.0
- **Issue:** `synthesis_attempts == 0` → adoption default 0.5, then +0.5 centering → 1.0 at framing 0.
- **Evidence:** E-12 (B_none = B_positive = 1.0; one failed attempt → 0.5); E-09 (F_no_synthesis raises ND +0.10 over F). `non_domination.py:305–306, 322–323`.
- **Impact:** making no synthesis attempts scores better than attempting and failing.
- **Recommended action:** same policy as I-09; handle attempts = 0 as not observed rather than as a rate.
- **Patch status:** candidate semantics / API change after the missingness policy (depends on I-08).

## I-11 — Proposal Acceptance zero-mean discontinuity
- **Issue:** acceptance is scored by the CV of per-agent rates. Equal low rates (e.g. 1/5 each) → 1.0, but all-zero rates (or no proposals, since the rate becomes 0.0) → mean 0 → 0.5.
- **Evidence:** E-09 (P_zero −0.125 vs. P; F_zero crosses into EMERGING). `non_domination.py:185, 194–195`.
- **Impact:** a vanishingly small but equal acceptance rate scores 1.0, while zero scores 0.5; the score is level-blind above zero and discontinuous at zero.
- **Recommended action:** investigate intended semantics: is 0.5 meant as "no evidence" (see I-08) or as a low-acceptance penalty? Separate those two cases.
- **Patch status:** investigate semantics before patch.

## I-12 — Emergence B depends strongly on previous-output availability and group size
- **Issue:** `previous_output=None` sets persistence to 0.5, halving B. Novelty is the mean distance to all agents, so under the fixed COPY_FAR geometry, copying one agent gives B = (n−1)/n.
- **Evidence:** E-10 (COPY_FAR 0.75 → 0.375 without a prior output; B = 0.50 at n = 2 → 0.90 at n = 10). `emergence.py:345–353, 361–367`.
- **Impact:** phase and class labels can change with prior-output availability and group size even when the copied-output relation under test is held fixed.
- **Recommended action:** review the formulation (novelty aggregation, persistence default); not a parameter-tuning task.
- **Patch status:** formulation review, not parameter tuning.

## I-13 — Emergence B construct / API mismatch
- **Issue:** `formulation_b` operationalizes novelty through geometric distance between score vectors, while distributed information and individual derivability are not represented; under the tested representation, an exact copy of one participant can therefore outscore arithmetic aggregation.
- **Evidence:** E-10 (Part A audit; COPY_FAR B = 0.75 > AVG 0.50, rising to 0.90 at n = 10). `emergence.py:317, 335–337`.
- **Impact:** a high B cannot be read as emergence from distributed information.
- **Recommended action:** specify what information the construct needs (links to I-07), then decide whether B is reformulated or re-scoped.
- **Patch status:** reformulation / specification question.

## I-14 — S4 diagnostic attribution mismatch (MODERATE note)
- **Issue:** the MODERATE note is hard-coded: "Correction bias recommended on decision concentration", regardless of which dimension caused the level.
- **Evidence:** E-11 X_s: note names decision concentration, but decision concentration is 0.750 in both H and X_s; the only change is emergence suppression 1.000 → 0.000. `non_domination.py:487–491`.
- **Impact:** the diagnostic text misattributes the cause and would direct repair at the wrong dimension.
- **Recommended action:** remove the hard-coded dimension-specific recommendation, or define and test an attribution rule based on the component scores before generating a dimension-specific note; add a regression test using the X_s inputs.
- **Patch status:** patch now (ordinary implementation / documentation bug; to be submitted upstream, not applied in this audit copy).

## I-15 — Categorical labels are fragile at provisional weights and thresholds
- **Issue:** the conditions of most interest sit within 0.05 of a hard-coded cutoff, and some of their labels flip under a single 25% weight change (others within the tested ×0.5 to ×1.5 range), even though the orderings do not change.
- **Evidence:** E-13 (X_s flips at suppression ×0.75; F Recip flips at acknowledgment ×0.75; H at +0.026 above 0.80). Cutoffs are at `non_domination.py:74–82, 360`, `reciprocity.py:341, 345` and `embodiment.py:307, 312`. Related: E-08 (grounded at ≥ 0.6) and E-11 (sovereignty flip under framing).
- **Impact:** labels such as "sovereign", "NONE" and "reciprocal" can be read as findings when they are artifacts of placeholder values.
- **Recommended action:** meanwhile, report every label with its score and its margin to the cutoff. Treat the ND suppression and acceptance weights, the Reciprocity acknowledgment weight, and the 0.65 / 0.80 cutoffs as priority calibration targets, but defer numerical calibration until the representation and missingness questions in I-07 and I-08 are specified.
- **Patch status:** do not patch yet — calibration deferred until representation and missingness are specified.

---

Lower-priority observations, not registered as issues:
- `formulation_b` has no input validation: an empty output raises ZeroDivisionError, and mismatched lengths are silently truncated by `zip` (`emergence.py:352, 357, 550`).
- `dominance_level` and `dominant_agent` are computed independently (`non_domination.py:459, 472`; E-11). Document the relation.
