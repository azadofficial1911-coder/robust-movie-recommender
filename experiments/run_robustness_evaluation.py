"""One command to rebuild all Robustness Comparison evidence (Member 4 --
Defence + Evaluation) from the attacked datasets and detection results.

    python experiments/run_robustness_evaluation.py
    python experiments/run_robustness_evaluation.py --skip-target-frequency   # reuse existing file (~10 min saved)
    python experiments/run_robustness_evaluation.py --verify-only

Pipeline (each step is the ordinary script, run as its own process):

    1. experiments/apply_defence.py               attacked + predicted labels -> defended datasets
    2. experiments/evaluate_recommender_metrics.py RMSE / MAE on the fixed genuine test set
    3. experiments/evaluate_defence_effect.py      target rank / score / Hit@10 on the evaluation users
    4. experiments/evaluate_target_frequency.py    supplementary target frequency (wider user sample)
    5. experiments/build_experiment_results.py     master results/experiment_results.csv
    6. results/generate_reports.py                 tables + figures, copied into static/
    7. experiments/verify_robustness_evidence.py   invariant checks + results/evidence_manifest.json

Inputs produced by teammates are *not* regenerated here:
    data/attacked/*            (Azad: experiments/generate_attacked_data.py)
    results/tables/*_detection_results.csv, detection_metrics_pilot.csv
                               (Azad: experiments/run_detection.py)
Re-run those first if the attack or detector changes, then run this script.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ("Apply defence", "experiments/apply_defence.py"),
    ("RMSE / MAE", "experiments/evaluate_recommender_metrics.py"),
    ("Target rank / score / Hit@10", "experiments/evaluate_defence_effect.py"),
    ("Target frequency", "experiments/evaluate_target_frequency.py"),
    ("Master results file", "experiments/build_experiment_results.py"),
    ("Tables and figures", "results/generate_reports.py"),
]
VERIFY = ("Verify evidence", "experiments/verify_robustness_evidence.py")


def run_step(label: str, script: str) -> None:
    print(f"\n=== {label} ({script}) ===", flush=True)
    start = time.time()
    completed = subprocess.run([sys.executable, str(PROJECT_ROOT / script)], cwd=PROJECT_ROOT)
    if completed.returncode != 0:
        raise SystemExit(f"\nStopped: '{script}' exited with status {completed.returncode}.")
    print(f"--- {label} done in {time.time() - start:.0f}s", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild and verify the Robustness Comparison evidence.")
    parser.add_argument("--skip-target-frequency", action="store_true",
                        help="reuse the existing target_frequency_*.csv files")
    parser.add_argument("--verify-only", action="store_true",
                        help="only run the evidence checks")
    args = parser.parse_args()

    steps = [] if args.verify_only else [
        s for s in STEPS
        if not (args.skip_target_frequency and s[1].endswith("evaluate_target_frequency.py"))
    ]
    for label, script in steps + [VERIFY]:
        run_step(label, script)

    print("\nAll Robustness Comparison evidence rebuilt and verified.")


if __name__ == "__main__":
    main()
