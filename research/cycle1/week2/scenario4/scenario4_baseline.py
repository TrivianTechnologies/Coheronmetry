"""Scenario 4, Round 1: hub influence vs domination (Non-Domination only). See scenario4_design.md."""

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import coheronmetry
from coheronmetry.relational_state import AgentID
from coheronmetry.field_constants import (
    NonDominationCalculator,
    SpeakingFrequencyMeasure,
    ProposalAcceptanceMeasure,
    DecisionConcentrationMeasure,
    EmergenceSuppressionMeasure,
)

AGENTS = [AgentID("H"), AgentID("S1"), AgentID("S2"), AgentID("S3")]
SYNTHESIS_ATTEMPTS = 4


def by_agent(*values):
    return dict(zip(AGENTS, values))


HUB_TURNS = (20, 10, 10, 10)
HUB_PROPOSALS = (8, 4, 4, 4)
HUB_DECISIONS = (5, 1, 1, 1)

# Design §4. Ground-truth fields are metadata only, never calculator inputs.
CONDITIONS = {
    "D": {
        "turns": (10, 10, 10, 10), "proposals": (5, 5, 5, 5), "accepted": (4, 4, 4, 4),
        "decisions": (1, 1, 1, 1), "adopted": 4, "reframed": 0, "framing": 0.0,
        "ground_truth": {"valid_corrections": 3, "corrections_affecting_decision": 3,
                         "corrective_influence_preserved": True},
    },
    "H": {
        "turns": HUB_TURNS, "proposals": HUB_PROPOSALS, "accepted": (7, 3, 3, 3),
        "decisions": HUB_DECISIONS, "adopted": 4, "reframed": 0, "framing": 0.0,
        "ground_truth": {"valid_corrections": 3, "corrections_affecting_decision": 3,
                         "corrective_influence_preserved": True},
    },
    "X_s": {
        "turns": HUB_TURNS, "proposals": HUB_PROPOSALS, "accepted": (7, 3, 3, 3),
        "decisions": HUB_DECISIONS, "adopted": 1, "reframed": 2, "framing": 0.5,
        "ground_truth": {"valid_corrections": 3, "corrections_affecting_decision": 0,
                         "corrective_influence_preserved": False},
    },
    "X_full": {
        "turns": HUB_TURNS, "proposals": HUB_PROPOSALS, "accepted": (8, 1, 1, 1),
        "decisions": HUB_DECISIONS, "adopted": 1, "reframed": 2, "framing": 0.5,
        "ground_truth": {"valid_corrections": 3, "corrections_affecting_decision": 0,
                         "corrective_influence_preserved": False},
    },
    "X_collision": {
        "turns": HUB_TURNS, "proposals": HUB_PROPOSALS, "accepted": (7, 3, 3, 3),
        "decisions": HUB_DECISIONS, "adopted": 4, "reframed": 0, "framing": 0.0,
        "ground_truth": {"valid_corrections": 3, "corrections_affecting_decision": 0,
                         "corrective_influence_preserved": False},
    },
}

FRAMING_VALUES = [0.0, 0.25, 0.5, 0.75, 1.0]
HUB_DECISION_VALUES = [1, 2, 3, 4, 5, 6, 7]

