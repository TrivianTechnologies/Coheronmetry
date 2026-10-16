# Scenario 3: Emergence From Distributed Information

## 1. Question

Does the Emergence measurement respond differently when a group produces
something **unavailable to any participant independently** than when agents
repeat, aggregate, or converge on information already present?

Round 1 tests **Formulation B only** (`emergence.py:317-369`), because it is
the only formulation with an explicit novelty component. A (trajectory
dynamics) and C (prediction error) are deferred.

## 2. Theoretical Ground Truth

Puzzle: candidates X, Y, Z. a1 knows X is impossible; a2 knows Y is
impossible; a3 knows exactly one candidate is valid. Only the combination
yields Z.

**Collective novelty** holds when:

1. no individual can derive the output before interaction;
2. the combined information is sufficient to derive it;
3. the group actually produces it.

| World | Z individually derivable before interaction? | Distributed info required? | Group output |
|---|---|---|---|
| **E** Emergent | No | Yes | Z |
| **R** Already present | Yes, by a1 | No | Z |
| **G** Aggregation | No | Yes | restates ¬X, ¬Y without deriving Z |

`individually_derivable`, `distributed_info_required`, and `derives_Z` are
recorded as ground-truth metadata. They are never encoded into any calculator
input.

## 3. Part A — Representational Adequacy Audit

**Question:** Using the repository's documented input semantics, is there a
specified mapping that makes E and R different?

Documented semantics (`emergence.py:335-337`): `output_vector` is "the joint
output vector [R, B, E, ND]"; `agent_vectors` is "each agent's individual
vector at time of output"; `previous_output` is "a prior emergent output".

Repository facts:

- No code produces `output_vector` or `agent_vectors`. `formulation_b` is
  called only by `EmergenceCalculator.calculate` (`emergence.py:476-479`);
  `EmergenceClassifier` uses Formulation A only (`monitors.py:417`).
- There are no tests of any Emergence formulation.
- No rule maps information distribution, individual derivability, or
  solution content to B's inputs.
- The input vector's third component (E) is itself an emergence score, so the
  documented semantics feed one emergence score into another (circularity
  risk; recorded, not resolved in Round 1).
- The class docstring's usage example `formulation_b(artifacts,
  agent_contributions)` (`emergence.py:240-241`) and README's "can the output
  be decomposed into individual contributions?" (`README.md:281`) imply
  content-level inputs that the signature does not accept.

**Pre-registered conclusion:** the defining distinction between E and R is
**not identifiable** from the current API without an external mapping rule.
This is stated as non-identifiability, not as B(E) = B(R): there is no
licensed basis for assigning E and R vectors at all. No mapping is invented
in Round 1.

## 4. Part B — Structural Probes of Formulation B

Calculator-level probes of what the implemented formula rewards. They are
not representations of E, R, or G and are not derived from the puzzle.

**Component isolation (fixed for all probes):**

- Every vector is constant across components (`[c, c, c, c]`), so
  coherence = 1.
- `previous_output` = a copy of `output_vector`, so persistence = 1. No probe
  uses the zero vector as output, because cosine similarity with a zero
  vector is 0 (`emergence.py:544-545`).
- Therefore **B = novelty** = min(1, mean Euclidean distance to agents / √dim)
  (`emergence.py:347-353`).
- Called through `calculate()` with only B's inputs and
  `sovereignty_score` = None, so composite = B and phase/class come from the
  implementation (`emergence.py:82-91, 552-577`).

| Probe | Agents | Output | Structural meaning | Predicted B | Phase / class |
|---|---|---|---|---|---|
| **SAME** | [.5]×4, [.5]×4 | [.5]×4 | everyone repeats the same thing | 0.00 | stagnation / stagnation |
| **AVG** | [0]×4, [1]×4 | [.5]×4 | arithmetic mean of inputs | 0.50 | corridor / neutral |
| **COPY-FAR** | [1]×4, [0]×4, [0]×4, [0]×4 | [1]×4 | exact copy of a1; others distant | **0.75** | **emergence / beneficial** |
| **FAR** | [0]×4 ×4 | [1]×4 | maximally distant (positive control) | 1.00 | emergence / beneficial |

Hand-derived, then checked once against the calculator on 2026-09-24; all
values and labels matched.

**Key predictions**

- **Aggregation receives nonzero novelty:** AVG = 0.50.
- **An exact copy of one participant is classified as emergent:** COPY-FAR =
  0.75 ≥ `EMERGENCE_THRESHOLD` 0.7 (`emergence.py:256`), class BENEFICIAL.
  Implemented novelty measures average geometric distance from participants,
  not whether the output was unavailable to every participant.

## 5. Part C — Sensitivity

| Check | Change | Predicted (checked) |
|---|---|---|
| Persistence default | `previous_output` = None | For these probes, persistence changes from 1.0 to 0.5, halving every nonzero B: SAME 0.00, AVG 0.25, COPY-FAR 0.375, FAR 0.50. COPY-FAR loses its emergence label. Under `previous_output` = None, Formulation B cannot exceed 0.5, because novelty ≤ 1, coherence ≤ 1, and default persistence = 0.5 (`emergence.py:362-367`) |
| Group size | COPY-FAR with n = 2, 3, 4, 5, 10 (one copied agent, n − 1 distant) | B = (n − 1)/n under this construction (coherence = persistence = 1; distant agents at maximal distance √dim): 0.50, 0.667, **0.75**, 0.80, 0.90. The same copied output becomes "emergent" at n ≥ 4 purely by adding distant participants |

## 6. What Counts as a Finding

- **Non-identifiability:** a theoretically defining distinction has no
  representation in the API (Part A).
- **Aggregation credited as novelty:** AVG > 0.
- **Copy credited as emergence:** COPY-FAR receives an emergence label.
- **Group-size dependence:** an unchanged output changes label as n changes.
- **Default dependence:** omitting `previous_output` changes a label.

Part A yields a **representation finding** (the construct has no specified
input mapping). Parts B and C yield **measurement-behavior findings** (what
the formula does with vectors supplied directly). They are reported
separately and are not combined into a single claim.

## 7. Record for Every Run

Probe ID; agent vectors; output vector; previous output (or None); B;
composite; phase; class; `formulations_computed`; notes. The API returns
only B, not its components; component values are not recomputed, because
the §4 isolation already fixes coherence and persistence at 1. For
Part A, record the repository facts in §3 with file and line references.
