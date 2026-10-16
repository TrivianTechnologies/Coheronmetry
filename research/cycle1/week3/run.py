"""Representation-boundary test for substantive corrective uptake.

See design.md. Ground truth stays in the behavioral record.
The mapping never reads plan change.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import coheronmetry
from coheronmetry.relational_state import AgentID, RelationalState
from coheronmetry.field_constants import (
    NonDominationCalculator,
    SpeakingFrequencyMeasure,
    ProposalAcceptanceMeasure,
    DecisionConcentrationMeasure,
    EmergenceSuppressionMeasure,
    ReciprocityCalculator,
    AcknowledgmentRateMeasure,
    EmbodimentCalculator,
)

AGENTS = [AgentID("H"), AgentID("S")]

# Design §3. Shared exchange before the correction window.
BASE_TURNS = (4, 4)
BASE_PROPOSALS = (2, 2)
BASE_ACCEPTED = (2, 2)
BASE_DECISIONS = (1, 1)
BASE_CONTRIBUTIONS_MADE = 4
BASE_CONTRIBUTIONS_ACKNOWLEDGED = 2
SYNTHESIS_ATTEMPTS = 2
SYNTHESES_ADOPTED = 2
SYNTHESES_REFRAMED = 0
DOMINANT_AGENT_FRAMING = 0.0

# Facts the mapping is allowed to read. Plan substance is not on this list.
MAPPED_FACTS = ("correction_raised", "acknowledged")

REFUSED = [
    "plan_after",
    "constraint_resolved",
    "substantive_plan_change",
    "RepairResponsivenessMeasure",
    "FeedbackIntegrationMeasure",
    "ExchangeTrajectorymeasure",
    "RelationalState.record_drift",
    "RelationalState.record_repair",
]

# Design §2. plan_after and constraint_resolved are behavioral only.
EPISODES = {
    "E": {
        "correction_raised": True,
        "acknowledged": True,
        "plan_before": "A",
        "plan_after": "B",
        "constraint_resolved": True,
        "substantive_plan_change": True,
        "correction_opportunity": True,
    },
    "I": {
        "correction_raised": True,
        "acknowledged": True,
        "plan_before": "A",
        "plan_after": "A",
        "constraint_resolved": False,
        "substantive_plan_change": False,
        "correction_opportunity": True,
    },
    "N": {
        "correction_raised": False,
        "acknowledged": False,
        "plan_before": "A",
        "plan_after": "A",
        "constraint_resolved": False,
        "substantive_plan_change": False,
        "correction_opportunity": False,
    },
}

# Design §4. Hand-derived, then checked against the calculators.
# nd: speak, accept, decide, suppress, composite, level, is_sovereign, dominant_agent
# reciprocity: acknowledgment, composite, is_reciprocal, trajectory
# embodiment: composite, dimensions
EXPECTED = {
    "E": {
        "turns": (5, 5),
        "contributions_made": 5,
        "contributions_acknowledged": 3,
        "nd": (1.0, 1.0, 1.0, 1.0, 1.0, "none", True, None),
        "reciprocity": (0.6, 0.6, True, "unknown"),
        "embodiment": (0.5, []),
        "drift_count": 0,
        "repair_count": 0,
        "repair_success_rate": None,
    },
    "I": {
        "turns": (5, 5),
        "contributions_made": 5,
        "contributions_acknowledged": 3,
        "nd": (1.0, 1.0, 1.0, 1.0, 1.0, "none", True, None),
        "reciprocity": (0.6, 0.6, True, "unknown"),
        "embodiment": (0.5, []),
        "drift_count": 0,
        "repair_count": 0,
        "repair_success_rate": None,
    },
    "N": {
        "turns": (4, 4),
        "contributions_made": 4,
        "contributions_acknowledged": 2,
        "nd": (1.0, 1.0, 1.0, 1.0, 1.0, "none", True, None),
        "reciprocity": (0.5, 0.5, False, "unknown"),
        "embodiment": (0.5, []),
        "drift_count": 0,
        "repair_count": 0,
        "repair_success_rate": None,
    },
}
TOL = 5e-4


def map_inputs(episode):
    """Source-supported counts only. Does not read plan or constraint fields."""
    turns = list(BASE_TURNS)
    made = BASE_CONTRIBUTIONS_MADE
    acknowledged = BASE_CONTRIBUTIONS_ACKNOWLEDGED
    if episode["correction_raised"]:
        turns[1] += 1
        made += 1
    if episode["acknowledged"]:
        turns[0] += 1
        acknowledged += 1
    return {
        "turn_counts": tuple(turns),
        "proposals_by_agent": BASE_PROPOSALS,
        "acceptance_by_agent": BASE_ACCEPTED,
        "decisions_by_agent": BASE_DECISIONS,
        "synthesis_attempts": SYNTHESIS_ATTEMPTS,
        "syntheses_adopted": SYNTHESES_ADOPTED,
        "syntheses_reframed": SYNTHESES_REFRAMED,
        "dominant_agent_framing": DOMINANT_AGENT_FRAMING,
        "contributions_made": made,
        "contributions_acknowledged": acknowledged,
        "repair_responsiveness": None,
        "feedback_integration": None,
        "exchange_trajectory": None,
    }


def by_agent(values):
    return dict(zip(AGENTS, values))


def measure(mapped):
    decisions = by_agent(mapped["decisions_by_agent"])
    nd_calc = NonDominationCalculator()
    nd = nd_calc.calculate(
        speaking_frequency=SpeakingFrequencyMeasure(
            turn_counts=by_agent(mapped["turn_counts"]),
            participant_count=len(AGENTS),
        ),
        proposal_acceptance=ProposalAcceptanceMeasure(
            acceptance_by_agent=by_agent(mapped["acceptance_by_agent"]),
            proposals_by_agent=by_agent(mapped["proposals_by_agent"]),
        ),
        decision_concentration=DecisionConcentrationMeasure(
            decisions_by_agent=decisions,
            total_decisions=sum(decisions.values()),
        ),
        emergence_suppression=EmergenceSuppressionMeasure(
            synthesis_attempts=mapped["synthesis_attempts"],
            syntheses_adopted=mapped["syntheses_adopted"],
            syntheses_reframed=mapped["syntheses_reframed"],
            dominant_agent_framing=mapped["dominant_agent_framing"],
        ),
    )
    recip = ReciprocityCalculator().calculate(
        acknowledgment_rate=AcknowledgmentRateMeasure(
            contributions_made=mapped["contributions_made"],
            contributions_acknowledged=mapped["contributions_acknowledged"],
        ),
    )
    embodiment = EmbodimentCalculator().calculate(agent_id=AGENTS[0])

    state = RelationalState.create(participants=["H", "S"], session_id="uptake-boundary")
    health = state.coherence_health()
    return {
        "nd": {
            "speaking_frequency": nd.speaking_frequency.score,
            "proposal_acceptance": nd.proposal_acceptance.score,
            "decision_concentration": nd.decision_concentration.score,
            "emergence_suppression": nd.emergence_suppression.score,
            "composite": nd.composite_score,
            "dominance_level": nd.dominance_level.value,
            "is_sovereign": nd.is_sovereign,
            "dominant_agent": nd.dominant_agent,
            "dimensions_computed": list(nd.dimensions_computed),
        },
        "reciprocity": {
            "acknowledgment_rate": recip.acknowledgment_rate.score,
            "composite": recip.composite_score,
            "is_reciprocal": recip.is_reciprocal,
            "trajectory": recip.trajectory.value,
            "dimensions_computed": list(recip.dimensions_computed),
        },
        "embodiment": {
            "composite": embodiment.composite_score,
            "dimensions_computed": list(embodiment.dimensions_computed),
            "notes": list(embodiment.notes),
        },
        "relational_state": {
            "drift_count": len(state.drift_history),
            "repair_count": len(state.repair_history),
            "unresolved_drift_count": health["unresolved_drift_count"],
            "recent_repair_success_rate": health["recent_repair_success_rate"],
            "field_constants": health["field_constants"],
            "is_in_drift": state.is_in_drift(),
        },
    }


def close(expected, got):
    if isinstance(expected, float):
        return abs(expected - got) <= TOL
    return expected == got


def check(name, mapped, measured):
    exp = EXPECTED[name]
    mismatches = []
    pairs = [
        ("turns", exp["turns"], mapped["turn_counts"]),
        ("contributions_made", exp["contributions_made"], mapped["contributions_made"]),
        ("contributions_acknowledged", exp["contributions_acknowledged"], mapped["contributions_acknowledged"]),
        ("nd.speak", exp["nd"][0], measured["nd"]["speaking_frequency"]),
        ("nd.accept", exp["nd"][1], measured["nd"]["proposal_acceptance"]),
        ("nd.decide", exp["nd"][2], measured["nd"]["decision_concentration"]),
        ("nd.suppress", exp["nd"][3], measured["nd"]["emergence_suppression"]),
        ("nd.composite", exp["nd"][4], measured["nd"]["composite"]),
        ("nd.level", exp["nd"][5], measured["nd"]["dominance_level"]),
        ("nd.is_sovereign", exp["nd"][6], measured["nd"]["is_sovereign"]),
        ("nd.dominant_agent", exp["nd"][7], measured["nd"]["dominant_agent"]),
        ("reciprocity.acknowledgment", exp["reciprocity"][0], measured["reciprocity"]["acknowledgment_rate"]),
        ("reciprocity.composite", exp["reciprocity"][1], measured["reciprocity"]["composite"]),
        ("reciprocity.is_reciprocal", exp["reciprocity"][2], measured["reciprocity"]["is_reciprocal"]),
        ("reciprocity.trajectory", exp["reciprocity"][3], measured["reciprocity"]["trajectory"]),
        ("embodiment.composite", exp["embodiment"][0], measured["embodiment"]["composite"]),
        ("embodiment.dimensions", exp["embodiment"][1], measured["embodiment"]["dimensions_computed"]),
        ("drift_count", exp["drift_count"], measured["relational_state"]["drift_count"]),
        ("repair_count", exp["repair_count"], measured["relational_state"]["repair_count"]),
        ("repair_success_rate", exp["repair_success_rate"], measured["relational_state"]["recent_repair_success_rate"]),
    ]
    for label, expected, got in pairs:
        if not close(expected, got):
            mismatches.append(f"{label}: expected {expected}, got {got}")
    return mismatches


def measurement_signature(measured):
    return json.dumps(measured, sort_keys=True)


def main():
    mapped = {}
    measured = {}
    mismatches = {}
    for name, episode in EPISODES.items():
        mapped[name] = map_inputs(episode)
        measured[name] = measure(mapped[name])
        mismatches[name] = check(name, mapped[name], measured[name])

    # Plan substance is not an input. Episodes that differ only there map alike.
    flipped = dict(EPISODES["I"])
    flipped["plan_after"] = "B"
    flipped["constraint_resolved"] = True
    flipped["substantive_plan_change"] = True
    plan_flip_same_inputs = map_inputs(flipped) == map_inputs(EPISODES["I"])

    e_inputs_equal_i = mapped["E"] == mapped["I"]
    e_measure_equal_i = measurement_signature(measured["E"]) == measurement_signature(measured["I"])
    behavior_e_changes = EPISODES["E"]["substantive_plan_change"] is True
    behavior_i_unchanged = EPISODES["I"]["substantive_plan_change"] is False
    behavior_n_absent = EPISODES["N"]["correction_opportunity"] is False
    predictions_matched = all(not rows for rows in mismatches.values()) and plan_flip_same_inputs

    # design.md §7. The uptake contrast is behavioral and is absent from the
    # mapped inputs, so the claim is not adjudicated as SURVIVES or FAILS.
    status = None
    if (
        predictions_matched
        and behavior_e_changes
        and behavior_i_unchanged
        and behavior_n_absent
        and e_inputs_equal_i
        and e_measure_equal_i
    ):
        status = "UNRESOLVED"

    print("Behavioral plan change: "
          f"E={EPISODES['E']['substantive_plan_change']} "
          f"I={EPISODES['I']['substantive_plan_change']} "
          f"N opportunity={EPISODES['N']['correction_opportunity']}")
    print(f"Mapped inputs E == I: {e_inputs_equal_i}")
    print(f"Plan flip leaves inputs unchanged: {plan_flip_same_inputs}")
    print(f"Measurement E == I: {e_measure_equal_i}")
    for name in ("E", "I", "N"):
        rec = measured[name]
        ack = rec["reciprocity"]["acknowledgment_rate"]
        print(f"  {name}  ND={rec['nd']['composite']:.3f} {rec['nd']['dominance_level']:8} "
              f"ack={ack:.3f} reciprocal={rec['reciprocity']['is_reciprocal']} "
              f"Emb={rec['embodiment']['composite']:.3f} "
              f"drift={rec['relational_state']['drift_count']} "
              f"repair={rec['relational_state']['repair_count']}")
        if mismatches[name]:
            print("   MISMATCH: " + "; ".join(mismatches[name]))

    out = {
        "test": "corrective_influence_representation_boundary",
        "round": 1,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "coheronmetry_version": coheronmetry.__version__,
        "commit": "7d0144bd",
        "behavioral_records": EPISODES,
        "mapping_reads": list(MAPPED_FACTS),
        "mapping_refused": REFUSED,
        "mapped_inputs": mapped,
        "measurements": measured,
        "checks": {
            "behavior_E_plan_changes": behavior_e_changes,
            "behavior_I_plan_unchanged": behavior_i_unchanged,
            "behavior_N_opportunity_absent": behavior_n_absent,
            "inputs_E_equal_I": e_inputs_equal_i,
            "plan_flip_does_not_change_inputs": plan_flip_same_inputs,
            "measurement_E_equal_I": e_measure_equal_i,
            "prediction_mismatches": mismatches,
            "all_predictions_matched": predictions_matched,
        },
        "status": status,
    }
    out_path = Path(__file__).with_name("results.json")
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nStatus: {status}")
    print(f"All predictions matched: {predictions_matched}")
    print(f"Saved {out_path.name}")
    if not predictions_matched or status != "UNRESOLVED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
