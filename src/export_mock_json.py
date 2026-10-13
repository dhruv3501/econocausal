"""Write mock_ite.json and mock_uplift.json for the React dashboard.

Run after train_dml.py:  python src/export_mock_json.py
Shapes (agree these with Member B):
  mock_ite.json    -> [{"user_id", "ite_10", "ite_20"}, ...]
  mock_uplift.json -> {"x": [...], "uplift": [...], "random_baseline": [...]}
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend" / "public" / "mock"
OUT.mkdir(parents=True, exist_ok=True)

scores = pd.read_csv(ROOT / "results" / "ite_scores.csv")

# 1) a small sample of per-customer ITE scores
scores.sample(300, random_state=42).round(2).to_json(
    OUT / "mock_ite.json", orient="records", indent=2)

# 2) placeholder uplift curve: rank customers by ITE, accumulate gain.
#    (A real Qini/AUUC curve with outcomes comes from Member B on 14 Oct.)
ranked = scores["ite_10"].sort_values(ascending=False).to_numpy()
cum = np.cumsum(ranked)
x = np.linspace(0, 1, 21)
idx = (x * len(ranked)).astype(int)
uplift = [0.0] + [float(cum[i - 1]) for i in idx[1:]]
curve = {"x": x.round(2).tolist(),
         "uplift": [round(u, 2) for u in uplift],
         "random_baseline": (x * cum[-1]).round(2).tolist()}
with open(OUT / "mock_uplift.json", "w") as f:
    json.dump(curve, f, indent=2)

print("Wrote", OUT.relative_to(ROOT))