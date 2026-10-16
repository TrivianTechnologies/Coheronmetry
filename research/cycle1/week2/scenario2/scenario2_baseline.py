"""Scenario 2, Round 1 baseline and structural variants. See scenario2_design.md."""

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
    AcknowledgmentRateMeasure,
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
    "syntheses_reframed": 0,
    "dominant_agent_framing": 0.0,
    "contributions_each": 6.0,
    "contributions_made": 24,
    "attempts": 3,
    "feedback_events": 2,
}


def uniform(k):
    return {a: k for a in AGENTS}


# Design §4 baseline conditions and §8 structural variants.
# "outcome" is ground truth, never a calculator input.
CONDITIONS = {
    "C": {
        "variant": "baseline", "perturbation_scope": None,
        "agreement": "high", "coordination": "integrated", "outcome": "success",
        "adjusts": True, "adjustment_scope": "shared_plan", "acceptance_uniform": True,
        "acceptance_by_agent": uniform(4), "synthesis_attempts": 4, "syntheses_adopted": 4,
        "contributions_acknowledged": 18, "adjustments_made": 2, "adjustment_magnitude": 0.5,
    },
    "P": {
        "variant": "baseline", "perturbation_scope": None,
        "agreement": "low", "coordination": "integrated", "outcome": "success",
        "adjusts": True, "adjustment_scope": "shared_plan", "acceptance_uniform": True,
        "acceptance_by_agent": uniform(1), "synthesis_attempts": 4, "syntheses_adopted": 4,
        "contributions_acknowledged": 18, "adjustments_made": 2, "adjustment_magnitude": 0.5,
    },
    "F": {
        "variant": "baseline", "perturbation_scope": None,
        "agreement": "low", "coordination": "fragmented", "outcome": "failure",
        "adjusts": False, "adjustment_scope": None, "acceptance_uniform": True,
        "acceptance_by_agent": uniform(1), "synthesis_attempts": 4, "syntheses_adopted": 0,
        "contributions_acknowledged": 2, "adjustments_made": 0, "adjustment_magnitude": 0.0,
    },
    "F_prime": {
        "variant": "baseline", "perturbation_scope": None,
        "agreement": "low", "coordination": "fragmented", "outcome": "failure",
        "adjusts": True, "adjustment_scope": "individual_plans", "acceptance_uniform": True,
        "acceptance_by_agent": uniform(1), "synthesis_attempts": 4, "syntheses_adopted": 0,
        "contributions_acknowledged": 2, "adjustments_made": 2, "adjustment_magnitude": 0.5,
    },
    "F_no_synthesis": {
        "variant": "of F", "perturbation_scope": "non_domination_only",
        "agreement": "low", "coordination": "fragmented", "outcome": "failure",
        "adjusts": False, "adjustment_scope": None, "acceptance_uniform": True,
        "acceptance_by_agent": uniform(1), "synthesis_attempts": 0, "syntheses_adopted": 0,
        "contributions_acknowledged": 2, "adjustments_made": 0, "adjustment_magnitude": 0.0,
    },
    "C_x_from_a1": {
        "variant": "of C", "perturbation_scope": "behavioral_variant",
        "agreement": "high", "coordination": "integrated", "outcome": "success",
        "adjusts": True, "adjustment_scope": "shared_plan", "acceptance_uniform": False,
        "acceptance_by_agent": {"a1": 5, "a2": 4, "a3": 4, "a4": 4},
        "synthesis_attempts": 4, "syntheses_adopted": 4,
        "contributions_acknowledged": 18, "adjustments_made": 2, "adjustment_magnitude": 0.5,
    },
    "P_zero": {
        "variant": "of P", "perturbation_scope": "non_domination_only",
        "agreement": "low", "coordination": "integrated", "outcome": "success",
        "adjusts": True, "adjustment_scope": "shared_plan", "acceptance_uniform": True,
        "acceptance_by_agent": uniform(0), "synthesis_attempts": 4, "syntheses_adopted": 4,
        "contributions_acknowledged": 18, "adjustments_made": 2, "adjustment_magnitude": 0.5,
    },
    "F_zero": {
        "variant": "of F", "perturbation_scope": "non_domination_only",
        "agreement": "low", "coordination": "fragmented", "outcome": "failure",
        "adjusts": False, "adjustment_scope": None, "acceptance_uniform": True,
        "acceptance_by_agent": uniform(0), "synthesis_attempts": 4, "syntheses_adopted": 0,
        "contributions_acknowledged": 2, "adjustments_made": 0, "adjustment_magnitude": 0.0,
    },
}

