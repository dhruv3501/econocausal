"""Blanket-discount baseline: give EVERY customer the same discount, ignoring the budget.

This is the "no targeting" policy the optimizer is compared against (plan item, 21 Oct).
It reuses true_gain() from optimizer.py so the ROI numbers are directly comparable
with results/policy_eval.json.

Needs :  results/ite_scores.csv  (from train_dml.py) and data/retail_mock.csv
Run   :  python src/optimize/blanket_baseline.py
Writes:  results/blanket_eval.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from optimizer import true_gain  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

scores = pd.read_csv(ROOT / "results" / "ite_scores.csv")
data = pd.read_csv(ROOT / "data" / "retail_mock.csv")
df = data.loc[scores["user_id"]].reset_index(drop=True)   # truth for the same customers
n = len(df)

report = {}
for discount in (10, 20):
    chosen = np.full(n, discount)
    spend = float(chosen.sum())
    gain = true_gain(df, chosen)
    report[f"blanket ${discount}"] = {
        "spend": spend,
        "customers_targeted": n,
        "true_incremental_revenue": round(gain, 2),
        "roi": round(gain / spend, 3),
    }
    print(f"blanket ${discount:<3d} spend ${spend:9.0f}  targeted {n:5d}  "
          f"true gain ${gain:9.2f}  ROI {report[f'blanket ${discount}']['roi']}")

# Compare with the optimizer result if it has been run
policy_file = ROOT / "results" / "policy_eval.json"
if policy_file.exists():
    policy = json.loads(policy_file.read_text())
    opt = policy.get("optimized (MILP)")
    if opt:
        print(f"optimized (MILP) spend ${opt['spend']:9.0f}  targeted {opt['customers_targeted']:5d}  "
              f"true gain ${opt['true_incremental_revenue']:9.2f}  ROI {opt['roi']}")
        report["note"] = (f"Optimized policy spends ${opt['spend']:.0f} (budget ${policy['budget']:.0f}); "
                          "blanket policies ignore the budget.")

with open(ROOT / "results" / "blanket_eval.json", "w") as f:
    json.dump(report, f, indent=2)
print("Wrote results/blanket_eval.json")
