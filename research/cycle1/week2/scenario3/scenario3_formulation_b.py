"""Scenario 3, Round 1: Formulation B audit and structural probes. See scenario3_design.md.

E / R / G are ground-truth worlds for the Part A audit only; they are never
passed to a calculator. Only the Part B probes and Part C sweeps call
EmergenceCalculator.
"""

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path

import coheronmetry
from coheronmetry.field_constants import EmergenceCalculator

# Design §2. Metadata only.
WORLDS = {
    "E": {"individually_derivable": False, "distributed_info_required": True,
          "derives_Z": True, "group_output": "Z"},
    "R": {"individually_derivable": True, "derivable_by": "a1",
          "distributed_info_required": False, "derives_Z": True, "group_output": "Z"},
    "G": {"individually_derivable": False, "distributed_info_required": True,
          "derives_Z": False, "group_output": "restates not-X, not-Y"},
}

# Design §3. Static repository facts; the signature is also read live below.
AUDIT_FACTS = [
    ("documented output_vector semantics: 'the joint output vector [R, B, E, ND]'", "emergence.py:335"),
    ("documented agent_vectors semantics: 'each agent's individual vector at time of output'", "emergence.py:336"),
    ("documented previous_output semantics: 'a prior emergent output'", "emergence.py:337"),
    ("formulation_b is called only by EmergenceCalculator.calculate", "emergence.py:476-479"),
    ("EmergenceClassifier uses Formulation A only", "monitors.py:417"),
    ("no tests exercise any Emergence formulation", "tests/"),
    ("no code maps information distribution, derivability, or solution content to B inputs", "repository-wide"),
    ("input component E is itself an emergence score (circularity risk)", "emergence.py:335"),
    ("usage example implies content inputs the signature does not accept", "emergence.py:240-241"),
    ("README describes decomposition into contributions; formula computes distance only", "README.md:281"),
]

Z4 = [0.0] * 4
O4 = [1.0] * 4
H4 = [0.5] * 4

# Design §4. previous_output = copy of output, so persistence = 1; constant
# components, so coherence = 1; therefore B = novelty.
PROBES = {
    "SAME":     {"agents": [H4, H4],             "output": H4},
    "AVG":      {"agents": [Z4, O4],             "output": H4},
    "COPY_FAR": {"agents": [O4, Z4, Z4, Z4],     "output": O4},
    "FAR":      {"agents": [Z4, Z4, Z4, Z4],     "output": O4},
}

GROUP_SIZES = [2, 3, 4, 5, 10]

# Design §4-§5 predictions: (B, phase, class).
EXPECTED = {
    ("probe", "SAME"):          (0.0,    "stagnation", "stagnation"),
    ("probe", "AVG"):           (0.5,    "corridor",   "neutral"),
    ("probe", "COPY_FAR"):      (0.75,   "emergence",  "beneficial"),
    ("probe", "FAR"):           (1.0,    "emergence",  "beneficial"),
    ("prev_none", "SAME"):      (0.0,    "stagnation", "stagnation"),
    ("prev_none", "AVG"):       (0.25,   "forming",    "neutral"),
    ("prev_none", "COPY_FAR"):  (0.375,  "forming",    "neutral"),
    ("prev_none", "FAR"):       (0.5,    "corridor",   "neutral"),
    ("group_size", 2):          (0.5,    "corridor",   "neutral"),
    ("group_size", 3):          (0.6667, "corridor",   "neutral"),
    ("group_size", 4):          (0.75,   "emergence",  "beneficial"),
    ("group_size", 5):          (0.8,    "emergence",  "beneficial"),
    ("group_size", 10):         (0.9,    "emergence",  "beneficial"),
}
TOL = 5e-4


def run(part, key, agents, output, previous):
    r = EmergenceCalculator().calculate(
        output_vector=output,
        agent_vectors=agents,
        previous_output=previous,
    )
    exp_b, exp_phase, exp_class = EXPECTED[(part, key)]
    mismatches = []
    if abs(r.score_b - exp_b) > TOL:
        mismatches.append(f"B: expected {exp_b}, got {r.score_b}")
    if r.phase.value != exp_phase:
        mismatches.append(f"phase: expected {exp_phase}, got {r.phase.value}")
    if r.emergence_class.value != exp_class:
        mismatches.append(f"class: expected {exp_class}, got {r.emergence_class.value}")
    return {
        "part": part,
        "key": key,
        "agent_vectors": agents,
        "output_vector": output,
        "previous_output": previous,
        "sovereignty_score": None,
        "score_b": r.score_b,
        "composite": r.composite_score,
        "phase": r.phase.value,
        "emergence_class": r.emergence_class.value,
        "formulations_computed": r.formulations_computed,
        "notes": r.notes,
        "prediction_mismatches": mismatches,
    }


def main():
    sig = inspect.signature(EmergenceCalculator.formulation_b)
    audit = {
        "formulation_b_signature": str(sig),
        "facts": [{"fact": f, "source": s} for f, s in AUDIT_FACTS],
        "conclusion": (
            "The defining distinction between E and R is not identifiable from the "
            "current API without an external mapping rule. No mapping is invented."
        ),
        "worlds": WORLDS,
    }

    runs = []
    for name, p in PROBES.items():
        runs.append(run("probe", name, p["agents"], p["output"], list(p["output"])))
    for name, p in PROBES.items():
        runs.append(run("prev_none", name, p["agents"], p["output"], None))
    for n in GROUP_SIZES:
        runs.append(run("group_size", n, [O4] + [Z4] * (n - 1), O4, list(O4)))

    print("Part A: representational adequacy audit")
    print(f"  formulation_b{sig}")
    for f, s in AUDIT_FACTS:
        print(f"  - {f}  [{s}]")
    print(f"  => {audit['conclusion']}")

    headings = {
        "probe": "Part B: structural probes (previous_output = output)",
        "prev_none": "Part C: previous_output = None",
        "group_size": "Part C: COPY_FAR by group size n",
    }
    for part, title in headings.items():
        print(f"\n{title}")
        for r in (x for x in runs if x["part"] == part):
            status = "match" if not r["prediction_mismatches"] else "MISMATCH: " + "; ".join(r["prediction_mismatches"])
            label = f"n={r['key']}" if part == "group_size" else r["key"]
            print(f"  {label:9} B={r['score_b']:.4f}  phase={r['phase']:10} "
                  f"class={r['emergence_class']:10} {status}")

    out = {
        "scenario": "scenario3",
        "round": 1,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "coheronmetry_version": coheronmetry.__version__,
        "part_a_audit": audit,
        "runs": runs,
        "all_predictions_matched": all(not r["prediction_mismatches"] for r in runs),
    }
    out_path = Path(__file__).with_name("scenario3_formulation_b_results.json")
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved {out_path.name}")


if __name__ == "__main__":
    main()
