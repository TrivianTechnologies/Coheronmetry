# Week 2 Findings Memo: Can Coheronmetry Tell Relational Conditions Apart?

Coheronmetry 0.2.0, commit `7d0144bd`. The full numbers and artifact paths are in `week2_evidence_ledger.md` (E-08 to E-13) and `week2_issue_patch_log.md` (I-07 to I-15).

## 1. What this week was for

This was not a calibration exercise. The question was simpler: when we change a relational condition in a controlled way, do the measurements move, and in the direction theory says they should? And do those differences hold up when we change the provisional weights and thresholds?

Here is how each of the four proposed scenarios held up as a test:

| Scenario | Usable as a falsification target? | What we did |
|---|---|---|
| S1 Agreement without coordination | Yes, with scope limits | Kept it. Varied outcome independently of the adjustment and agreement proxies the calculators can see. |
| S2 Disagreement with coordination | Yes | Kept it. Varied disagreement independently of integration vs. fragmentation. |
| S3 Distributed-information emergence | Not as stated. The current API has no way to express it | Replaced it with an audit of what `formulation_b` can represent, plus a few structural probes. We did not invent a mapping from information to vectors. |
| S4 Hub influence vs. domination | Yes | Kept it. Separated structural asymmetry from encoded suppression, and added a control where corrective influence is lost but the inputs are identical. |

S3 not being expressible through the current API is a result in its own right. My own falsifier, on missing evidence, is in §4.

## 2. Method

We fed synthetic, controlled inputs straight into the real calculators. Ground truth (outcome, coordination, corrective influence, whether evidence exists) was kept as metadata and never passed in. No observation layer was invented.

Before each run we worked out the expected scores by hand from the source code and froze them. Every prediction matched, in all five pre-registered runners. That tells us the experiments read out what we think they do and that we understand the code. It says nothing about whether the constructs are valid. That evidence comes from the collisions, the sensitivities, and the places where what the code can see doesn't line up with the condition we set up.

The weight and threshold check was exploratory, not pre-registered. We changed one calculator's weights at a time: equal weights, or one supplied weight scaled by 0.5 to 1.5. Thresholds are hard-coded, so for those we just measured how far each score sits from the nearest cutoff.

To rerun anything: use a Python environment with coheronmetry at the commit above, go into the runner's folder, and run `python <runner>.py`.

## 3. Main findings

**F1. The thing we want to measure often isn't an input.**
- **Task outcome.** ND and Reciprocity don't see it at all. In S1, a group that succeeds (A) and one that fails (B′) score the same on all three calculators. In S2, disagreeing-but-successful (P) equals agreeing-and-successful (C).
- **Kind of adjustment.** Embodiment can't tell coordinated adjustment from each agent adjusting on its own: S2 F′ = P.
- **Corrective influence.** There's no channel for it. In S4, a hub that has stopped taking correction (X_collision) has exactly the same inputs as a healthy hub (H), so both get ND 0.826.
- **Emergence.** The defining distinction between real emergence (E) and relay (R) is not represented in `formulation_b`'s inputs, so the two cannot be directly tested as stated. Worse, under the available vector representation, an exact copy of one participant scores B = 0.75, higher than simple averaging (0.50). The copy's score also climbs with group size, from 0.50 at n = 2 to 0.90 at n = 10. The classifier labels the copy "beneficial", but that's only 0.05 above the 0.70 cutoff, so we don't lean on the label.

**F2. When a proxy is supplied, the calculators respond sensibly.** In S2, the gap between productive disagreement (P) and fragmentation (F) comes from acknowledgment and adjustment. In S4, the whole −0.20 gap between X_s and H comes from emergence suppression and nothing else.

**F3. Missing evidence gets an ordinary score, not a "don't know".** Depending on the dimension, the default is 0.5 or 1.0, and in some cases observing nothing scores as well as, or better than, clear positive evidence.

**F4. Several core dimensions measure how evenly things are spread, not how much or how well.** Four of four proposals accepted per agent and one of four per agent both score 1.0. In S4, H is rated "no dominance / sovereign" while the same result names H as the dominant agent.

**F5. In the tested contrasts, a simple raw proxy can discriminate as well as the composite.** In S2 the acknowledgment rate alone separates P from F; in S4 the adoption and reframing counts alone separate H from X_s. S3 is different: no simple observable available to the current API captures the distributed-information distinction. Where one construct bled into another, it came from how the inputs were defined, not from the weights.

## 4. Independent falsifier: missing evidence

This one came from noticing the default-value behavior across scenarios, not from the PI's list. The question: can a high score be told apart from simply having no evidence?

| | positive | absent | negative |
|---|---|---|---|
| Decision Concentration | 1.0 | **1.0** | 0.0 (a1 flagged authoritarian) |
| Emergence Suppression | 1.0 | **1.0** | 0.5 |

No. Both dimensions can tell observed failure from no observation, but not no observation from clear success. This doesn't say what missing evidence *should* score, only that 1.0 currently means two different things. The first observation also causes a big jump: a single decision takes Decision Concentration from 1.0 to 0.0.

## 5. Robustness

- **Orderings hold.** Across all 18 ND weight schemes, S4 stays D > H = X_collision > X_s > X_full, and the S1 and S2 baseline orderings don't change.
- **Labels don't.** X_s's sovereignty and S2 F's Reciprocity label each flip with a single 25% weight change; X_full's severity flips at 50%. H sits only 0.026 above the 0.80 cutoff, and X_s is 0.024 below 0.65.
- **Inputs matter too.** S1's Embodiment label flips when adjustment magnitude goes from 0.5 to 0.6, and S3's score halves if there's no previous output.

## 6. What holds up, and what doesn't

**Earns its place so far.** Supplied proxies such as acknowledgment and synthesis suppression moved the dimension they feed, in the expected direction and in isolation, and the orderings survived every weight change we tried.

**Challenged** (for the current API and inputs):
1. High ND or Reciprocity can't by itself show that coordination worked (the S1 and S2 collisions).
2. Formulation B doesn't separate copying from the novelty it's meant to capture. This rests on the scores, not the label (F1).
3. "No dominance" doesn't mean no agent is flagged as dominant (S4 H).
4. A 1.0 can't be read as positive evidence unless you know something was actually observed (§4).

**Needs recalibration.** Weights and thresholds, especially the ND suppression and acceptance weights, the Reciprocity acknowledgment weight, and the 0.65 / 0.80 cutoffs. Until then, treat labels as provisional and report them with their margins.

**Needs reformulation or a spec.** How missing evidence is represented, and the observation layer that turns interaction into inputs. If Formulation B is meant to capture emergence from distributed information rather than geometric novelty, it needs reformulating or re-scoping, and in its current interpretation it may not survive.

**Still open.**
- Whether any observation layer could supply outcome, corrective influence and informational novelty from real interactions.
- S1's scope. We tested static snapshots, with agreement defined through proposal acceptance and synthesis inputs. We didn't model agreement growing over time, test exchange-trajectory dynamics, or look at linguistic coherence in transcripts. The outcome-blind result applies to the static setup we tested, not to those.
- Everything here used synthetic inputs, so none of it speaks directly to scores computed from real transcripts.

## 7. Next questions

1. **Observation layer:** which observable events map to which inputs, and how are they counted? This has to come before any tuning.
2. **Missingness:** should each dimension report "not observed" or a confidence value instead of a default score, consistently across dimensions?
3. **Missing constructs:** should task success, corrective influence and informational novelty become inputs, or be declared out of scope?
4. **Calibration last:** tuning weights and thresholds now would just be fitting placeholders.
