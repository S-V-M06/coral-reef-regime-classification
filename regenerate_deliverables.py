"""Regenerate the PDF and slide deck from existing results without retraining models."""
from pathlib import Path
import json
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from coral_reef_ml.reporting import generate_report
from coral_reef_ml.presentation import generate_presentation


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Required results file is missing: {path}. Run run_project.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    results = ROOT / "results"
    cv_results = pd.read_csv(results / "model_comparison_cv.csv")
    metrics = load_json(results / "final_test_metrics.json")
    report_dict = pd.read_csv(results / "classification_report.csv")
    importance = pd.read_csv(results / "permutation_importance.csv")
    audit = load_json(results / "dataset_audit.json")

    pdf_path = generate_report(ROOT, cv_results, metrics, report_dict, importance, audit)
    pptx_path = generate_presentation(ROOT, cv_results, metrics, report_dict, importance, audit)
    print("Updated deliverables from existing results (models were not retrained):")
    print(f"PDF: {pdf_path}")
    print(f"PowerPoint: {pptx_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
