# Claims and Questions Log

Task 4, Coheronmetry 0.2.0, commit `7d0144bd225519f9069d7df5e46277853fe62c24`.

Notes from reading README, ARCHITECTURE, VERIFICATION, CHANGELOG, plus the field-constant code, tests, and examples. This is a working list, not a verdict.

VERIFICATION.md already says passing tests only show implementation consistency. They do not validate the constructs, the measurements, the thresholds, or any real-world relational effect. That is the ceiling for what the baseline suite can settle.

---

## Q1. Do the scores measure what they claim?

The repo treats Reciprocity, Embodiment, Emergence, and Non-Domination as measurable properties of a relational field. I do not yet see how a number such as Reciprocity = 0.8 is produced from an actual AI conversation, or why that procedure should count as measuring reciprocity. Would a second person coding the same exchange get a similar number?

What I can see in the code is aggregation of counts and 0–1 values the caller already supplied. The examples do not even do that; they drop in hand-set vectors.

Assumptions and gaps:

- Words like "grounded claim," "acknowledgment," "decision," and "reframing" need someone to label them. There is no coding guide and no inter-rater check.
- Missing data is sometimes filled with a neutral score instead of left missing.
- I have not seen evidence that the four constants are distinct constructs rather than overlapping proxies.

Things worth testing later: write a short annotation guide and get two raters on the same transcript; run the calculators on exchanges that were labeled independently; see whether the scores do more than track turn count or activity.

---

## Q2. Why product for RCD?

The relational condition is `RCD = Reciprocity × Embodiment × Non-Domination`. The point is clear enough: a high score on one dimension should not cover for a collapse on another.

Multiplication does that, but so do min, harmonic mean, geometric mean, and a hard threshold. The tests show the product is implemented correctly. The changelog says that does not make it empirically valid. So the open question is why this rule, and whether it is better than the others.

Also sitting in the code: a corridor check that uses thresholds (`min(R, B, N) >= 0.7`). It is not obvious which of those two rules is the one that matters.

Assumptions and gaps:

- R, B, and N are being treated as comparable numbers with a meaningful zero.
- Product shrinks the scale. Three 0.8s give 0.512, which is easy to misread.
- I have not found a comparison against the other non-compensatory rules.

Later: put the same examples through product / min / harmonic / geometric / threshold and see which ranking matches an independent judgment of "the field is in bad shape." Also poke one input with a coding error and see how violently each rule moves.

---

## Q3. Emergence, or just something new?

The claim is that emergence is structure formed between agents that neither one had alone. The question is how you would tell that apart from ordinary novelty, a random sample, a bad prediction, or a model saying something unexpected.

There are several formulas. Some of them run on the R/B/E/ND score vectors, not on the actual joint text. The repo also lists "emergence vs statistical novelty" as an open problem, which matches what the implementation looks like.

Assumptions and gaps:

- Movement in the monitoring scores is not the same thing as a new structure in the output.
- Prediction error can just mean noise or a poorly calibrated forecast.
- "New" is not the same as "could not have come from one agent."

Later: compare a joint run with each agent working alone; check whether the "emergent" bit also shows up if you only change temperature or seed; see if the new structure is still there a few turns later; include boring controls (repetition, shuffle, high-temperature junk).

---

## Q4. Do five similar model answers support the thesis?

README says five systems, each without the others' answers, converged on "the relationship itself as a measurable object," and that this convergence was emergent and already demonstrates the thesis.

I would need to know what "independent" and "converged" meant in that run, how the setup was controlled, and why agreement among models would count as emergence or as evidence that a relational field exists and can be measured.

The repo says the models could not see one another. I have not found the prompts, the full outputs, a pre-set definition of convergence, or any controls.

Assumptions and gaps:

- Not seeing sibling answers is only one kind of independence. Shared training data and a shared prompt still sit in the background.
- Several models saying "relationship matters" is a long way from "this field is real and these scores measure it."
- Even a clean replication of the agreement would still need a separate argument before it counted as emergence.

Later: rerun with saved prompts and model versions; lock the convergence criteria before reading the answers; add repeats, paraphrased prompts, a human condition, and a null prompt; keep this episode out of the measurement-validity file.

---

## Setup notes

- The pytest suite checks the software. It does not validate the science.
- The example "ensemble" is synthetic vectors, not live models.
- The missing piece is the observation layer: how a real transcript becomes the numbers the calculators eat.
- Several cutoffs and default fills look like implementation choices. I have not seen the calibration.
- Baseline tests were run on unmodified code; I am not treating that pass as an answer to Q1–Q4.

---

## Status

17 September 2026. Coheronmetry 0.2.0, `7d0144bd`.

Open: Q1 measurement validity, Q2 RCD aggregation, Q3 emergence vs novelty, Q4 five-model evidence.

Closed: none. No construct-validation experiments yet.
