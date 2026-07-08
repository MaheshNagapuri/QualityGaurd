"""
Evaluate trained ML models on evaluation dataset.

Calculates performance metrics (R², MAE, RMSE) for both models.
"""


# # TODO: Implement evaluate_all_models() function
# # Purpose: Evaluate both trained ML models (defect classifier and return rate predictor) on evaluation datasets
# # Parameters: evaluation_dir (CSV files with test data), model_dir (directory with .pkl model artifacts)
# # Returns: Dict with performance metrics (R², MAE, RMSE, MSE) for both defect and return rate models


import os, sys, pickle
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.constants import ML_FEATURES_ORDERED


# Load the correct model, scaler, and encoder artifacts for either defect or return-rate evaluation.
def _load_artifacts(model_dir: Path, prefix: str):
    if prefix == "defect":
        model   = pickle.load(open(model_dir/"defect_classifier.pkl", "rb"))
        scaler  = pickle.load(open(model_dir/"defect_scaler.pkl",     "rb"))
        encoder = pickle.load(open(model_dir/"defect_encoder.pkl",    "rb"))
    else:
        model   = pickle.load(open(model_dir/"return_predictor.pkl",  "rb"))
        scaler  = pickle.load(open(model_dir/"return_scaler.pkl",     "rb"))
        encoder = pickle.load(open(model_dir/"return_encoder.pkl",    "rb"))
    return model, scaler, encoder


# Run preprocessing plus inference on one dataset and return standard regression metrics.
def _evaluate(df, target_col, model, scaler, encoder) -> dict:
    df["product_manufacturing_country"] = df["product_manufacturing_country"].str.upper().str.strip()
    known = set(encoder.classes_)
    df["product_manufacturing_country"] = df["product_manufacturing_country"].apply(
        lambda x: x if x in known else list(known)[0]
    )
    X = df[ML_FEATURES_ORDERED].copy()
    X["product_manufacturing_country"] = encoder.transform(X["product_manufacturing_country"])
    X_scaled = scaler.transform(X)
    y_true   = df[target_col].values
    y_pred   = np.clip(model.predict(X_scaled), 0, 100)
    mse  = float(mean_squared_error(y_true, y_pred))
    mae  = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2   = float(r2_score(y_true, y_pred))
    return {"R2": round(r2,4), "MAE": round(mae,4), "RMSE": round(rmse,4), "MSE": round(mse,4)}


# Evaluate both trained models against their evaluation CSVs and return per-model metric summaries.
def evaluate_all_models(evaluation_dir, model_dir) -> dict:
    evaluation_dir = Path(evaluation_dir)
    model_dir      = Path(model_dir)
    results        = {}

    # Defect classifier
    defect_csv = evaluation_dir / "defect_classifier_evaluation.csv"
    if defect_csv.exists():
        try:
            df = pd.read_csv(defect_csv)
            model, scaler, encoder = _load_artifacts(model_dir, "defect")
            # ✅ FIX: handle both old and new column names
            if "defect_probability" in df.columns:
                target = "defect_probability"
            elif "predicted_defect_probability_percent" in df.columns:
                target = "predicted_defect_probability_percent"
            else:
                raise ValueError(f"No target column found. Columns: {list(df.columns)}")
            results["defect_classifier"] = _evaluate(df, target, model, scaler, encoder)
        except Exception as e:
            results["defect_classifier"] = {"error": str(e)}
    else:
        results["defect_classifier"] = {"error": "Evaluation dataset not found"}

    # Return rate predictor
    return_csv = evaluation_dir / "return_rate_predictor_evaluation.csv"
    if return_csv.exists():
        try:
            df = pd.read_csv(return_csv)
            model, scaler, encoder = _load_artifacts(model_dir, "return")
            # ✅ FIX: handle both old and new column names
            if "return_rate" in df.columns:
                target = "return_rate"
            elif "predicted_return_rate_percent" in df.columns:
                target = "predicted_return_rate_percent"
            else:
                raise ValueError(f"No target column found. Columns: {list(df.columns)}")
            results["return_rate_predictor"] = _evaluate(df, target, model, scaler, encoder)
        except Exception as e:
            results["return_rate_predictor"] = {"error": str(e)}
    else:
        results["return_rate_predictor"] = {"error": "Evaluation dataset not found"}

    return results
