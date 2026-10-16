"""Scenario 1, Round 1 sensitivity checks (design §8). Baseline files are not modified."""

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import coheronmetry
from scenario1_baseline import CONDITIONS, run_condition

# Design §8: adjustment magnitude 0.5 baseline, tested at 0.4 and 0.6.
# Only conditions that adjust are affected; with adjustments_made == 0 the
# magnitude has no effect on the score.
MAGNITUDES = [0.4, 0.5, 0.6]


def adjustment_magnitude_sweep():
    runs = []
    for m in MAGNITUDES:
        for name, base_cfg in CONDITIONS.items():
            cfg = copy.deepcopy(base_cfg)
            if cfg["adjusts"]:
                cfg["adjustment_magnitude"] = m
            rec = run_condition(name, cfg)
            rec["variant"] = f"adjustment_magnitude={m}"
            rec["is_baseline_value"] = m == 0.5
            runs.append(rec)
    return runs


def main():
    runs = adjustment_magnitude_sweep()
    baseline = {r["condition"]: r for r in runs if r["is_baseline_value"]}

    print("Adjustment magnitude sweep (Embodiment; ND and Reciprocity do not take this input)")
    print(f"  {'magnitude':9} {'cond':8} {'Emb':>5} {'label':12} {'vs baseline':12}")
    flips = []
    for r in runs:
        base = baseline[r["condition"]]
        changed = r["embodiment"]["label"] != base["embodiment"]["label"]
        if changed:
            flips.append({
                "variant": r["variant"],
                "condition": r["condition"],
                "from": base["embodiment"]["label"],
                "to": r["embodiment"]["label"],
                "score": r["embodiment"]["composite"],
            })
        mag = r["inputs"]["adjustment_magnitude"]
        print(f"  {mag:<9} {r['condition']:8} {r['embodiment']['composite']:5.3f} "
              f"{r['embodiment']['label']:12} {'LABEL FLIP' if changed else ''}")

    print("\nOrdering of conditions by Embodiment score")
    orderings = {}
    for m in MAGNITUDES:
        scores = {r["condition"]: r["embodiment"]["composite"]
                  for r in runs if r["variant"] == f"adjustment_magnitude={m}"}
        order = " > ".join(
            "=".join(sorted(c for c, s in scores.items() if s == v))
            for v in sorted(set(scores.values()), reverse=True)
        )
        orderings[m] = order
        print(f"  {m}: {order}")

    print("\nLabel flips relative to baseline (0.5)")
    for f in flips:
        print(f"  {f['variant']:24} {f['condition']:8} {f['from']} -> {f['to']} "
              f"(score {f['score']:.3f})")
    if not flips:
        print("  none")

    out = {
        "scenario": "scenario1",
        "round": 1,
        "check": "adjustment_magnitude",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "coheronmetry_version": coheronmetry.__version__,
        "values_tested": MAGNITUDES,
        "baseline_value": 0.5,
        "runs": runs,
        "label_flips": flips,
        "orderings": {str(k): v for k, v in orderings.items()},
    }
    out_path = Path(__file__).with_name("scenario1_sensitivity_results.json")
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved {out_path.name}")


if __name__ == "__main__":
    main()
