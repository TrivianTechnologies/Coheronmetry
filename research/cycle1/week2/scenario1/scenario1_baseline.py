"""Scenario 1, Round 1 baseline. See scenario1_design.md."""

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
    ReciprocityCalculator,
    ContributionBalanceMeasure,
    EmbodimentCalculator,
    FeedbackIntegrationMeasure,
)

AGENTS = [AgentID("a1"), AgentID("a2"), AgentID("a3"), AgentID("a4")]

# Design §4, shared by all conditions.
SHARED = {
    "turns_each": 10,
    "participant_count": 4,
    "proposals_each": 5,
    "decisions_each": 1,
    "synthesis_attempts": 4,
    "syntheses_reframed": 0,
    "dominant_agent_framing": 0.0,
    "contributions_each": 6.0,
    "attempts": 3,
    "feedback_events": 2,
}

# Design §4, varying by condition. "outcome" is ground truth, never a calculator input.
CONDITIONS = {
    "A": {
        "agreement": "high", "outcome": "success", "adjusts": True,
        "acceptance_each": 4, "syntheses_adopted": 4,
        "adjustments_made": 2, "adjustment_magnitude": 0.5,
    },
    "B": {
        "agreement": "high", "outcome": "failure", "adjusts": False,
        "acceptance_each": 4, "syntheses_adopted": 4,
        "adjustments_made": 0, "adjustment_magnitude": 0.0,
    },
    "B_prime": {
        "agreement": "high", "outcome": "failure", "adjusts": True,
        "acceptance_each": 4, "syntheses_adopted": 4,
        "adjustments_made": 2, "adjustment_magnitude": 0.5,
    },
    "C": {
        "agreement": "low", "outcome": "success", "adjusts": True,
        "acceptance_each": 1, "syntheses_adopted": 1,
        "adjustments_made": 2, "adjustment_magnitude": 0.5,
    },
    "D": {
        "agreement": "low", "outcome": "failure", "adjusts": False,
        "acceptance_each": 1, "syntheses_adopted": 1,
        "adjustments_made": 0, "adjustment_magnitude": 0.0,
    },
}

# Design §5 predictions: (nd, dominance, reciprocity, reciprocity_label,
# embodiment, embodiment_label, embodiment_without_feedback).
EXPECTED = {
    "A":       (1.00, "none", 1.0, "reciprocal", 0.5, "intermediate", 0.5),
    "B":       (1.00, "none", 1.0, "reciprocal", 0.0, "drifting",     0.5),
    "B_prime": (1.00, "none", 1.0, "reciprocal", 0.5, "intermediate", 0.5),
    "C":       (0.95, "none", 1.0, "reciprocal", 0.5, "intermediate", 0.5),
    "D":       (0.95, "none", 1.0, "reciprocal", 0.0, "drifting",     0.5),
}

# Design §6.
CONTRASTS = [
    ("B - A",       "B",       "A"),
    ("C - A",       "C",       "A"),
    ("D - B",       "D",       "B"),
    ("B_prime - A", "B_prime", "A"),
    ("B_prime - B", "B_prime", "B"),
]

OMITTED = {
    "reciprocity": ["acknowledgment_rate", "exchange_trajectory", "repair_responsiveness"],
    "embodiment": [
        "reality_anchor", "actionability", "context_sensitivity",
        "evolutionary_plasticity", "grounding_ratio",
    ],
}

TOL = 1e-9


def build_inputs(cfg):
    return {
        "turn_counts": {a: SHARED["turns_each"] for a in AGENTS},
        "participant_count": SHARED["participant_count"],
        "acceptance_by_agent": {a: cfg["acceptance_each"] for a in AGENTS},
        "proposals_by_agent": {a: SHARED["proposals_each"] for a in AGENTS},
        "decisions_by_agent": {a: SHARED["decisions_each"] for a in AGENTS},
        "total_decisions": SHARED["decisions_each"] * len(AGENTS),
        "synthesis_attempts": SHARED["synthesis_attempts"],
        "syntheses_adopted": cfg["syntheses_adopted"],
        "syntheses_reframed": SHARED["syntheses_reframed"],
        "dominant_agent_framing": SHARED["dominant_agent_framing"],
        "contribution_totals": {a: SHARED["contributions_each"] for a in AGENTS},
        "feedback_events": SHARED["feedback_events"],
        "adjustments_made": cfg["adjustments_made"],
        "adjustment_magnitude": cfg["adjustment_magnitude"],
    }


