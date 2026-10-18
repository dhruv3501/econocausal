# EconoCausal

Dynamic pricing using Double Machine Learning (causal inference). Infotact Solutions internship project (Data Science & ML).

The project estimates how much each customer's purchase value rises if they are shown a $10 or $20 discount (their Individual Treatment Effect), then picks a budget-constrained discount plan that targets only the customers who respond.

## Project structure

```
econocausal/
├── data/                  retail_mock.csv (synthetic data with a known true effect)
├── docs/                  design notes, results write-ups, causal DAG image
├── frontend/              React + Vite + Plotly dashboard (3 pages)
├── models/                saved LinearDML models (joblib)
├── results/               ite_scores.csv, allocation.csv and JSON result files
├── src/
│   ├── generate_mock_data.py
│   ├── export_mock_json.py
│   ├── causal/            baseline, dml_setup, train_dml, evaluate_dml, tune_dml, refute
│   └── optimize/          optimizer.py (SciPy MILP budget optimizer)
├── api/                   reserved for the REST API (Week 4)
├── run_pipeline.py        runs the whole pipeline end to end
└── requirements.txt
```

## Setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

## Run the full pipeline

```bash
python run_pipeline.py          # data -> DML -> evaluation -> tuning -> refutation -> optimizer
python run_pipeline.py --fast   # skips the slow tuning and refutation steps
```

`run_pipeline.py` creates `data/retail_mock.csv` if it is missing, then runs each step below in order.

## Run steps one by one

| Step | Command | Output |
|---|---|---|
| Generate mock data | `python src/generate_mock_data.py` | `data/retail_mock.csv` |
| DoWhy baseline (run from the repo root) | `python src/causal/baseline.py` | prints naive / DoWhy / true effect, saves `docs/causal_dag.png` |
| Train LinearDML | `python src/causal/train_dml.py` | `models/linear_dml.joblib`, `results/ite_scores.csv`, `results/dml_summary.json` |
| Evaluate vs naive and truth | `python src/causal/evaluate_dml.py` | `results/model_eval.json`, `docs/model_eval.md` |
| Tune nuisance models | `python src/causal/tune_dml.py` | `results/tuning.json`, `docs/tuning.md`, `models/linear_dml_tuned.joblib` |
| Refutation tests | `python src/causal/refute.py` | `results/refutation.json`, `docs/causal_audit.md` |
| Budget optimizer | `python src/optimize/optimizer.py --budget 5000` | `results/allocation.csv`, `results/policy_eval.json` |
| Dashboard mock JSON | `python src/export_mock_json.py` | `frontend/public/mock/mock_ite.json`, `mock_uplift.json` |

`run_pipeline.py` covers train, evaluate, tune, refute and optimize. The DoWhy baseline and the dashboard mock JSON export are run separately.

## Dashboard

```bash
cd frontend
npm install
npm run dev
```

The dashboard currently reads mock JSON from `frontend/public/mock/`. Pages: Upload + Budget, Uplift Curves, Allocation Matrix.

## Key results (synthetic data, 2,000-customer hold-out)

| Metric | $10 vs $0 | $20 vs $0 |
|---|---|---|
| True ATE | 13.59 | 27.18 |
| DML ATE | 13.87 | 26.60 |
| Naive ATE | 22.98 | 43.02 |
| DML ITE RMSE | 1.32 | 1.49 |

At a $5,000 budget the MILP optimizer returns an ROI of 2.01, against 1.88 for greedy targeting and 1.35 for random targeting. All DoWhy refutation tests pass. See `docs/mid_review_pack.md` for the full evidence.

## Documentation

- `docs/causal_design.md`: treatment, outcome, confounders, assumptions
- `docs/week1.md`, `docs/baseline_results.md`: Week 1 summary and baseline
- `docs/dml_setup.md`, `docs/model_eval.md`, `docs/tuning.md`: Double ML setup, evaluation, tuning
- `docs/causal_audit.md`: refutation tests
- `docs/mid_review_pack.md`: Mid Review evidence pack

## Team workflow

- Each member pushes only to their own branch (`Dhruv`, `tejaswini`).
- Nothing is merged into `main` until the end review is completed (Infotact notice, 12 Oct 2026).
- Commit and push regularly.
