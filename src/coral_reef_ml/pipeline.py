"""Reproducible classification pipeline for the Hawaiian coral reef regime data."""
from __future__ import annotations

import json
import hashlib
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score, make_scorer)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import joblib

DATA_URL = "https://raw.githubusercontent.com/JBjouffray/Hawaii_RegimesPredictors/master/Data/Hawaii_RegimesPredictors.txt"
TARGET = "Regime"
PREDICTORS = [
    "Effluent", "Sedimentation", "New_Development", "Habitat_Modification",
    "Invasive_Algae", "Fishing_Comm_Total", "Fishing_NonComm_Boat_Total",
    "Fishing_NonComm_Shore_Line", "Fishing_NonComm_Shore_Net",
    "Fishing_NonComm_Shore_Spear", "SST_CLIM_M", "SST_STD", "CHL_CLIM_M",
    "CHL_ANOM_F", "PAR_CLIM_M", "PAR_STD", "WAV_CLIM_M", "WAV_ANOM_F",
    "Complexity", "Depth"
]
RANDOM_STATE = 42
INTERACTION_FEATURES = [
    "WavePower_x_Complexity", "WavePower_x_Depth", "Complexity_x_Depth",
    "InvasiveAlgae_x_PAR", "WaveAnomaly_x_ChlorophyllAnomaly"
]


def add_interaction_features(X: pd.DataFrame) -> pd.DataFrame:
    """Add five pre-specified domain-motivated interactions for a controlled ablation."""
    out = X.copy()
    out["WavePower_x_Complexity"] = out["WAV_CLIM_M"] * out["Complexity"]
    out["WavePower_x_Depth"] = out["WAV_CLIM_M"] * out["Depth"]
    out["Complexity_x_Depth"] = out["Complexity"] * out["Depth"]
    out["InvasiveAlgae_x_PAR"] = out["Invasive_Algae"] * out["PAR_CLIM_M"]
    out["WaveAnomaly_x_ChlorophyllAnomaly"] = out["WAV_ANOM_F"] * out["CHL_ANOM_F"]
    return out


def load_dataset(root: Path) -> Tuple[pd.DataFrame, str]:
    """Load a local tab-delimited source file or download the canonical copy."""
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    local_path = data_dir / "Hawaii_RegimesPredictors.txt"
    if not local_path.exists():
        request = urllib.request.Request(DATA_URL, headers={"User-Agent": "CoralReefMiniProject/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read()
            local_path.write_bytes(payload)
        except Exception as exc:
            raise RuntimeError(
                "Could not download the official source dataset. Check internet access and try again, "
                "or manually save the tab-delimited file from this URL as data/Hawaii_RegimesPredictors.txt:\n"
                f"{DATA_URL}\nOriginal error: {exc}"
            ) from exc
    # The official file is tab-delimited and uses a decimal comma.
    df = pd.read_csv(local_path, sep="\t", decimal=",")
    df.columns = [str(c).strip() for c in df.columns]
    if TARGET not in df.columns:
        raise ValueError(f"Target column {TARGET!r} not found. Found: {list(df.columns)}")
    absent = [c for c in PREDICTORS if c not in df.columns]
    if absent:
        raise ValueError(f"Required predictor columns missing from source data: {absent}")
    df = df.dropna(subset=[TARGET]).copy()
    df[TARGET] = pd.to_numeric(df[TARGET], errors="raise").astype(int)
    y_labels = sorted(df[TARGET].unique().tolist())
    if len(df) != 620 or y_labels != [1, 2, 3, 5]:
        raise ValueError(
            "The downloaded source does not match the project specification. "
            f"Expected 620 rows with regime labels [1, 2, 3, 5]; got {len(df)} rows and {y_labels}. "
            "Inspect the data source rather than silently continuing."
        )
    return df, str(local_path)


def build_models() -> Dict[str, Pipeline]:
    """Create preprocessing/model pipelines so imputers and scalers fit inside CV folds."""
    return {
        "Most-Frequent Baseline": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", DummyClassifier(strategy="most_frequent")),
        ]),
        "Logistic Regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=3000, class_weight="balanced", random_state=RANDOM_STATE)),
        ]),
        "RBF SVM": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", SVC(kernel="rbf", class_weight="balanced", random_state=RANDOM_STATE)),
        ]),
        "Random Forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(
                n_estimators=400, min_samples_leaf=2, class_weight="balanced_subsample",
                random_state=RANDOM_STATE, n_jobs=-1
            )),
        ]),
        "Gradient Boosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", GradientBoostingClassifier(random_state=RANDOM_STATE)),
        ]),
    }


