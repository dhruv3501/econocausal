"""Budget-constrained discount allocation (multiple-choice knapsack with SciPy MILP).

Each customer gets ONE option from {0, $10, $20}.
Maximise  sum(margin * predicted ITE)   subject to   total discount spend <= budget.

Needs :  results/ite_scores.csv  (from train_dml.py)
Run   :  python src/optimize/optimizer.py --budget 5000
Writes:  results/allocation.csv, results/policy_eval.json
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix, hstack, identity

ROOT = Path(__file__).resolve().parents[2]
OPTIONS = (10, 20)


def optimize(ite_10, ite_20, budget, margin=1.0, time_limit=60):
    """Return an array with the chosen discount (0/10/20) for every customer."""
    n = len(ite_10)
    gain = margin * np.concatenate([ite_10, ite_20])          # value of each (user, option)
    cost = np.concatenate([np.full(n, 10.0), np.full(n, 20.0)])

    one_choice = LinearConstraint(hstack([identity(n), identity(n)]).tocsr(), ub=np.ones(n))
    in_budget = LinearConstraint(csr_matrix(cost.reshape(1, -1)), ub=budget)

    res = milp(c=-gain,                                        # milp minimises -> negate
               constraints=[one_choice, in_budget],
               integrality=np.ones(2 * n),
               bounds=Bounds(0, 1),
               options={"time_limit": time_limit, "mip_rel_gap": 1e-4})
    if res.x is None:
        raise RuntimeError(f"Solver failed: {res.message}")
    x = np.round(res.x).astype(int)
    return np.where(x[n:] == 1, 20, np.where(x[:n] == 1, 10, 0))


def greedy_10(ite_10, budget):
    """Baseline: $10 to the highest predicted-ITE customers until budget runs out."""
    chosen = np.zeros(len(ite_10), dtype=int)
    for i in np.argsort(-ite_10)[: int(budget // 10)]:
        if ite_10[i] > 0:
            chosen[i] = 10
    return chosen


def random_10(n, budget, seed=0):
    """Baseline: $10 to random customers until budget runs out."""
    chosen = np.zeros(n, dtype=int)
    chosen[np.random.default_rng(seed).permutation(n)[: int(budget // 10)]] = 10
    return chosen


def true_gain(df, discount):
    """Real incremental revenue (possible because the data is synthetic)."""
    return float(np.sum(df["true_effect"].to_numpy() * discount / 20))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=5000)
    ap.add_argument("--margin", type=float, default=1.0)
    args = ap.parse_args()

    scores = pd.read_csv(ROOT / "results" / "ite_scores.csv")
    data = pd.read_csv(ROOT / "data" / "retail_mock.csv")
    df = data.loc[scores["user_id"]].reset_index(drop=True)    # truth for the same customers

    policies = {
        "optimized (MILP)": optimize(scores.ite_10.to_numpy(), scores.ite_20.to_numpy(),
                                     args.budget, args.margin),
        "greedy $10 by ITE": greedy_10(scores.ite_10.to_numpy(), args.budget),
        "random $10": random_10(len(scores), args.budget),
    }

    report = {}
    for name, disc in policies.items():
        spend = float(disc.sum())
        gain = true_gain(df, disc)
        report[name] = {"spend": spend, "customers_targeted": int((disc > 0).sum()),
                        "true_incremental_revenue": round(gain, 2),
                        "roi": round(gain / spend, 3) if spend else None}
        assert spend <= args.budget + 1e-6, "budget violated!"
        print(f"{name:20s} spend ${spend:8.0f}  targeted {report[name]['customers_targeted']:5d}  "
              f"true gain ${gain:9.2f}  ROI {report[name]['roi']}")

    best = policies["optimized (MILP)"]
    alloc = pd.DataFrame({
        "user_id": scores["user_id"],
        "ite_10": scores.ite_10, "ite_20": scores.ite_20,
        "recommended_discount": best,
        "cost": best,
        "expected_uplift": np.where(best == 20, scores.ite_20,
                                    np.where(best == 10, scores.ite_10, 0.0)).round(4),
    })
    alloc.to_csv(ROOT / "results" / "allocation.csv", index=False)
    with open(ROOT / "results" / "policy_eval.json", "w") as f:
        json.dump({"budget": args.budget, **report}, f, indent=2)
    print("Wrote results/allocation.csv and results/policy_eval.json")
