"""Controlled implementation of corrective_uptake_observation_spec.md.

The spec defines the functions. This file does not.
Cases hold artifacts only. EXPECTED is the test oracle and is never
passed into the functions. This file does not import Coheronmetry.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# Field values only. No plan_changed, acknowledged, or uptake flags.
CASES = {
    "effective_uptake": {
        "plan_before": {"route": "A", "departure_time": "09:00"},
        "correction": {"target": "route", "requested_value": "B"},
        "constraint_identified": {"field": "route", "violating_value": "A"},
        "plan_after": {"route": "B", "departure_time": "09:00"},
        "subsequent_actions": [{"route": "B", "departure_time": "09:00"}],
        "observation_window": "next plan + next action",
    },
    "acknowledgment_only": {
        "plan_before": {"route": "A", "departure_time": "09:00"},
        "correction": {"target": "route", "requested_value": "B"},
        "constraint_identified": {"field": "route", "violating_value": "A"},
        "plan_after": {"route": "A", "departure_time": "09:00"},
        "subsequent_actions": [{"route": "A", "departure_time": "09:00"}],
        "observation_window": "next plan + next action",
    },
    "no_correction": {
        "plan_before": {"route": "A"},
        "correction": None,
        "constraint_identified": None,
        "plan_after": {"route": "A"},
        "subsequent_actions": [],
        "observation_window": "next plan",
    },
    "unrelated_change": {
        "plan_before": {"route": "A", "departure_time": "09:00"},
        "correction": {"target": "route", "requested_value": "B"},
        "constraint_identified": {"field": "route", "violating_value": "A"},
        "plan_after": {"route": "A", "departure_time": "10:00"},
        "subsequent_actions": [{"route": "A", "departure_time": "10:00"}],
        "observation_window": "next plan + next action",
    },
}

# Oracle. Not an observer input. acknowledgment_only stays UNRESOLVED
# because the artifacts do not record acknowledgment.
EXPECTED = {
    "effective_uptake": "SUBSTANTIVE_UPTAKE",
    "acknowledgment_only": "UNRESOLVED",
    "no_correction": "NO_CLASSIFICATION",
    "unrelated_change": "UNRELATED_CHANGE",
}

# Not a fifth research condition. Checks the revert branch in section 6.
BRANCH_CASES = {
    "effective_then_reverted": {
        "plan_before": {"route": "A", "departure_time": "09:00"},
        "correction": {"target": "route", "requested_value": "B"},
        "constraint_identified": {"field": "route", "violating_value": "A"},
        "plan_after": {"route": "B", "departure_time": "09:00"},
        "subsequent_actions": [{"route": "A", "departure_time": "09:00"}],
        "observation_window": "next plan + next action",
    },
}
BRANCH_EXPECTED = {
    "effective_then_reverted": "REJECTED_OR_OVERRIDDEN",
}


def detect_plan_delta(plan_before, plan_after):
    if not isinstance(plan_before, dict) or not isinstance(plan_after, dict):
        return {"missing": True, "changed": None, "changes": {}}
    keys = set(plan_before) | set(plan_after)
    changes = {}
    for key in sorted(keys):
        old = plan_before.get(key)
        new = plan_after.get(key)
        if old != new:
            changes[key] = [old, new]
    return {"missing": False, "changed": bool(changes), "changes": changes}


def evaluate_constraint_resolution(constraint_identified, plan_after, subsequent_actions):
    if not constraint_identified:
        return {"status": "not_applicable"}
    field = constraint_identified["field"]
    violating = constraint_identified["violating_value"]
    still_in_plan = plan_after.get(field) == violating
    put_back = any(action.get(field) == violating for action in subsequent_actions)
    if still_in_plan or put_back:
        return {"status": "unresolved_constraint"}
    return {"status": "resolved"}


def trace_change_to_correction(correction, plan_before, plan_after, subsequent_actions):
    """Content alignment only. Does not show that the correction caused the change."""
    del subsequent_actions
    observed = detect_plan_delta(plan_before, plan_after)
    if observed["missing"]:
        return {"status": "unclear", "observed": {}}
    if not observed["changed"]:
        return {"status": "not_applicable", "observed": {}}
    target = correction["target"]
    requested = correction["requested_value"]
    changes = observed["changes"]
    requested_landed = target in changes and changes[target][1] == requested
    other_fields = [key for key in changes if key != target]
    if requested_landed and not other_fields:
        return {"status": "attributed", "observed": changes}
    if requested_landed and other_fields:
        return {"status": "unclear", "observed": changes}
    return {"status": "unrelated", "observed": changes}


def evaluate_persistence(plan_before, plan_after, subsequent_actions, observation_window):
    """Later actions on fields that changed. observation_window is not parsed.
    Callers pass only the actions already inside the window."""
    del observation_window
    if not subsequent_actions:
        return {"status": "not_in_window"}
    changed = [
        key for key in set(plan_before) | set(plan_after)
        if plan_before.get(key) != plan_after.get(key)
    ]
    for action in subsequent_actions:
        for key in changed:
            if key in action and action[key] == plan_before.get(key):
                return {"status": "reverted", "field": key}
    return {"status": "held"}


def classify_uptake(plan_delta, constraint_resolution, attribution, persistence):
    """Section 6. First match wins. No uptake flag is an argument."""
    if plan_delta["missing"]:
        return "UNRESOLVED"
    if attribution["status"] == "unclear":
        return "UNRESOLVED"
    if not plan_delta["changed"]:
        return "UNRESOLVED"
    if attribution["status"] == "unrelated":
        return "UNRELATED_CHANGE"
    if persistence["status"] == "reverted":
        return "REJECTED_OR_OVERRIDDEN"
    constraint_blocks = constraint_resolution["status"] in (
        "not_applicable",
        "unresolved_constraint",
    )
    if constraint_blocks:
        return "UNRESOLVED"
    held = persistence["status"] in ("held", "not_in_window")
    if (
        plan_delta["changed"]
        and attribution["status"] == "attributed"
        and constraint_resolution["status"] == "resolved"
        and held
    ):
        return "SUBSTANTIVE_UPTAKE"
    return "UNRESOLVED"


def observe(case):
    """Run the functions. Reads artifacts only."""
    if case["correction"] is None:
        return {
            "functions_called": False,
            "classification": "NO_CLASSIFICATION",
        }
    plan_delta = detect_plan_delta(case["plan_before"], case["plan_after"])
    constraint = evaluate_constraint_resolution(
        case["constraint_identified"],
        case["plan_after"],
        case["subsequent_actions"],
    )
    attribution = trace_change_to_correction(
        case["correction"],
        case["plan_before"],
        case["plan_after"],
        case["subsequent_actions"],
    )
    persistence = evaluate_persistence(
        case["plan_before"],
        case["plan_after"],
        case["subsequent_actions"],
        case["observation_window"],
    )
    return {
        "functions_called": True,
        "plan_delta": "changed" if plan_delta["changed"] else "unchanged",
        "changes": plan_delta["changes"],
        "constraint": constraint["status"],
        "attribution": attribution["status"],
        "persistence": persistence["status"],
        "classification": classify_uptake(
            plan_delta, constraint, attribution, persistence
        ),
    }


def run_group(cases, expected, role):
    rows = []
    for name, case in cases.items():
        got = observe(case)
        want = expected[name]
        row = {
            "case": name,
            "role": role,
            "artifacts": case,
            "observer": got,
            "expected": want,
            "match": got["classification"] == want,
        }
        rows.append(row)
        bits = [f"{name}"]
        if got["functions_called"]:
            bits.append(f"  plan_delta: {got['plan_delta']}")
            bits.append(f"  constraint: {got['constraint']}")
            bits.append(f"  attribution: {got['attribution']}")
            bits.append(f"  persistence: {got['persistence']}")
        bits.append(f"  classification: {got['classification']}")
        bits.append(f"  expected: {want}")
        bits.append(f"  match: {str(row['match']).lower()}")
        print("\n".join(bits))
        print()
    return rows


def main():
    print("Primary four")
    primary = run_group(CASES, EXPECTED, "primary")
    print("Branch check")
    branch = run_group(BRANCH_CASES, BRANCH_EXPECTED, "branch")
    rows = primary + branch
    matched = all(row["match"] for row in rows)
    out = {
        "test": "corrective_uptake_observer",
        "spec": "corrective_uptake_observation_spec.md",
        "spec_frozen": "2026-10-05",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "cases": rows,
        "primary_matched": all(row["match"] for row in primary),
        "all_matched": matched,
        "note": (
            "The four primary cases show that the classification rules were "
            "implemented and exercised on controlled structured cases. "
            "They do not show that the observer reliably distinguishes uptake. "
            "acknowledgment_only is UNRESOLVED because the inputs do not record "
            "acknowledgment. evaluate_persistence now receives plan_before, "
            "which the first signature omitted. observation_window is not parsed; "
            "subsequent_actions are already limited to that window."
        ),
    }
    path = Path(__file__).with_name("corrective_uptake_test_results.json")
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"All matched: {matched}")
    print(f"Saved {path.name}")
    if not matched:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
