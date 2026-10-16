"""Independent falsifier: missing evidence vs. positive evidence.
See independent_falsifier_missing_evidence_design.md.

Ground truth (positive / absent / negative) is metadata only and is never
passed to a measure. Dimension-level only: no composite calculator is called.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import coheronmetry
from coheronmetry.relational_state import AgentID
from coheronmetry.field_constants import (
    DecisionConcentrationMeasure,
    EmergenceSuppressionMeasure,
)

AGENTS = [AgentID(f"a{i}") for i in range(1, 5)]

# Design §4. decisions per agent, in AGENTS order.
TEST_A = {
    "A_balanced":     {"ground_truth": "positive", "decisions": [1, 1, 1, 1]},
    "A_none":         {"ground_truth": "absent",   "decisions": [0, 0, 0, 0]},
    "A_concentrated": {"ground_truth": "negative", "decisions": [4, 0, 0, 0]},
}

# Design §5. syntheses_reframed = 0; framing = 0.0 at baseline.
TEST_B = {
    "B_positive": {"ground_truth": "positive", "attempts": 4, "adopted": 4},
    "B_none":     {"ground_truth": "absent",   "attempts": 0, "adopted": 0},
    "B_failed":   {"ground_truth": "negative", "attempts": 4, "adopted": 0},
}

# Design §6 sensitivity: first observation appears.
A_FIRST = {"A_one_decision": {"ground_truth": "negative", "decisions": [1, 0, 0, 0]}}
B_FIRST = {
    "B_one_adopted": {"ground_truth": "positive", "attempts": 1, "adopted": 1},
    "B_one_failed":  {"ground_truth": "negative", "attempts": 1, "adopted": 0},
}
FRAMINGS = [0.0, 0.5, 1.0]

# Design §6 predictions. A: (score, authoritarian_agent). B: score.
EXPECTED_A = {
    "A_balanced":     (1.0, None),
    "A_none":         (1.0, None),
    "A_concentrated": (0.0, "a1"),
    "A_one_decision": (0.0, "a1"),
}
EXPECTED_B = {
    ("B_positive", 0.0): 1.0, ("B_none", 0.0): 1.0,  ("B_failed", 0.0): 0.5,
    ("B_positive", 0.5): 1.0, ("B_none", 0.5): 0.75, ("B_failed", 0.5): 0.25,
    ("B_positive", 1.0): 1.0, ("B_none", 1.0): 0.5,  ("B_failed", 1.0): 0.0,
    ("B_one_adopted", 0.0): 1.0,
    ("B_one_failed", 0.0): 0.5,
}
TOL = 1e-9


def run_a(name, cfg):
    by_agent = dict(zip(AGENTS, cfg["decisions"]))
    total = sum(cfg["decisions"])
    m = DecisionConcentrationMeasure(decisions_by_agent=by_agent, total_decisions=total)
    exp_score, exp_auth = EXPECTED_A[name]
    mismatches = []
    if abs(m.score - exp_score) > TOL:
        mismatches.append(f"score: expected {exp_score}, got {m.score}")
    if m.authoritarian_agent != exp_auth:
        mismatches.append(f"authoritarian: expected {exp_auth}, got {m.authoritarian_agent}")
    return {
        "test": "A", "condition": name, "ground_truth": cfg["ground_truth"],
        "inputs": {"decisions_by_agent": {str(a): c for a, c in by_agent.items()},
                   "total_decisions": total},
        "hhi": m.concentration_ratio,
        "score": m.score,
        "authoritarian_agent": m.authoritarian_agent,
        "prediction_mismatches": mismatches,
    }


def run_b(name, cfg, framing):
    m = EmergenceSuppressionMeasure(
        synthesis_attempts=cfg["attempts"],
        syntheses_adopted=cfg["adopted"],
        syntheses_reframed=0,
        dominant_agent_framing=framing,
    )
    exp = EXPECTED_B[(name, framing)]
    mismatches = [] if abs(m.score - exp) <= TOL else [f"score: expected {exp}, got {m.score}"]
    return {
        "test": "B", "condition": name, "ground_truth": cfg["ground_truth"],
        "inputs": {"synthesis_attempts": cfg["attempts"], "syntheses_adopted": cfg["adopted"],
                   "syntheses_reframed": 0, "dominant_agent_framing": framing},
        "adoption_rate": m.adoption_rate,
        "reframing_rate": m.reframing_rate,
        "score": m.score,
        "prediction_mismatches": mismatches,
    }


def falsification(runs, positive, absent):
    s = {r["condition"]: r["score"] for r in runs}
    delta = s[absent] - s[positive]
    return {
        "positive": positive, "absent": absent,
        "positive_score": s[positive], "absent_score": s[absent], "delta": delta,
        "discriminates": abs(delta) >= TOL,
    }


def status(r):
    return "match" if not r["prediction_mismatches"] else "MISMATCH: " + "; ".join(r["prediction_mismatches"])


def main():
    primary_a = [run_a(n, c) for n, c in TEST_A.items()]
    primary_b = [run_b(n, c, 0.0) for n, c in TEST_B.items()]
    first_a = [run_a(n, c) for n, c in A_FIRST.items()]
    first_b = [run_b(n, c, 0.0) for n, c in B_FIRST.items()]
    framing_sweep = [run_b(n, c, f) for f in FRAMINGS for n, c in TEST_B.items()]

    empty = DecisionConcentrationMeasure(decisions_by_agent={}, total_decisions=0)
    probe = {
        "note": "Secondary API-semantics check; not part of the falsification criterion.",
        "registered_zero_counts_score": primary_a[1]["score"],
        "empty_dict_score": empty.score,
        "empty_dict_hhi": empty.concentration_ratio,
    }

    verdicts = {
        "A": falsification(primary_a, "A_balanced", "A_none"),
        "B": falsification(primary_b, "B_positive", "B_none"),
    }

    print("Primary: Test A (Decision Concentration)")
    for r in primary_a:
        print(f"  {r['condition']:15} {r['ground_truth']:9} score={r['score']:.4f}  "
              f"authoritarian={r['authoritarian_agent']}  {status(r)}")
    print("Primary: Test B (Emergence Suppression, framing=0)")
    for r in primary_b:
        print(f"  {r['condition']:15} {r['ground_truth']:9} score={r['score']:.4f}  {status(r)}")

    print("\nSensitivity: first observation (0 -> 1)")
    for r in first_a:
        print(f"  {r['condition']:15} score={r['score']:.4f}  "
              f"authoritarian={r['authoritarian_agent']}  {status(r)}")
    for r in first_b:
        print(f"  {r['condition']:15} score={r['score']:.4f}  {status(r)}")

    print("\nSensitivity: Test B framing sweep")
    for f in FRAMINGS:
        row = [r for r in framing_sweep if r["inputs"]["dominant_agent_framing"] == f]
        cells = "  ".join(f"{r['condition']}={r['score']:.2f}" for r in row)
        ok = "match" if all(not r["prediction_mismatches"] for r in row) else "MISMATCH"
        print(f"  f={f:<4} {cells}  {ok}")

    print("\nOptional representation probe (not in criterion)")
    print(f"  zero counts {{a1..a4: 0}} score={probe['registered_zero_counts_score']:.4f}  "
          f"empty dict {{}} score={probe['empty_dict_score']:.4f}")

    print("\nFalsification criterion (|delta| < 1e-9 => does not discriminate)")
    for test, v in verdicts.items():
        word = "discriminates" if v["discriminates"] else "DOES NOT discriminate"
        print(f"  Test {test}: {v['absent']}={v['absent_score']:.4f} vs "
              f"{v['positive']}={v['positive_score']:.4f}  -> {word}")

    runs = primary_a + primary_b + first_a + first_b + framing_sweep
    out = {
        "scenario": "independent_falsifier_missing_evidence",
        "round": 1,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "coheronmetry_version": coheronmetry.__version__,
        "primary": primary_a + primary_b,
        "sensitivity_first_observation": first_a + first_b,
        "sensitivity_framing_sweep": framing_sweep,
        "optional_representation_probe": probe,
        "falsification": verdicts,
        "all_predictions_matched": all(not r["prediction_mismatches"] for r in runs),
    }
    out_path = Path(__file__).with_name("independent_falsifier_missing_evidence_results.json")
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved {out_path.name}")


if __name__ == "__main__":
    main()