# Design §5-§6 predictions: (speak, accept, decide, suppress, nd, level, is_sovereign, dominant_agent).
EXPECTED = {
    ("baseline", "D"):           (1.0,    1.0,    1.0,    1.0,   1.0,    "none",     True,  None),
    ("baseline", "H"):           (0.6536, 0.9307, 0.75,   1.0,   0.8259, "none",     True,  "H"),
    ("baseline", "X_s"):         (0.6536, 0.9307, 0.75,   0.0,   0.6259, "moderate", False, "H"),
    ("baseline", "X_full"):      (0.6536, 0.2577, 0.75,   0.0,   0.4576, "severe",   False, "H"),
    ("baseline", "X_collision"): (0.6536, 0.9307, 0.75,   1.0,   0.8259, "none",     True,  "H"),
    ("framing_X_s", 0.0):        (0.6536, 0.9307, 0.75,   0.25,  0.6759, "emerging", True,  "H"),
    ("framing_X_s", 0.25):       (0.6536, 0.9307, 0.75,   0.125, 0.6509, "emerging", True,  "H"),
    ("framing_X_s", 0.5):        (0.6536, 0.9307, 0.75,   0.0,   0.6259, "moderate", False, "H"),
    ("framing_X_s", 0.75):       (0.6536, 0.9307, 0.75,   0.0,   0.6259, "moderate", False, "H"),
    ("framing_X_s", 1.0):        (0.6536, 0.9307, 0.75,   0.0,   0.6259, "moderate", False, "H"),
    **{("framing_H", f):         (0.6536, 0.9307, 0.75,   1.0,   0.8259, "none",     True,  "H")
       for f in FRAMING_VALUES},
    ("decisions_H", 1):          (0.6536, 0.9307, 1.0,    1.0,   0.9134, "none",     True,  None),
    ("decisions_H", 2):          (0.6536, 0.9307, 0.96,   1.0,   0.8994, "none",     True,  None),
    ("decisions_H", 3):          (0.6536, 0.9307, 0.8889, 1.0,   0.8745, "none",     True,  None),
    ("decisions_H", 4):          (0.6536, 0.9307, 0.8163, 1.0,   0.8491, "none",     True,  "H"),
    ("decisions_H", 5):          (0.6536, 0.9307, 0.75,   1.0,   0.8259, "none",     True,  "H"),
    ("decisions_H", 6):          (0.6536, 0.9307, 0.6914, 1.0,   0.8054, "none",     True,  "H"),
    ("decisions_H", 7):          (0.6536, 0.9307, 0.64,   1.0,   0.7874, "emerging", True,  "H"),
}
TOL = 5e-4

CONTRASTS = [
    ("X_s - H",         "X_s",         "H"),
    ("X_collision - H", "X_collision", "H"),
    ("H - D",           "H",           "D"),
    ("X_full - X_s",    "X_full",      "X_s"),
]


def run(part, key, cfg):
    decisions = by_agent(*cfg["decisions"])
    calc = NonDominationCalculator()
    nd = calc.calculate(
        speaking_frequency=SpeakingFrequencyMeasure(
            turn_counts=by_agent(*cfg["turns"]),
            participant_count=len(AGENTS),
        ),
        proposal_acceptance=ProposalAcceptanceMeasure(
            acceptance_by_agent=by_agent(*cfg["accepted"]),
            proposals_by_agent=by_agent(*cfg["proposals"]),
        ),
        decision_concentration=DecisionConcentrationMeasure(
            decisions_by_agent=decisions,
            total_decisions=sum(decisions.values()),
        ),
        emergence_suppression=EmergenceSuppressionMeasure(
            synthesis_attempts=SYNTHESIS_ATTEMPTS,
            syntheses_adopted=cfg["adopted"],
            syntheses_reframed=cfg["reframed"],
            dominant_agent_framing=cfg["framing"],
        ),
    )
    dims = {
        "speaking_frequency": nd.speaking_frequency.score,
        "proposal_acceptance": nd.proposal_acceptance.score,
        "decision_concentration": nd.decision_concentration.score,
        "emergence_suppression": nd.emergence_suppression.score,
    }
    got = (*dims.values(), nd.composite_score, nd.dominance_level.value,
           nd.is_sovereign, nd.dominant_agent)
    names = ["speak", "accept", "decide", "suppress", "nd", "level", "is_sovereign", "dominant_agent"]
    mismatches = []
    for n, e, g in zip(names, EXPECTED[(part, key)], got):
        same = abs(e - g) <= TOL if isinstance(e, float) else e == g
        if not same:
            mismatches.append(f"{n}: expected {e}, got {g}")
    return {
        "part": part,
        "key": key,
        "ground_truth": cfg.get("ground_truth"),
        "inputs": {
            "turn_counts": cfg["turns"], "proposals_by_agent": cfg["proposals"],
            "acceptance_by_agent": cfg["accepted"], "decisions_by_agent": cfg["decisions"],
            "total_decisions": sum(cfg["decisions"]), "synthesis_attempts": SYNTHESIS_ATTEMPTS,
            "syntheses_adopted": cfg["adopted"], "syntheses_reframed": cfg["reframed"],
            "dominant_agent_framing": cfg["framing"], "agent_order": list(AGENTS),
        },
        "dimensions": dims,
        "composite": nd.composite_score,
        "dominance_level": nd.dominance_level.value,
        "is_sovereign": nd.is_sovereign,
        "requires_immediate_action": nd.requires_immediate_action,
        "dominant_agent": nd.dominant_agent,
        "detectors": {
            "dominant_speaker": nd.speaking_frequency.dominant_speaker,
            "concentrated_in": nd.proposal_acceptance.concentrated_in,
            "authoritarian_agent": nd.decision_concentration.authoritarian_agent,
        },
        "weights": dict(calc.WEIGHTS),
        "notes": nd.notes,
        "prediction_mismatches": mismatches,
    }


