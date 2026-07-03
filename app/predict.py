import joblib
import json
import pandas as pd
from pathlib import Path

# Load sekali saat module di-import, BUKAN setiap request
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
_pipeline = joblib.load(MODEL_DIR / "bank_marketing_rf-model.joblib")

with open(MODEL_DIR / "rf-model_metadata.json") as f:
    _metadata = json.load(f)

THRESHOLD = _metadata["threshold"]


def _engineer_features(raw_input: dict) -> pd.DataFrame:
    """Transformasi raw input (dari API) jadi format yang dikenali pipeline.
    Ini meniru EXACTLY apa yang dilakukan di notebook Fase 4."""
    data = raw_input.copy()

    # replikasi feature engineering pdays dari notebook
    data["was_contacted_before"] = 0 if data["pdays"] == -1 else 1
    data["pdays_clean"] = 0 if data["pdays"] == -1 else data["pdays"]
    del data["pdays"]  # kolom mentah ini di-drop, sama seperti di notebook

    return pd.DataFrame([data])


def predict_subscription(raw_input: dict) -> dict:
    """Input: dict mentah dari API (sesuai schema CustomerInput).
    Output: dict siap dikirim sebagai PredictionOutput."""
    df_input = _engineer_features(raw_input)

    proba = _pipeline.predict_proba(df_input)[0, 1]
    prediction = "yes" if proba >= THRESHOLD else "no"

    return {
        "prediction": prediction,
        "probability": round(float(proba), 4),
        "threshold_used": THRESHOLD
    }
