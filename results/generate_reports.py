"""Generate Week 6 defence/evaluation tables and graphs from the real
master results file (results/experiment_results.csv), built by
experiments/build_experiment_results.py from actual pilot runs.

Produces:
  - results/tables/final_recommender_metrics.csv
  - results/tables/final_attack_metrics.csv
  - results/tables/final_detection_metrics.csv
  - results/figures/clean_attacked_defended.png
  - results/figures/target_rank_comparison.png
  - results/figures/target_hit_rate.png
  - results/figures/detection_metrics.png
  - results/figures/confusion_matrix.png

If experiment_results.csv has no rows, this script reports that and
exits without creating anything -- every figure/table here comes only
from real rows already written by the pilot scripts.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.detection_metrics import confusion_counts  # noqa: E402

RESULTS_FILE = PROJECT_ROOT / "results" / "experiment_results.csv"
RANDOM_DETECTION_FILE = PROJECT_ROOT / "results" / "tables" / "random_detection_results.csv"
AVERAGE_DETECTION_FILE = PROJECT_ROOT / "results" / "tables" / "average_detection_results.csv"

TABLES_DIR = PROJECT_ROOT / "results" / "tables"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"

CONDITION_ORDER = ["clean", "random", "random_defended", "average", "average_defended"]


def load_results() -> pd.DataFrame:
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(
            f"{RESULTS_FILE} does not exist yet. "
            "Run experiments/build_experiment_results.py first."
        )
    results = pd.read_csv(RESULTS_FILE)
    if results.empty:
        raise ValueError(f"{RESULTS_FILE} has no experiment rows yet.")
    return results.set_index("condition").reindex(CONDITION_ORDER)


def generate_recommender_table(results: pd.DataFrame) -> pd.DataFrame:
    table = results[["rmse", "mae"]].astype(float)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(TABLES_DIR / "final_recommender_metrics.csv")
    return table


def generate_attack_table(results: pd.DataFrame) -> pd.DataFrame:
    table = results[["target_rank", "target_score", "hit_rate"]].astype(float)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(TABLES_DIR / "final_attack_metrics.csv")
    return table


def generate_detection_table(results: pd.DataFrame) -> pd.DataFrame:
    columns = ["detection_precision", "detection_recall", "detection_f1", "false_positive_rate"]
    table = results.loc[["random", "average"], columns].astype(float)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(TABLES_DIR / "final_detection_metrics.csv")
    return table


def plot_clean_attacked_defended(table: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    table.plot(kind="bar")
    plt.title("Clean vs Attacked vs Defended -- RMSE / MAE (Week 6 pilot)")
    plt.ylabel("Error")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "clean_attacked_defended.png")
    plt.close()


def plot_target_rank(table: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    table["target_rank"].plot(kind="bar", color="steelblue")
    plt.title("Target Movie Rank -- Clean vs Attacked vs Defended (Week 6 pilot)")
    plt.ylabel("Mean rank (lower = more promoted)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "target_rank_comparison.png")
    plt.close()


def plot_hit_rate(table: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    table["hit_rate"].plot(kind="bar", color="darkorange")
    plt.title("Target Hit Rate @10 -- Clean vs Attacked vs Defended (Week 6 pilot)")
    plt.ylabel("Hit Rate")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "target_hit_rate.png")
    plt.close()


def plot_detection_metrics(table: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    table[["detection_precision", "detection_recall", "detection_f1"]].plot(kind="bar")
    plt.title("Detection Performance (Week 6 pilot)")
    plt.ylabel("Score")
    plt.ylim(0, 1.1)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "detection_metrics.png")
    plt.close()


def plot_confusion_matrix() -> None:
    if not RANDOM_DETECTION_FILE.exists() or not AVERAGE_DETECTION_FILE.exists():
        print("Skipping confusion matrix: detection result files not found.")
        return

    random_detection = pd.read_csv(RANDOM_DETECTION_FILE)
    average_detection = pd.read_csv(AVERAGE_DETECTION_FILE)
    combined = pd.concat([random_detection, average_detection], ignore_index=True)

    counts = confusion_counts(
        combined["true_label"].tolist(),
        combined["predicted_label"].tolist(),
    )

    matrix = [[counts["tn"], counts["fp"]], [counts["fn"], counts["tp"]]]

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots()
    ax.imshow(matrix, cmap="Blues")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Predicted Genuine", "Predicted Suspicious"])
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Actual Genuine", "Actual Suspicious"])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, matrix[i][j], ha="center", va="center")
    ax.set_title("Detection Confusion Matrix (Random + Average pilots combined)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "confusion_matrix.png")
    plt.close()


def main() -> None:
    results = load_results()

    recommender_table = generate_recommender_table(results)
    attack_table = generate_attack_table(results)
    detection_table = generate_detection_table(results)

    plot_clean_attacked_defended(recommender_table)
    plot_target_rank(attack_table)
    plot_hit_rate(attack_table)
    plot_detection_metrics(detection_table)
    plot_confusion_matrix()

    print("Reports generated from the real experiment_results.csv data:")
    print(f"  Tables  -> {TABLES_DIR}")
    print(f"  Figures -> {FIGURES_DIR}")


if __name__ == "__main__":
    main()