# Design §5 and §8 predictions: (nd, dominance, reciprocity, reciprocity_label,
# embodiment, embodiment_label).
EXPECTED = {
    "C":              (1.000,  "none",     0.875,  "reciprocal",   0.5, "intermediate"),
    "P":              (1.000,  "none",     0.875,  "reciprocal",   0.5, "intermediate"),
    "F":              (0.900,  "none",     0.5417, "intermediate", 0.0, "drifting"),
    "F_prime":        (0.900,  "none",     0.5417, "intermediate", 0.5, "intermediate"),
    "F_no_synthesis": (1.000,  "none",     0.5417, "intermediate", 0.0, "drifting"),
    "C_x_from_a1":    (0.9745, "none",     0.875,  "reciprocal",   0.5, "intermediate"),
    "P_zero":         (0.875,  "none",     0.875,  "reciprocal",   0.5, "intermediate"),
    "F_zero":         (0.775,  "emerging", 0.5417, "intermediate", 0.0, "drifting"),
}
PREDICTION_TOL = 5e-4  # expected values are written to 3-4 decimals

# Design §6, plus one contrast per §8 variant against its parent.
CONTRASTS = [
    ("P - C",                  "P",              "C"),
    ("F - P",                  "F",              "P"),
    ("F_prime - P",            "F_prime",        "P"),
    ("F_prime - F",            "F_prime",        "F"),
    ("F_no_synthesis - F",     "F_no_synthesis", "F"),
    ("C_x_from_a1 - P",        "C_x_from_a1",    "P"),
    ("C_x_from_a1 - C",        "C_x_from_a1",    "C"),
    ("P_zero - P",             "P_zero",         "P"),
    ("F_zero - F",             "F_zero",         "F"),
]

OMITTED = {
    "reciprocity": ["exchange_trajectory", "repair_responsiveness"],
    "embodiment": [
        "reality_anchor", "actionability", "context_sensitivity",
        "evolutionary_plasticity", "grounding_ratio",
    ],
}


def build_inputs(cfg):
    return {
        "turn_counts": uniform(SHARED["turns_each"]),
        "participant_count": SHARED["participant_count"],
        "acceptance_by_agent": {AgentID(a): v for a, v in cfg["acceptance_by_agent"].items()},
        "proposals_by_agent": uniform(SHARED["proposals_each"]),
        "decisions_by_agent": uniform(SHARED["decisions_each"]),
        "total_decisions": SHARED["decisions_each"] * len(AGENTS),
        "synthesis_attempts": cfg["synthesis_attempts"],
        "syntheses_adopted": cfg["syntheses_adopted"],
        "syntheses_reframed": SHARED["syntheses_reframed"],
        "dominant_agent_framing": SHARED["dominant_agent_framing"],
        "contribution_totals": uniform(SHARED["contributions_each"]),
        "contributions_made": SHARED["contributions_made"],
        "contributions_acknowledged": cfg["contributions_acknowledged"],
        "feedback_events": SHARED["feedback_events"],
        "adjustments_made": cfg["adjustments_made"],
        "adjustment_magnitude": cfg["adjustment_magnitude"],
    }


