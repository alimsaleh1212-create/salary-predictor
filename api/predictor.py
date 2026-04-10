"""Loads the trained model and runs inference."""

import os
from pathlib import Path

import joblib
import pandas as pd

# Resolve model path relative to project root (works both locally and on Railway)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MODEL_PATH = _PROJECT_ROOT / "models" / "random_forest_model.joblib"

_model = None


def _get_model():
    global _model
    if _model is None:
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {_MODEL_PATH}")
        _model = joblib.load(_MODEL_PATH)
    return _model


def predict(features_df: pd.DataFrame) -> list[float]:
    """
    Run the trained pipeline on pre-transformed features.
    Returns a list of predicted salary values in USD.
    """
    model = _get_model()
    predictions = model.predict(features_df)
    return [float(p) for p in predictions]