def manipulation_check(cfg, inputs):
    """Design §2-§3 checks on the inputs only; no calculator output is used."""
    rates = [
        inputs["acceptance_by_agent"][a] / inputs["proposals_by_agent"][a]
        for a in AGENTS
    ]
    if cfg["agreement"] == "high":
        agreement_ok = all(r >= 0.8 for r in rates)
    else:
        agreement_ok = all(r <= 0.2 for r in rates)

    adjusts = cfg["adjusts"]
    checks = {
        "agreement_definition": agreement_ok,
        "acceptance_uniform": len(set(rates)) == 1,
        "feedback_events_equal_2": inputs["feedback_events"] == 2,
        "adjustment_pattern": (
            inputs["adjustments_made"] == inputs["feedback_events"]
            if adjusts else inputs["adjustments_made"] == 0
        ),
        "magnitude_set_when_adjusting": (
            inputs["adjustment_magnitude"] > 0 if inputs["adjustments_made"] else True
        ),
        "total_decisions_matches_sum": (
            inputs["total_decisions"] == sum(inputs["decisions_by_agent"].values())
        ),
    }
    checks["passed"] = all(checks.values())
    return checks


def reciprocity_label(rc):
    if rc.is_reciprocal:
        return "reciprocal"
    if rc.is_extractive:
        return "extractive"
    return "intermediate"


def embodiment_label(em):
    if em.is_grounded:
        return "grounded"
    if em.is_drifting_from_reality:
        return "drifting"
    return "intermediate"


def run_condition(name, cfg):
    inputs = build_inputs(cfg)

    nd_calc = NonDominationCalculator()
    nd = nd_calc.calculate(
        speaking_frequency=SpeakingFrequencyMeasure(
            turn_counts=inputs["turn_counts"],
            participant_count=inputs["participant_count"],
        ),
        proposal_acceptance=ProposalAcceptanceMeasure(
            acceptance_by_agent=inputs["acceptance_by_agent"],
            proposals_by_agent=inputs["proposals_by_agent"],
        ),
        decision_concentration=DecisionConcentrationMeasure(
            decisions_by_agent=inputs["decisions_by_agent"],
            total_decisions=inputs["total_decisions"],
        ),
        emergence_suppression=EmergenceSuppressionMeasure(
            synthesis_attempts=inputs["synthesis_attempts"],
            syntheses_adopted=inputs["syntheses_adopted"],
            syntheses_reframed=inputs["syntheses_reframed"],
            dominant_agent_framing=inputs["dominant_agent_framing"],
        ),
    )

    rc_calc = ReciprocityCalculator()
    rc = rc_calc.calculate(
        contribution_balance=ContributionBalanceMeasure(
            contribution_totals=inputs["contribution_totals"],
            participant_count=inputs["participant_count"],
        ),
    )

    em_calc = EmbodimentCalculator()
    em = em_calc.calculate(
        agent_id=AgentID("group"),
        feedback_integration=FeedbackIntegrationMeasure(
            feedback_events=inputs["feedback_events"],
            adjustments_made=inputs["adjustments_made"],
            adjustment_magnitude=inputs["adjustment_magnitude"],
        ),
    )
    em_no_fb = em_calc.calculate(agent_id=AgentID("group"))

    return {
        "condition": name,
        "agreement": cfg["agreement"],
        "outcome": cfg["outcome"],
        "adjusts": cfg["adjusts"],
        "variant": "baseline",
        "attempts": SHARED["attempts"],
        "inputs": {k: (dict(v) if isinstance(v, dict) else v) for k, v in inputs.items()},
        "manipulation_check": manipulation_check(cfg, inputs),
        "non_domination": {
            "dimensions": {
                "speaking_frequency": nd.speaking_frequency.score,
                "proposal_acceptance": nd.proposal_acceptance.score,
                "decision_concentration": nd.decision_concentration.score,
                "emergence_suppression": nd.emergence_suppression.score,
            },
            "composite": nd.composite_score,
            "dominance_level": nd.dominance_level.value,
            "is_sovereign": nd.is_sovereign,
            "requires_immediate_action": nd.requires_immediate_action,
            "dominant_agent": nd.dominant_agent,
            "weights": dict(nd_calc.WEIGHTS),
            "notes": nd.notes,
        },
        "reciprocity": {
            "dimensions": {"contribution_balance": rc.contribution_balance.score},
            "composite": rc.composite_score,
            "is_reciprocal": rc.is_reciprocal,
            "is_extractive": rc.is_extractive,
            "label": reciprocity_label(rc),
            "weights": dict(rc_calc.WEIGHTS),
            "omitted": OMITTED["reciprocity"],
            "notes": rc.notes,
        },
        "embodiment": {
            "agent_id": "group",
            "dimensions": em.dimension_scores(),
            "composite": em.composite_score,
            "is_grounded": em.is_grounded,
            "is_drifting_from_reality": em.is_drifting_from_reality,
            "label": embodiment_label(em),
            "weights": dict(em_calc.WEIGHTS),
            "omitted": OMITTED["embodiment"],
            "notes": em.notes,
        },
        "embodiment_feedback_omitted": {
            "composite": em_no_fb.composite_score,
            "label": embodiment_label(em_no_fb),
            "omitted": OMITTED["embodiment"] + ["feedback_integration"],
            "notes": em_no_fb.notes,
        },
    }


