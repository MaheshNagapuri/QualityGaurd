"""
Train return rate prediction model.

Predicts expected return rate (0-100%) based on product features using a
lightweight Gradient Boosting model.
"""



# TODO: Implement train_return_rate_predictor() function
# Purpose: Train Gradient Boosting regression model to predict return rate percentage (0-100%) from 9 product features
# Parameters: training_file (cleaned CSV path), output_dir (directory for model artifacts .pkl files)
# Returns: Dict with training metrics (R², MAE, RMSE, MSE) and saves 3 pickle files (model, scaler, encoder)


import pickle, sys, os
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.constants import ML_FEATURES_ORDERED, MODEL_HYPERPARAMETERS, TEST_SIZE, RANDOM_STATE

# Train and persist the return-rate regression pipeline (encoder, scaler, model) and return evaluation metrics.
def train_return_rate_predictor(training_file, output_dir):
    df = pd.read_csv(training_file)
    target_col = "return_rate"
    if target_col not in df.columns:
        target_col = "predicted_return_rate_percent"

    df["product_manufacturing_country"] = df["product_manufacturing_country"].str.upper().str.strip()
    X = df[ML_FEATURES_ORDERED].copy()
    y = df[target_col].values

    encoder = LabelEncoder()
    X["product_manufacturing_country"] = encoder.fit_transform(X["product_manufacturing_country"])

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    model = GradientBoostingRegressor(random_state=RANDOM_STATE)
    model.fit(X_train, y_train)

    y_pred  = model.predict(X_test)
    metrics = {
        "R2":   float(r2_score(y_test, y_pred)),
        "MAE":  float(mean_absolute_error(y_test, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "MSE":  float(mean_squared_error(y_test, y_pred)),
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pickle.dump(model,   open(output_dir/"return_predictor.pkl", "wb"))
    pickle.dump(scaler,  open(output_dir/"return_scaler.pkl",    "wb"))
    pickle.dump(encoder, open(output_dir/"return_encoder.pkl",   "wb"))
    print(f"Return predictor trained. R²={metrics['R2']:.3f}")
    return metrics
