"""Policy evaluation on held-out customers: optimized vs blanket vs random (21 Oct task).

Needs :  results/ite_scores.csv (held-out customers) and data/retail_mock.csv
Run   :  python src/optimize/policy_evaluation.py --budget 5000
Writes:  results/policy_comparison.csv, results/roi_comparison.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from optimizer import optimize, greedy_10, random_10, true_gain  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

ap = argparse.ArgumentParser()
ap.add_argument("--budget", type=float, default=5000)
ap.add_argument("--seeds", type=int, default=200)
args = ap.parse_args()

scores = pd.read_csv(ROOT / "results" / "ite_scores.csv")
data = pd.read_csv(ROOT / "data" / "retail_mock.csv")
df = data.loc[scores["user_id"]].reset_index(drop=True)   # truth for held-out customers only
ite10, ite20 = scores.ite_10.to_numpy(), scores.ite_20.to_numpy()
n = len(df)


def row(name, disc, **extra):
    spend = float(disc.sum())
    gain = true_gain(df, disc)
    return {"policy": name, "spend": spend, "customers_targeted": int((disc > 0).sum()),
            "true_incremental_revenue": round(gain, 2),
            "roi": round(gain / spend, 3) if spend else None,
            "net_roi": round((gain - spend) / spend, 3) if spend else None, **extra}


rows = []

# 1) Optimized (MILP), plus predicted vs true gain
opt = optimize(ite10, ite20, args.budget)
pred_gain = float(np.where(opt == 20, ite20, np.where(opt == 10, ite10, 0)).sum())
rows.append(row("Optimized (MILP)", opt, predicted_gain=round(pred_gain, 2)))

# 2) Greedy $10 by ITE
rows.append(row("Greedy $10 by ITE", greedy_10(ite10, args.budget)))

# 3) Random $10, averaged over many seeds
rand = [row("r", random_10(n, args.budget, seed=s)) for s in range(args.seeds)]
r_roi = np.array([r["roi"] for r in rand])
r_gain = np.array([r["true_incremental_revenue"] for r in rand])
rows.append({"policy": f"Random $10 (mean of {args.seeds} seeds)", "spend": args.budget,
             "customers_targeted": rand[0]["customers_targeted"],
             "true_incremental_revenue": round(r_gain.mean(), 2),
             "roi": round(r_roi.mean(), 3),
             "net_roi": round(r_roi.mean() - 1, 3),
             "roi_std": round(r_roi.std(), 3)})

# 4) Blanket policies (ignore the budget)
for d in (10, 20):
    rows.append(row(f"Blanket ${d} (no budget limit)", np.full(n, d)))

table = pd.DataFrame(rows)
print(table.to_string(index=False))

best_other = table.loc[table.policy.str.startswith(("Greedy", "Random", "Blanket")), "roi"].max()
print(f"\nOptimized ROI {rows[0]['roi']} vs best baseline ROI {best_other}")
assert rows[0]["spend"] <= args.budget + 1e-6, "budget violated!"

table.to_csv(ROOT / "results" / "policy_comparison.csv", index=False)
chart = [{"policy": r["policy"], "roi": r["roi"], "spend": r["spend"],
          "incremental_revenue": r["true_incremental_revenue"]} for r in rows]
(ROOT / "results" / "roi_comparison.json").write_text(json.dumps(chart, indent=2))
print("Wrote results/policy_comparison.csv and results/roi_comparison.json")