def manipulation_check(cfg, inputs):
    """Design §2-§4 checks on the inputs only; no calculator output is used."""
    rates = [
        inputs["acceptance_by_agent"][a] / inputs["proposals_by_agent"][a]
        for a in AGENTS
    ]
    overall = sum(inputs["acceptance_by_agent"].values()) / sum(inputs["proposals_by_agent"].values())
    agreement_ok = overall >= 0.8 if cfg["agreement"] == "high" else all(r <= 0.2 for r in rates)
    expect_uniform = cfg["acceptance_uniform"]
    integrated = cfg["coordination"] == "integrated"

    checks = {
        "agreement_definition": agreement_ok,
        "acceptance_uniformity_as_designed": (len(set(rates)) == 1) == expect_uniform,
        "feedback_events_equal_2": inputs["feedback_events"] == 2,
        "adjustment_pattern": (
            inputs["adjustments_made"] == inputs["feedback_events"]
            if cfg["adjusts"] else inputs["adjustments_made"] == 0
        ),
        "magnitude_set_when_adjusting": (
            inputs["adjustment_magnitude"] > 0 if inputs["adjustments_made"] else True
        ),
        "integration_pattern": (
            inputs["syntheses_adopted"] == inputs["synthesis_attempts"] > 0
            if integrated else inputs["syntheses_adopted"] == 0
        ),
        "total_decisions_matches_sum": (
            inputs["total_decisions"] == sum(inputs["decisions_by_agent"].values())
        ),
        "contributions_made_matches_totals": (
            inputs["contributions_made"] == sum(inputs["contribution_totals"].values())
        ),
        # §3: contributions = proposals + syntheses.
        "contributions_match_counting_rule": (
            inputs["contributions_made"]
            == sum(inputs["proposals_by_agent"].values()) + inputs["synthesis_attempts"]
        ),
    }
    # Calculator-level perturbations freeze non-ND inputs by design (§8), so a
    # counting-rule mismatch there is expected and recorded rather than failed.
    exempt = []
    if cfg["perturbation_scope"] == "non_domination_only":
        if not checks["contributions_match_counting_rule"]:
            checks["contributions_match_counting_rule"] = "exempt"
            exempt.append("contributions_match_counting_rule")
    checks["passed"] = all(v is True or v == "exempt" for v in checks.values())
    checks["exempt"] = exempt
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
        acknowledgment_rate=AcknowledgmentRateMeasure(
            contributions_made=inputs["contributions_made"],
            contributions_acknowledged=inputs["contributions_acknowledged"],
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

    return {
        "condition": name,
        "variant": cfg["variant"],
        "perturbation_scope": cfg["perturbation_scope"],
        "agreement": cfg["agreement"],
        "coordination": cfg["coordination"],
        "outcome": cfg["outcome"],
        "adjusts": cfg["adjusts"],
        "adjustment_scope": cfg["adjustment_scope"],
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
            "dimensions": {
                "contribution_balance": rc.contribution_balance.score,
                "acknowledgment_rate": rc.acknowledgment_rate.score,
            },
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
    )
    fields = ["nd", "dominance", "recip", "recip_label", "emb", "emb_label"]
    mismatches = []
    for f, e, g in zip(fields, exp, got):
        same = abs(e - g) <= PREDICTION_TOL if isinstance(e, float) else e == g
        if not same:
            mismatches.append(f"{f}: expected {e}, got {g}")
    return mismatches


def main():
    records = {name: run_condition(name, cfg) for name, cfg in CONDITIONS.items()}

    print("Manipulation checks")
    for name, rec in records.items():
        mc = rec["manipulation_check"]
        failed = [k for k, v in mc.items() if k not in ("passed", "exempt") and v is False]
        status = "pass" if mc["passed"] else "FAIL " + ", ".join(failed)
        if mc["exempt"]:
            status += f"  (exempt, {rec['perturbation_scope']}: {', '.join(mc['exempt'])})"
        print(f"  {name:15} {status}")

    print("\nScores")
    print(f"  {'cond':15} {'variant':8} {'agree':5} {'coord':10} {'outcome':8} "
          f"{'ND':>6} {'level':8} {'Recip':>6} {'label':12} {'Emb':>5} {'label':12}")
    for name, r in records.items():
        print(f"  {name:15} {r['variant']:8} {r['agreement']:5} {r['coordination']:10} {r['outcome']:8} "
              f"{r['non_domination']['composite']:6.4f} {r['non_domination']['dominance_level']:8} "
              f"{r['reciprocity']['composite']:6.4f} {r['reciprocity']['label']:12} "
              f"{r['embodiment']['composite']:5.3f} {r['embodiment']['label']:12}")

    print("\nDimensions")
    for name, r in records.items():
        nd = r["non_domination"]["dimensions"]
        rc = r["reciprocity"]["dimensions"]
        print(f"  {name:15} ND[speak={nd['speaking_frequency']:.3f} accept={nd['proposal_acceptance']:.3f} "
              f"decide={nd['decision_concentration']:.3f} suppress={nd['emergence_suppression']:.3f}]  "
              f"Recip[balance={rc['contribution_balance']:.3f} ack={rc['acknowledgment_rate']:.3f}]")

    print("\nContrasts (raw difference; * = label changes)")
    contrasts = []
    for label, x, y in CONTRASTS:
        rx, ry = records[x], records[y]
        row = {"contrast": label}
        for calc, lab in [("non_domination", "dominance_level"),
                          ("reciprocity", "label"), ("embodiment", "label")]:
            row[calc] = rx[calc]["composite"] - ry[calc]["composite"]
            row[f"{calc}_label_changes"] = rx[calc][lab] != ry[calc][lab]
        contrasts.append(row)
        print(f"  {label:20} "
              f"ND {row['non_domination']:+.4f}{'*' if row['non_domination_label_changes'] else ' '}  "
              f"Recip {row['reciprocity']:+.4f}{'*' if row['reciprocity_label_changes'] else ' '}  "
              f"Emb {row['embodiment']:+.3f}{'*' if row['embodiment_label_changes'] else ' '}")

    print("\nPredictions (design §5, §8)")
    prediction_mismatches = {}
    for name, rec in records.items():
        mism = compare_to_expected(rec)
        prediction_mismatches[name] = mism
        print(f"  {name:15} {'match' if not mism else 'MISMATCH: ' + '; '.join(mism)}")

    out = {
        "scenario": "scenario2",
        "round": 1,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "coheronmetry_version": coheronmetry.__version__,
        "shared_inputs": SHARED,
        "records": records,
        "contrasts": contrasts,
        "prediction_mismatches": prediction_mismatches,
    }
    out_path = Path(__file__).with_name("scenario2_baseline_results.json")
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved {out_path.name}")


if __name__ == "__main__":
    main()
