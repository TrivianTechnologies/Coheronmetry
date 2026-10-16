"""Week 2 parameter sensitivity: calculator weights and label thresholds.

Exploratory robustness check (not pre-registered). The frozen S1, S2 and S4
baseline conditions are re-run through their own runners while one
calculator's class-level WEIGHTS is overridden at runtime and then restored;
repository files are unchanged. Label thresholds are hard-coded in the
repository, so they are assessed by each label's margin to the nearest cutoff.
"""

import importlib
import json
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import coheronmetry
from coheronmetry.field_constants import (
    NonDominationCalculator,
    ReciprocityCalculator,
    EmbodimentCalculator,
)

WEEK2 = Path(__file__).resolve().parent.parent
for sub in ("scenario1", "scenario2", "scenario4"):
    sys.path.insert(0, str(WEEK2 / sub))
s1 = importlib.import_module("scenario1_baseline")
s2 = importlib.import_module("scenario2_baseline")
s4 = importlib.import_module("scenario4_baseline")

# Only dimensions the frozen conditions supply affect the renormalized composite.
CALCULATORS = {
    "nd": (NonDominationCalculator, ["speaking_frequency", "proposal_acceptance",
                                     "decision_concentration", "emergence_suppression"]),
    "recip": (ReciprocityCalculator, ["contribution_balance", "acknowledgment_rate"]),
    "emb": (EmbodimentCalculator, ["feedback_integration"]),
}
FACTORS = [0.5, 0.75, 1.25, 1.5]

# Label cutoffs as hard-coded in the repository.
CUTOFFS = {
    "nd": [("none|emerging", 0.8), ("emerging|moderate; sovereign", 0.65),
           ("moderate|severe", 0.5), ("severe|critical", 0.3)],   # non_domination.py:74-82, 360
    "recip": [("reciprocal", 0.6), ("extractive", 0.35)],          # reciprocity.py:341, 345
    "emb": [("grounded", 0.6), ("drifting", 0.4)],                 # embodiment.py:307, 312
}
FRAGILE_MARGIN = 0.05
TIE = 1e-9


@contextmanager
def weights(cls, w):
    original = cls.WEIGHTS
    cls.WEIGHTS = w
    try:
        yield
    finally:
        cls.WEIGHTS = original


def schemes(cls, supplied):
    base = dict(cls.WEIGHTS)
    yield "baseline", base
    yield "equal", {k: 1.0 / len(base) for k in base}
    for dim in supplied:
        for f in FACTORS:
            w = dict(base)
            w[dim] = base[dim] * f
            yield f"{dim} x{f}", w


def collect():
    """{(scenario, condition, measure): (score, label)} for all frozen baseline conditions."""
    out = {}
    for scen, mod in (("S1", s1), ("S2", s2)):
        for name, cfg in mod.CONDITIONS.items():
            r = mod.run_condition(name, cfg)
            nd = r["non_domination"]
            sov = "sovereign" if nd["composite"] >= 0.65 else "not_sovereign"
            out[(scen, name, "nd")] = (nd["composite"], f"{nd['dominance_level']}/{sov}")
            out[(scen, name, "recip")] = (r["reciprocity"]["composite"], r["reciprocity"]["label"])
            out[(scen, name, "emb")] = (r["embodiment"]["composite"], r["embodiment"]["label"])
    for name, cfg in s4.CONDITIONS.items():
        r = s4.run("baseline", name, cfg)
        sov = "sovereign" if r["is_sovereign"] else "not_sovereign"
        out[("S4", name, "nd")] = (r["composite"], f"{r['dominance_level']}/{sov}")
    return out


def ordering(results, scen, measure):
    items = sorted(((s, c) for (sc, c, m), (s, _) in results.items() if sc == scen and m == measure),
                   key=lambda x: -x[0])
    groups, prev = [], None
    for score, cond in items:
        if prev is not None and abs(prev - score) <= TIE:
            groups[-1].append(cond)
        else:
            groups.append([cond])
        prev = score
    return " > ".join("=".join(g) for g in groups)


def orderings(results):
    keys = sorted({(sc, m) for sc, _, m in results})
    return {f"{sc}/{m}": ordering(results, sc, m) for sc, m in keys}


