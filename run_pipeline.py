"""Run the whole EconoCausal pipeline: data -> DML -> evaluation -> audit -> optimizer.

Usage:  python run_pipeline.py            (everything)
        python run_pipeline.py --fast     (skip slow tuning + refutation)
"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fast = "--fast" in sys.argv

steps = []
if not (ROOT / "data" / "retail_mock.csv").exists():
    steps.append(["src/generate_mock_data.py"])
steps += [
    ["src/causal/train_dml.py"],
    ["src/causal/evaluate_dml.py"],
]
if not fast:
    steps += [["src/causal/tune_dml.py"], ["src/causal/refute.py"]]
steps += [["src/optimize/optimizer.py", "--budget", "5000"]]

(ROOT / "data").mkdir(exist_ok=True)
for step in steps:
    print(f"\n=== {' '.join(step)} ===", flush=True)
    t0 = time.time()
    subprocess.run([sys.executable, *step], cwd=ROOT, check=True)
    print(f"--- done in {time.time() - t0:.0f}s ---")
print("\nPipeline finished. Outputs are in results/ and docs/.")
