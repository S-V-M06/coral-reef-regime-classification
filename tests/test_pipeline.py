from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from coral_reef_ml.pipeline import PREDICTORS, build_models


def test_predictor_count_and_boundaries():
    assert len(PREDICTORS) == 20
    assert PREDICTORS[0] == "Effluent"
    assert PREDICTORS[-1] == "Depth"
    assert "Regime1" not in PREDICTORS
    assert "Coral" not in PREDICTORS


def test_all_model_pipelines_fit_small_synthetic_data():
    rng = np.random.default_rng(42)
    X = pd.DataFrame(rng.normal(size=(80, len(PREDICTORS))), columns=PREDICTORS)
    X.loc[0:2, "Complexity"] = np.nan
    y = pd.Series(np.tile([1, 2, 3, 5], 20))
    for model in build_models().values():
        model.fit(X, y)
        preds = model.predict(X.iloc[:5])
        assert len(preds) == 5
        assert set(preds).issubset({1, 2, 3, 5})


def test_interaction_features_are_derived_without_changing_base_columns():
    from coral_reef_ml.pipeline import INTERACTION_FEATURES, add_interaction_features
    row = {name: 1.0 for name in PREDICTORS}
    X = pd.DataFrame([row])
    out = add_interaction_features(X)
    assert list(out.columns[:len(PREDICTORS)]) == PREDICTORS
    assert all(name in out.columns for name in INTERACTION_FEATURES)
    assert len(out.columns) == 25
    assert out.loc[0, "WavePower_x_Depth"] == out.loc[0, "WAV_CLIM_M"] * out.loc[0, "Depth"]