def _plot_class_distribution(y: pd.Series, path: Path) -> None:
    counts = y.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.bar([str(i) for i in counts.index], counts.values)
    ax.set_title("Observed class distribution")
    ax.set_xlabel("Reef regime label")
    ax.set_ylabel("Number of sites")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)



def _plot_missingness(X: pd.DataFrame, path: Path) -> None:
    missing = X.isna().sum().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(8.4, 5.5))
    ax.barh(missing.index, missing.values)
    ax.set_title("Missing values by predictor")
    ax.set_xlabel("Missing cell count (of 620 sites)")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _plot_correlations(X: pd.DataFrame, path: Path) -> None:
    corr = X.corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(10.5, 8.5))
    image = ax.imshow(corr.values, vmin=-1, vmax=1, cmap="coolwarm", aspect="auto")
    ax.set_xticks(range(len(corr.columns)), corr.columns, rotation=75, ha="right", fontsize=7)
    ax.set_yticks(range(len(corr.index)), corr.index, fontsize=7)
    ax.set_title("Pearson correlation among numeric predictors")
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.03)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _plot_distributions(X: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(5, 4, figsize=(13, 12))
    for ax, col in zip(axes.ravel(), X.columns):
        vals = X[col].dropna()
        ax.hist(vals, bins=20)
        ax.set_title(col, fontsize=8)
        ax.tick_params(axis="both", labelsize=6)
    for ax in axes.ravel()[len(X.columns):]:
        ax.axis("off")
    fig.suptitle("Predictor distributions (unscaled source values)", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _plot_cv_comparison(cv_results: pd.DataFrame, path: Path) -> None:
    frame = cv_results.sort_values("cv_macro_f1_mean", ascending=True)
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.barh(frame["model"], frame["cv_macro_f1_mean"], xerr=frame["cv_macro_f1_std"], capsize=3)
    ax.set_xlim(0, 1)
    ax.set_xlabel("5-fold mean macro-F1 (higher is better)")
    ax.set_title("Training-only cross-validation comparison")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _plot_confusion(cm: np.ndarray, labels: list[int], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.3, 4.6))
    im = ax.imshow(cm, interpolation="nearest")
    ax.set_title("Held-out test confusion matrix")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_xticks(range(len(labels)), [str(x) for x in labels])
    ax.set_yticks(range(len(labels)), [str(x) for x in labels])
    ax.set_xlabel("Predicted regime")
    ax.set_ylabel("True regime")
    threshold = (cm.max() / 2.0) if cm.size else 0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, f"{cm[i, j]}", ha="center", va="center",
                    color="white" if cm[i, j] > threshold else "black")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _plot_importance(importance: pd.DataFrame, path: Path) -> None:
    frame = importance.head(12).sort_values("permutation_importance_mean", ascending=True)
    fig, ax = plt.subplots(figsize=(8.3, 5.3))
    ax.barh(frame["feature"], frame["permutation_importance_mean"],
            xerr=frame["permutation_importance_std"], capsize=2)
    ax.set_xlabel("Decrease in test macro-F1 after permutation")
    ax.set_title("Top permutation importances (test-set interpretation only)")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def run_pipeline(root: Path) -> None:
    results_dir = root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    print("[1/7] Loading official dataset...")
    df, local_path = load_dataset(root)
    X = df[PREDICTORS].apply(pd.to_numeric, errors="coerce")
    y = df[TARGET].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE
    )
    if set(y_train.unique()) != set(y_test.unique()):
        raise RuntimeError("Stratified split unexpectedly dropped a target class.")

    audit = {
        "dataset_source": DATA_URL,
        "local_data_path": str(Path(local_path).relative_to(root)),
        "source_data_sha256": hashlib.sha256(Path(local_path).read_bytes()).hexdigest(),
        "rows": int(len(df)),
        "predictor_count": int(len(PREDICTORS)),
        "predictors": PREDICTORS,
        "engineered_interactions": INTERACTION_FEATURES,
        "target": TARGET,
        "classes": [int(x) for x in sorted(y.unique())],
        "missing_values_by_predictor": {k: int(v) for k, v in X.isna().sum().items() if v > 0},
        "exact_duplicate_rows_in_source": int(df.duplicated().sum()),
        "class_counts": {str(k): int(v) for k, v in y.value_counts().sort_index().items()},
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "split": "80/20 stratified train/test; random_state=42",
        "selection_metric": "mean 5-fold macro-F1 on training split",
        "cv": "StratifiedKFold(n_splits=5, shuffle=True, random_state=42)",
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    (results_dir / "dataset_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    pd.DataFrame({"regime": sorted(y.value_counts().index),
                  "count": [int(y.value_counts().loc[k]) for k in sorted(y.value_counts().index)]}).to_csv(
                      results_dir / "class_distribution.csv", index=False)
    _plot_class_distribution(y, results_dir / "class_distribution.png")
    missingness = pd.DataFrame({
        "predictor": X.columns,
        "missing_count": X.isna().sum().values,
        "missing_percent": (X.isna().mean().values * 100.0),
    }).sort_values("missing_count", ascending=False)
    missingness.to_csv(results_dir / "missingness.csv", index=False, float_format="%.3f")
    X.corr(numeric_only=True).to_csv(results_dir / "predictor_correlation.csv", float_format="%.6f")
    _plot_missingness(X, results_dir / "missingness.png")
    _plot_correlations(X, results_dir / "predictor_correlation.png")
    _plot_distributions(X, results_dir / "predictor_distributions.png")
    eda_summary = {
        "exact_duplicate_rows_not_removed": int(df.duplicated().sum()),
        "predictors_with_missing_values": {k: int(v) for k, v in X.isna().sum().items() if v > 0},
        "class_counts": {str(k): int(v) for k, v in y.value_counts().sort_index().items()},
        "interpretation_note": "No rows were removed automatically; inspect duplicates and missingness before interpreting the outputs."
    }
    (results_dir / "eda_summary.json").write_text(json.dumps(eda_summary, indent=2), encoding="utf-8")

    print("[2/7] Running 5-fold stratified cross-validation on the training split...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scoring = {
        "macro_f1": make_scorer(f1_score, average="macro", zero_division=0),
        "micro_f1": make_scorer(f1_score, average="micro", zero_division=0),
        "weighted_f1": make_scorer(f1_score, average="weighted", zero_division=0),
        "accuracy": "accuracy",
        "balanced_accuracy": "balanced_accuracy",
    }
    model_map = build_models()
    X_train_engineered = add_interaction_features(X_train)
    X_test_engineered = add_interaction_features(X_test)
    candidate_specs = {name: (model, PREDICTORS, "base_20") for name, model in model_map.items()}
    candidate_specs["Random Forest + interactions"] = (
        clone(model_map["Random Forest"]), PREDICTORS + INTERACTION_FEATURES, "base_20_plus_5_interactions"
    )
    cv_rows = []
    for name, (model, feature_names, feature_set) in candidate_specs.items():
        cv_X = X_train_engineered[feature_names] if feature_set != "base_20" else X_train[feature_names]
        cv_scores = cross_validate(model, cv_X, y_train, cv=cv, scoring=scoring,
                                   n_jobs=1, return_train_score=False, error_score="raise")
        cv_rows.append({
            "model": name,
            "feature_set": feature_set,
            "feature_count": int(len(feature_names)),
            "cv_macro_f1_mean": float(np.mean(cv_scores["test_macro_f1"])),
            "cv_macro_f1_std": float(np.std(cv_scores["test_macro_f1"], ddof=1)),
            "cv_micro_f1_mean": float(np.mean(cv_scores["test_micro_f1"])),
            "cv_weighted_f1_mean": float(np.mean(cv_scores["test_weighted_f1"])),
            "cv_accuracy_mean": float(np.mean(cv_scores["test_accuracy"])),
            "cv_balanced_accuracy_mean": float(np.mean(cv_scores["test_balanced_accuracy"])),
        })
    cv_results = pd.DataFrame(cv_rows).sort_values("cv_macro_f1_mean", ascending=False).reset_index(drop=True)
    cv_results.to_csv(results_dir / "model_comparison_cv.csv", index=False, float_format="%.6f")
    _plot_cv_comparison(cv_results, results_dir / "model_comparison_cv.png")
    best_name = str(cv_results.iloc[0]["model"])
    best_model, best_features, best_feature_set = candidate_specs[best_name]
    best_model = clone(best_model)
    X_train_best = X_train_engineered[best_features] if best_feature_set != "base_20" else X_train[best_features]
    X_test_best = X_test_engineered[best_features] if best_feature_set != "base_20" else X_test[best_features]

    print(f"[3/7] Fitting CV-selected model: {best_name}...")
    best_model.fit(X_train_best, y_train)
    y_pred = best_model.predict(X_test_best)
    final_metrics = {
        "selected_model": best_name,
        "feature_set": best_feature_set,
        "feature_count": int(len(best_features)),
        "features_used": list(best_features),
        "selection_basis": "Highest mean 5-fold macro-F1 on training split; test set not used for selection",
        "test_accuracy": float(accuracy_score(y_test, y_pred)),
        "test_balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "test_macro_f1": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
        "test_micro_f1": float(f1_score(y_test, y_pred, average="micro", zero_division=0)),
        "test_weighted_f1": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
        "test_macro_precision": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
        "test_macro_recall": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "class_labels": [int(c) for c in sorted(y.unique())],
    }
    (results_dir / "final_test_metrics.json").write_text(json.dumps(final_metrics, indent=2), encoding="utf-8")
    report_dict = classification_report(y_test, y_pred, labels=sorted(y.unique()), output_dict=True, zero_division=0)
    pd.DataFrame(report_dict).transpose().to_csv(results_dir / "classification_report.csv", float_format="%.6f")
    cm = confusion_matrix(y_test, y_pred, labels=sorted(y.unique()))
    cm_df = pd.DataFrame(cm, index=[f"true_{c}" for c in sorted(y.unique())],
                         columns=[f"pred_{c}" for c in sorted(y.unique())])
    cm_df.to_csv(results_dir / "confusion_matrix.csv")
    _plot_confusion(cm, sorted(y.unique()), results_dir / "confusion_matrix.png")
    joblib.dump(best_model, results_dir / "selected_model.joblib")

    print("[4/7] Computing permutation importance for model interpretation...")
    perm = permutation_importance(best_model, X_test_best, y_test, scoring="f1_macro",
                                  n_repeats=20, random_state=RANDOM_STATE, n_jobs=-1)
    importance = pd.DataFrame({
        "feature": best_features,
        "permutation_importance_mean": perm.importances_mean,
        "permutation_importance_std": perm.importances_std,
    }).sort_values("permutation_importance_mean", ascending=False)
    importance.to_csv(results_dir / "permutation_importance.csv", index=False, float_format="%.6f")
    _plot_importance(importance, results_dir / "permutation_importance.png")

    metadata = {
        "run_time_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": __import__("platform").python_version(),
        "pandas_version": pd.__version__,
        "scikit_learn_version": __import__("sklearn").__version__,
        "random_state": RANDOM_STATE,
        "dataset_url": DATA_URL,
        "selected_model": best_name,
    }
    (results_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print("[5/7] Generating the results-backed PDF write-up...")
    from coral_reef_ml.reporting import generate_report
    generate_report(root, cv_results, final_metrics, report_dict, importance, audit)
    print("[6/7] Generating the results-backed slide deck...")
    from coral_reef_ml.presentation import generate_presentation
    generate_presentation(root, cv_results, final_metrics, report_dict, importance, audit)
    print("[7/7] Complete.")
    print(f"CV comparison: {results_dir / 'model_comparison_cv.csv'}")
    print(f"Final write-up: {results_dir / 'Coral_Reef_Mini_Project_Report.pdf'}")
    print(f"Presentation: {results_dir / 'Coral_Reef_Mini_Project_Presentation.pptx'}")


if __name__ == "__main__":
    run_pipeline(Path(__file__).resolve().parents[2])
