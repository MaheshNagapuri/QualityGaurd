"""
Return rate predictor tool for predicting expected return rate.

Uses trained Gradient Boosting model to predict return rate (0-100%)
based on product features.
"""

from crewai.tools import tool

# TODO: Implement predict_return_rate() as CrewAI tool
# Purpose: Predict return rate (0-100%) using trained Gradient Boosting ML model
# Parameters: product features (9 numerical/categorical features as individual parameters)
# Returns: String with formatted return rate percentage prediction

from crewai.tools import tool
import pickle
import numpy as np
from pathlib import Path

@tool("Predict Return Rate")
def predict_return_rate(
    product_price_usd: float,
    warranty_period_months: int,
    customer_review_count: int,
    customer_average_rating: float,
    material_quality_score: int,
    supplier_reliability_rating: float,
    product_age_days: int,
    market_demand_index: float,
    product_manufacturing_country: str
) -> str:
    """Predict product return rate (0-100%) using trained Random Forest model."""
    try:
        models_dir = Path(__file__).resolve().parent.parent / "ml" / "models"
        model   = pickle.load(open(models_dir/"return_predictor.pkl", "rb"))
        scaler  = pickle.load(open(models_dir/"return_scaler.pkl",    "rb"))
        encoder = pickle.load(open(models_dir/"return_encoder.pkl",   "rb"))

        country         = product_manufacturing_country.upper().strip()
        country_encoded = encoder.transform([country])[0]

        features = np.array([[
            country_encoded,
            product_price_usd,
            warranty_period_months,
            customer_review_count,
            customer_average_rating,
            material_quality_score,
            supplier_reliability_rating,
            product_age_days,
            market_demand_index,
        ]])
        X_scaled   = scaler.transform(features)
        prediction = float(np.clip(model.predict(X_scaled)[0], 0, 100))
        return f"Return Rate: {prediction:.2f}%"
    except Exception as e:
        return f"Error predicting return rate: {str(e)}"
