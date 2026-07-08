"""
Data cleaning for return rate predictor training dataset.

Handles noise removal and data validation:
- Missing values (dropna)
- Duplicate records (remove)
- Numerical outliers (IQR method)
- Out-of-range values (hard bounds)
- Invalid categories (filter)
"""

# TODO: Implement clean_return_rate_predictor_dataset() function
# Purpose: Clean raw return rate predictor training data by removing noise, duplicates, outliers, and invalid values
# Parameters: input_file (raw CSV path with training data)
# Returns: Cleaned pandas DataFrame with valid records ready for model training (removes NaN, duplicates, outliers via IQR)


import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.constants import VALIDATION_BOUNDS, VALID_COUNTRIES

# Clean return-rate training data by removing nulls/duplicates, enforcing bounds, filtering countries, and trimming IQR outliers.
def clean_return_rate_predictor_dataset(input_file):
    df = pd.read_csv(input_file)
    df = df.dropna()
    df = df.drop_duplicates()
    if "product_manufacturing_country" in df.columns:
        df["product_manufacturing_country"] = df["product_manufacturing_country"].str.upper().str.strip()
        df = df[df["product_manufacturing_country"].isin(VALID_COUNTRIES)]
    for column, (min_val, max_val) in VALIDATION_BOUNDS.items():
        if column in df.columns:
            df = df[(df[column] >= min_val) & (df[column] <= max_val)]
    for col in VALIDATION_BOUNDS.keys():
        if col not in df.columns:
            continue
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        df = df[(df[col] >= Q1 - 1.5*IQR) & (df[col] <= Q3 + 1.5*IQR)]
    return df.reset_index(drop=True)
