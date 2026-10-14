# Predicting Coral Reef Regimes from Human and Natural Influences

**Course:** UE24CS352A - Machine Learning Mini-Project  
**Assigned problem:** 79  
**Project type:** Four-class supervised classification

This repository implements a reproducible, command-line version of the assigned coral reef regime classification task. It is inspired by the Stanford CS229 project and makes small, defensible changes: leakage-safe preprocessing, a fixed random seed, consistent cross-validation, macro-F1 model selection, and programmatically generated reports.

> **Important:** Run the pipeline before using the generated PDF/PPTX as final submission artifacts. Scores are calculated from the actual data and are not hard-coded. The reference paper's reported score is not presented as our result.

## Quick start

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python run_project.py
```

The first run downloads the official data file into `data/Hawaii_RegimesPredictors.txt`. An internet connection is required only for that first download. For an offline run, download the file from the link in `data/README.md` and save it at that path. The program checks for 620 observations and regime labels [1, 2, 3, 5] before proceeding.


## Write-up length

The course brief is internally inconsistent: its section heading says “One-Page Write-up” while the body requests a “two-page summary.” The generated results-backed PDF is two pages. Confirm the expected length with the instructor before submission.

## Windows quick-run helper

On Windows, you can run `run_project_windows.bat` from the project root. It creates a virtual environment, installs the listed dependencies, runs the official-data pipeline, and pauses at the end so any errors remain visible. It requires network access for the first dataset download.

## Method summary

- Target: `Regime` with nominal labels 1, 2, 3 and 5.
- Inputs: 20 predictors from `Effluent` through `Depth`.
- Excluded: `Regime1`, `Regime2`, `Regime3`, and `Regime5` one-hot indicators, ecological response columns, identifiers and coordinates.
- Split: stratified 80/20 train/test with `random_state=42`.
- Model comparison: 5-fold stratified cross-validation on the training split only.
- Candidates: most-frequent baseline, Logistic Regression, RBF SVM, Random Forest and Gradient Boosting; additionally, a controlled Random Forest ablation adds five domain-motivated interactions (wave power × complexity, wave power × depth, complexity × depth, invasive algae × irradiance, and wave anomaly × chlorophyll anomaly).
- Selection metric: mean CV macro-F1. Micro-F1, weighted-F1, accuracy and balanced accuracy are reported as complementary metrics.
- Preprocessing: median imputation inside each pipeline; scaling for linear/SVM models only.
- Final test: CV-selected model is refit on the entire training split and evaluated on the held-out test set once.

## Output artifacts

After `python run_project.py`, check `results/`:

| File | Purpose |
|---|---|
| `dataset_audit.json` | Rows, classes, missingness, predictor schema and split sizes |
| `class_distribution.csv/.png` | Class-count check and plot |
| `missingness.csv/.png` | Missing values by predictor |
| `predictor_correlation.csv/.png` | Predictor correlation audit |
| `predictor_distributions.png` | Numeric predictor distribution overview |
| `eda_summary.json` | Duplicate/missingness/class-count notes |
| `model_comparison_cv.csv/.png` | Comparable training-only cross-validation scores |
| `final_test_metrics.json` | Held-out test summary for the CV-selected model |
| `classification_report.csv` | Per-class precision, recall and F1 |
| `confusion_matrix.csv/.png` | Held-out test errors by class |
| `permutation_importance.csv/.png` | Model-specific test-set permutation importance |
| `selected_model.joblib` | Serialized selected model |
| `Coral_Reef_Mini_Project_Report.pdf` | Results-backed concise PDF write-up |
| `Coral_Reef_Mini_Project_Presentation.pptx` | Results-backed review slide deck |

## Team names and regenerating only the documents

The supplied `TEAM_MEMBERS.txt` currently lists `SHREE VERDHAN M` and `SUHAS`, matching the names in the provided presentation/report. Before submission, confirm that both are the required full names and edit this file if needed (one name per line). Then run:

```bash
python regenerate_deliverables.py
```

This regenerates the PDF and PowerPoint from the existing result files without retraining models. To rerun the complete experiment instead, use `python run_project.py`.

## Tests

```bash
python -m pytest -q
```

The included tests check the 20-feature boundary and fit/predict behavior of each candidate pipeline on synthetic data. They are not a substitute for running the full experiment on the official dataset.

## Live demo plan

1. Run `python run_project.py` and show the source/schema checks.
2. Open `results/model_comparison_cv.csv` and explain selection by macro-F1.
3. Open the confusion matrix and explain one class-wise error.
4. Show the top permutation-importance values and explain why they are not causal effects.
5. Show the generated PDF and slide deck; connect every displayed metric to the result files.

## Research references

- Cheng, Murphy & Walecka, Stanford CS229, *Predicting Coral Reef Regimes from Human and Natural Influences*: https://cs229.stanford.edu/proj2019spr/report/56.pdf
- Poster: https://cs229.stanford.edu/proj2019spr/poster/56.pdf
- Jouffray et al. (2019), *Parsing human and biophysical drivers of coral reef regimes*, Proceedings of the Royal Society B: https://doi.org/10.1098/rspb.2018.2544
- Official data and analysis: https://github.com/JBjouffray/Hawaii_RegimesPredictors

## Team-owned submission actions

Create a private GitHub repository, push the extracted project folder contents (not just the ZIP archive), share it with the instructor and assigned TAs, confirm the write-up length with the instructor, validate outputs on your own machine, and rehearse the Q&A. The polished two-page PDF and nine-slide PowerPoint are generated from the saved measured results by `regenerate_deliverables.py`; this does not retrain models. See `docs/VALIDATION_CHECKLIST.md`.
