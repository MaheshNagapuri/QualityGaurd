# """
# Defect classifier tool for predicting defect probability.

# Uses trained Random Forest model to predict defect probability (0-100%)
# based on product features.
# """

# from crewai.tools import tool

# # TODO: Implement predict_defect_probability() as CrewAI tool
# # Purpose: Predict defect probability (0-100%) using trained Random Forest ML model
# # Parameters: product features (9 numerical/categorical features as individual parameters)
# # Returns: String with formatted defect probability percentage prediction

# import pickle
# import numpy as np
# import pandas as pd
# from pathlib import Path


# def _encode_country(encoder, product_manufacturing_country: str) -> int:
#     normalized_country = str(product_manufacturing_country).strip().upper()
#     known_labels = list(getattr(encoder, "classes_", []))
#     fallback_label = known_labels[0] if known_labels else normalized_country
#     safe_country = normalized_country if normalized_country in known_labels else fallback_label
#     return int(encoder.transform([safe_country])[0])


# @tool("Predict Defect Probability")
# def predict_defect_probability(
#     product_price_usd: float,
#     warranty_period_months: int,
#     customer_review_count: int,
#     customer_average_rating: float,
#     material_quality_score: int,
#     supplier_reliability_rating: float,
#     product_age_days: int,
#     market_demand_index: float,
#     product_manufacturing_country: str
# ) -> str:
#     """Predict defect probability for a product using the trained model."""
#     try:
#         project_root = Path(__file__).resolve().parent.parent
#         models_dir = project_root/"ml"/"models"
#         model_path = models_dir/"defect_classifier.pkl"
#         scaler_path = models_dir/"defect_scaler.pkl"
#         encoder_path = models_dir/"defect_encoder.pkl"

#         with open(model_path, "rb") as f:
#             model= pickle.load(f)
#         with open(scaler_path, "rb") as f:
#             scaler= pickle.load(f)
#         with open(encoder_path, "rb") as f:
#             encoder= pickle.load(f)
        
#         country_encoded = _encode_country(encoder, product_manufacturing_country)
#         features= [
#             country_encoded,
#             product_price_usd,
#             warranty_period_months,
#             customer_review_count,
#             customer_average_rating,
#             material_quality_score,
#             supplier_reliability_rating,
#             product_age_days,
#             market_demand_index
#         ]
#         X = pd.DataFrame([features], columns=[
#             "product_manufacturing_country",
#             "product_price_usd",
#             "warranty_period_months",
#             "customer_review_count",
#             "customer_average_rating",
#             "material_quality_score",
#             "supplier_reliability_rating",
#             "product_age_days",
#             "market_demand_index",
#         ])
#         X_scaled= scaler.transform(X)
#         prediction= model.predict(X_scaled)[0]
#         defect_probability= max(0, min(float(prediction), 100))
#         return f"Defect Probability: {defect_probability:.2f}%"
#     except Exception as e:
#         return f"Error predicting defect probability: {str(e)}"
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