def margin(measure, score):
    name, cut = min(CUTOFFS[measure], key=lambda c: abs(score - c[1]))
    return name, cut, score - cut


def main():
    baseline = collect()
    base_order = orderings(baseline)

    weight_runs = {}
    for key, (cls, supplied) in CALCULATORS.items():
        rows = []
        for label, w in schemes(cls, supplied):
            with weights(cls, w):
                res = collect()
            order = orderings(res)
            flips = [
                {"scenario": sc, "condition": c, "measure": m,
                 "baseline": baseline[(sc, c, m)][1], "perturbed": lab, "score": s}
                for (sc, c, m), (s, lab) in res.items() if lab != baseline[(sc, c, m)][1]
            ]
            order_changes = {k: {"baseline": base_order[k], "perturbed": v}
                             for k, v in order.items() if v != base_order[k]}
            deltas = {k: res[k][0] - baseline[k][0] for k in res}
            other_measures_changed = any(abs(d) > TIE for (sc, c, m), d in deltas.items() if m != key)
            rows.append({
                "scheme": label,
                "weights": w,
                "label_flips": flips,
                "ordering_changes": order_changes,
                "max_abs_delta": max(abs(d) for (_, _, m), d in deltas.items() if m == key),
                "other_measures_changed": other_measures_changed,
                "scores": {f"{sc}/{c}/{m}": v for (sc, c, m), v in res.items() if m == key},
            })
        weight_runs[key] = rows

    margins = []
    for (sc, c, m), (score, lab) in baseline.items():
        name, cut, d = margin(m, score)
        margins.append({"scenario": sc, "condition": c, "measure": m, "score": score,
                        "label": lab, "nearest_cutoff": name, "cutoff": cut, "margin": d,
                        "fragile": abs(d) <= FRAGILE_MARGIN})

    print("Part 1: weight perturbation (one calculator at a time, others at baseline)")
    for key, rows in weight_runs.items():
        print(f"\n  {key.upper()}  (supplied dimensions: {', '.join(CALCULATORS[key][1])})")
        print(f"    {'scheme':34} flips  order_changes  max|delta|  other_measures_changed")
        for r in rows:
            print(f"    {r['scheme']:34} {len(r['label_flips']):5}  {len(r['ordering_changes']):13}  "
                  f"{r['max_abs_delta']:10.4f}  {r['other_measures_changed']}")
        for r in rows:
            for f in r["label_flips"]:
                print(f"      FLIP  {r['scheme']:32} {f['scenario']}/{f['condition']:14} "
                      f"{f['baseline']} -> {f['perturbed']} (score {f['score']:.4f})")
            for k, v in r["ordering_changes"].items():
                print(f"      ORDER {r['scheme']:32} {k}: {v['baseline']}  ->  {v['perturbed']}")

    print("\nBaseline orderings")
    for k, v in base_order.items():
        print(f"  {k:10} {v}")

    print(f"\nPart 2: threshold margins at baseline weights (fragile if |margin| <= {FRAGILE_MARGIN})")
    for r in sorted(margins, key=lambda r: abs(r["margin"])):
        if abs(r["margin"]) <= 0.10:
            tag = "FRAGILE" if r["fragile"] else ""
            print(f"  {r['scenario']}/{r['condition']:14} {r['measure']:5} score={r['score']:.4f}  "
                  f"{r['label']:24} nearest {r['nearest_cutoff']} ({r['cutoff']}) "
                  f"margin={r['margin']:+.4f} {tag}")

    out = {
        "check": "weight_threshold_sensitivity",
        "preregistered": False,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "coheronmetry_version": coheronmetry.__version__,
        "method": {
            "weights": "class-level WEIGHTS overridden at runtime per scheme, then restored",
            "factors": FACTORS,
            "conditions": "frozen S1, S2, S4 baseline conditions via their own runners",
            "thresholds": "margin of each baseline score to the nearest hard-coded cutoff",
            "fragile_margin": FRAGILE_MARGIN,
        },
        "baseline_orderings": base_order,
        "weight_perturbation": weight_runs,
        "threshold_margins": margins,
    }
    out_path = Path(__file__).with_name("weight_threshold_sensitivity_results.json")
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved {out_path.name}")


if __name__ == "__main__":
    main()
