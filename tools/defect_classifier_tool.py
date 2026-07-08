"""
Defect classifier tool for predicting defect probability.

Uses trained Random Forest model to predict defect probability (0-100%)
based on product features.
"""



# TODO: Implement predict_defect_probability() as CrewAI tool
# Purpose: Predict defect probability (0-100%) using trained Random Forest ML model
# Parameters: product features (9 numerical/categorical features as individual parameters)
# Returns: String with formatted defect probability percentage prediction

from crewai.tools import tool
import pickle
import numpy as np
from pathlib import Path

@tool("Predict Defect Probability")
def predict_defect_probability(
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
    """Predict product defect probability (0-100%) using trained Random Forest model."""
    try:
        models_dir = Path(__file__).resolve().parent.parent / "ml" / "models"
        model   = pickle.load(open(models_dir/"defect_classifier.pkl", "rb"))
        scaler  = pickle.load(open(models_dir/"defect_scaler.pkl",     "rb"))
        encoder = pickle.load(open(models_dir/"defect_encoder.pkl",    "rb"))

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
        return f"Defect Probability: {prediction:.2f}%"
    except Exception as e:
        return f"Error predicting defect probability: {str(e)}"