def fmt(r, label):
    d = r["dimensions"]
    det = r["detectors"]
    status = "match" if not r["prediction_mismatches"] else "MISMATCH: " + "; ".join(r["prediction_mismatches"])
    return (f"  {label:12} speak={d['speaking_frequency']:.3f} accept={d['proposal_acceptance']:.3f} "
            f"decide={d['decision_concentration']:.3f} suppress={d['emergence_suppression']:.3f}  "
            f"ND={r['composite']:.4f} {r['dominance_level']:8} sov={str(r['is_sovereign']):5} "
            f"dom={r['dominant_agent']} [auth={det['authoritarian_agent']} conc={det['concentrated_in']} "
            f"spk={det['dominant_speaker']}]  {status}")


def main():
    runs = []
    baseline = {}
    for name, cfg in CONDITIONS.items():
        rec = run("baseline", name, cfg)
        baseline[name] = rec
        runs.append(rec)
    for f in FRAMING_VALUES:
        cfg = copy.deepcopy(CONDITIONS["X_s"])
        cfg["framing"] = f
        runs.append(run("framing_X_s", f, cfg))
    for f in FRAMING_VALUES:
        cfg = copy.deepcopy(CONDITIONS["H"])
        cfg["framing"] = f
        runs.append(run("framing_H", f, cfg))
    for k in HUB_DECISION_VALUES:
        cfg = copy.deepcopy(CONDITIONS["H"])
        cfg["decisions"] = (k, 1, 1, 1)
        runs.append(run("decisions_H", k, cfg))

    print("Baseline (ground truth: corrective_influence_preserved)")
    for name, r in baseline.items():
        preserved = "preserved" if r["ground_truth"]["corrective_influence_preserved"] else "lost"
        print(fmt(r, name) + f"  corrective influence: {preserved}")

    print("\nContrasts (raw ND difference; * = dominance level changes)")
    contrasts = []
    for label, x, y in CONTRASTS:
        rx, ry = baseline[x], baseline[y]
        row = {
            "contrast": label,
            "nd": rx["composite"] - ry["composite"],
            "level_changes": rx["dominance_level"] != ry["dominance_level"],
            "dimension_deltas": {k: rx["dimensions"][k] - ry["dimensions"][k] for k in rx["dimensions"]},
        }
        contrasts.append(row)
        changed = [k for k, v in row["dimension_deltas"].items() if abs(v) > 1e-12]
        print(f"  {label:16} ND {row['nd']:+.4f}{'*' if row['level_changes'] else ' '}  "
              f"dimensions changed: {', '.join(changed) if changed else 'none'}")

    titles = {
        "framing_X_s": "Framing sweep on X_s (adoption 1/4, reframed 2/4)",
        "framing_H": "Framing sweep on H (adoption 4/4, reframed 0)",
        "decisions_H": "Decision asymmetry on H (specialists fixed at 1 each)",
    }
    for part, title in titles.items():
        print(f"\n{title}")
        for r in (x for x in runs if x["part"] == part):
            label = f"f={r['key']}" if part.startswith("framing") else f"H dec={r['key']}"
            print(fmt(r, label))

    out = {
        "scenario": "scenario4",
        "round": 1,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "coheronmetry_version": coheronmetry.__version__,
        "runs": runs,
        "contrasts": contrasts,
        "all_predictions_matched": all(not r["prediction_mismatches"] for r in runs),
    }
    out_path = Path(__file__).with_name("scenario4_baseline_results.json")
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nAll predictions matched: {out['all_predictions_matched']}")
    print(f"Saved {out_path.name}")


if __name__ == "__main__":
    main()
