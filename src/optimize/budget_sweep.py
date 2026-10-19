"""Compare policies across several budgets.

Needs :  results/ite_scores.csv (from train_dml.py), data/retail_mock.csv
Run   :  python src/optimize/budget_sweep.py
Writes:  results/budget_sweep.csv
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from optimizer import optimize, greedy_10, random_10, true_gain  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BUDGETS = [2500, 5000, 10000, 20000]

scores = pd.read_csv(ROOT / "results" / "ite_scores.csv")
data = pd.read_csv(ROOT / "data" / "retail_mock.csv")
df = data.loc[scores["user_id"]].reset_index(drop=True)   # truth for the same customers
ite_10, ite_20 = scores.ite_10.to_numpy(), scores.ite_20.to_numpy()

rows = []
for b in BUDGETS:
    policies = {
        "optimized (MILP)": optimize(ite_10, ite_20, b),
        "greedy $10 by ITE": greedy_10(ite_10, b),
        "random $10": random_10(len(df), b),
    }
    for name, disc in policies.items():
        spend = float(disc.sum())
        assert spend <= b + 1e-6, "budget violated!"
        gain = true_gain(df, disc)
        rows.append({"budget": b, "policy": name, "spend": spend,
                     "customers_targeted": int((disc > 0).sum()),
                     "true_gain": round(gain, 2),
                     "roi": round(gain / spend, 3) if spend else None})

out = pd.DataFrame(rows)
out.to_csv(ROOT / "results" / "budget_sweep.csv", index=False)
print(out.pivot(index="budget", columns="policy", values="roi"))
print("Wrote results/budget_sweep.csv")