def compare_to_expected(rec):
    exp = EXPECTED[rec["condition"]]
    got = (
        rec["non_domination"]["composite"],
        rec["non_domination"]["dominance_level"],
        rec["reciprocity"]["composite"],
        rec["reciprocity"]["label"],
        rec["embodiment"]["composite"],
        rec["embodiment"]["label"],
        rec["embodiment_feedback_omitted"]["composite"],
    )
    fields = ["nd", "dominance", "recip", "recip_label", "emb", "emb_label", "emb_no_fb"]
    mismatches = []
    for f, e, g in zip(fields, exp, got):
        same = abs(e - g) <= TOL if isinstance(e, float) else e == g
        if not same:
            mismatches.append(f"{f}: expected {e}, got {g}")
    return mismatches


def main():
    records = {name: run_condition(name, cfg) for name, cfg in CONDITIONS.items()}

    print("Manipulation checks")
    for name, rec in records.items():
        mc = rec["manipulation_check"]
        failed = [k for k, v in mc.items() if k != "passed" and not v]
        print(f"  {name:8} {'pass' if mc['passed'] else 'FAIL ' + ', '.join(failed)}")

    print("\nScores")
    header = (f"  {'cond':8} {'agree':5} {'outcome':8} "
              f"{'ND':>5} {'level':6} {'Recip':>5} {'label':11} "
              f"{'Emb':>5} {'label':12} {'Emb-fb':>6}")
    print(header)
    for name, r in records.items():
        print(f"  {name:8} {r['agreement']:5} {r['outcome']:8} "
              f"{r['non_domination']['composite']:5.3f} {r['non_domination']['dominance_level']:6} "
              f"{r['reciprocity']['composite']:5.3f} {r['reciprocity']['label']:11} "
              f"{r['embodiment']['composite']:5.3f} {r['embodiment']['label']:12} "
              f"{r['embodiment_feedback_omitted']['composite']:6.3f}")

    print("\nNon-Domination dimensions")
    for name, r in records.items():
        dims = r["non_domination"]["dimensions"]
        print(f"  {name:8} " + "  ".join(f"{k}={v:.3f}" for k, v in dims.items()))

    print("\nContrasts (raw difference; * = label changes)")
    contrasts = []
    for label, x, y in CONTRASTS:
        rx, ry = records[x], records[y]
        row = {
            "contrast": label,
            "non_domination": rx["non_domination"]["composite"] - ry["non_domination"]["composite"],
            "non_domination_label_changes":
                rx["non_domination"]["dominance_level"] != ry["non_domination"]["dominance_level"],
            "reciprocity": rx["reciprocity"]["composite"] - ry["reciprocity"]["composite"],
            "reciprocity_label_changes": rx["reciprocity"]["label"] != ry["reciprocity"]["label"],
            "embodiment": rx["embodiment"]["composite"] - ry["embodiment"]["composite"],
            "embodiment_label_changes": rx["embodiment"]["label"] != ry["embodiment"]["label"],
            "embodiment_feedback_omitted":
                rx["embodiment_feedback_omitted"]["composite"]
                - ry["embodiment_feedback_omitted"]["composite"],
        }
        contrasts.append(row)
        print(f"  {label:12} "
              f"ND {row['non_domination']:+.3f}{'*' if row['non_domination_label_changes'] else ' '}  "
              f"Recip {row['reciprocity']:+.3f}{'*' if row['reciprocity_label_changes'] else ' '}  "
              f"Emb {row['embodiment']:+.3f}{'*' if row['embodiment_label_changes'] else ' '}  "
              f"Emb-fb {row['embodiment_feedback_omitted']:+.3f}")

    print("\nPredictions (design §5)")
    prediction_mismatches = {}
    for name, rec in records.items():
        mism = compare_to_expected(rec)
        prediction_mismatches[name] = mism
        print(f"  {name:8} {'match' if not mism else 'MISMATCH: ' + '; '.join(mism)}")

    out = {
        "scenario": "scenario1",
        "round": 1,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "coheronmetry_version": coheronmetry.__version__,
        "shared_inputs": SHARED,
        "records": records,
        "contrasts": contrasts,
        "prediction_mismatches": prediction_mismatches,
    }
    out_path = Path(__file__).with_name("scenario1_baseline_results.json")
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved {out_path.name}")


if __name__ == "__main__":
    main()
