# Issue / Patch Log

Coheronmetry 0.2.0, commit `7d0144bd`. No patches applied; baseline preserved.

| ID | Date | Location | Issue | Evidence | Patch status |
|---|---|---|---|---|---|
| I-01 | 2026-09-22 | `non_domination.py` `DecisionConcentrationMeasure.score` | Normalizes by the number of dictionary entries. Omitting zero-decision agents makes a hub that makes every decision score 1.0 instead of 0.0. | E-02; Test 1 adapter check | Not patched. Document convention or normalize by participant count. |
| I-02 | 2026-09-22 | `monitors.py` `FieldMonitor.observe` | Composite and dissonance gate use per-constant means across agents, so one collapsed agent is averaged away. Contradicts README non-compensation claim. | E-06 | Not patched. Candidate: gate on minimum per-agent RCD. |
| I-03 | 2026-09-22 | Non-Domination inputs | No input for correction uptake. Loss of corrective influence is invisible unless it shifts overall proposal acceptance. | E-03 | Design question, not a code fix. |
| I-04 | 2026-09-22 | Field Constant inputs | No input for task outcome. Feedback integration rewards adjustment, so successful groups can score lower on Embodiment. | E-05 | Design question. |
| I-05 | 2026-09-22 | `non_domination.py` docstring | States Non-Domination is "weighted highest in the CoherenceVector composite"; RCD is an unweighted product. | Code reading | Documentation only. |
| I-06 | 2026-09-17 | `reciprocity.py` `ContributionRecord.acknowledgment_rate` | Denominator is `max(1, 1)`, always 1. | Code reading (Week 1) | Not patched. |
