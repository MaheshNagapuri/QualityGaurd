"""
ML training pipeline orchestrator.

Orchestrates complete ML workflow:
1. Clean training datasets
2. Train both ML models
3. Evaluate models on evaluation dataset
4. Save results

Usage:
    python ml/train_pipeline.py
"""


# TODO: Implement run_full_pipeline() and main() functions
# Purpose: Orchestrate complete ML training pipeline with 3 steps: data cleaning, model training, evaluation and showing results
# Functions needed: run_full_pipeline(training_dir, evaluation_dir, output_dir, processed_dir) coordinating full workflow and main() entry point
# Returns: Pipeline result dict with training metrics, evaluation scores, and model file paths for both defect and return rate models


    
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.data_cleaning.clean_defect_classifier_data    import clean_defect_classifier_dataset
from ml.data_cleaning.clean_return_rate_predictor_data import clean_return_rate_predictor_dataset
from ml.train_model.train_defect_classifier           import train_defect_classifier
from ml.train_model.train_return_rate_predictor       import train_return_rate_predictor
from ml.evaluation.evaluate_models                    import evaluate_all_models

 
# Run the full ML lifecycle: clean datasets, train both models, evaluate, and return aggregated results.
def run_full_pipeline(training_dir, evaluation_dir, output_dir, processed_dir) -> dict:
    training_dir   = Path(training_dir)
    evaluation_dir = Path(evaluation_dir)
    output_dir     = Path(output_dir)
    processed_dir  = Path(processed_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    print("\n[Step 1/3] Cleaning datasets...")
    defect_clean_path = processed_dir/"clean_defect_classifier_data.csv"
    return_clean_path = processed_dir/"clean_return_rate_predictor_data.csv"

    defect_clean = clean_defect_classifier_dataset(training_dir/"defect_classifier_training.csv")
    defect_clean.to_csv(defect_clean_path, index=False)
    print(f"  Defect: {len(defect_clean)} rows | Countries: {defect_clean['product_manufacturing_country'].unique().tolist()}")

    return_clean = clean_return_rate_predictor_dataset(training_dir/"return_rate_predictor_training.csv")
    return_clean.to_csv(return_clean_path, index=False)
    print(f"  Return: {len(return_clean)} rows | Countries: {return_clean['product_manufacturing_country'].unique().tolist()}")

    print("\n[Step 2/3] Training models...")
    results["defect"]  = train_defect_classifier(defect_clean_path, output_dir)
    results["return"]  = train_return_rate_predictor(return_clean_path, output_dir)

    print("\n[Step 3/3] Evaluating models...")
    eval_results = evaluate_all_models(evaluation_dir, output_dir)
    results["eval"] = eval_results
    print(f"  Defect_Classifier → {eval_results.get('defect_classifier')}")
    print(f"  Return_rate_Predictor → {eval_results.get('return_rate_predictor')}")
    print("\n=== ML Pipeline Completed ===")

    return results


# Resolve default project paths and execute the end-to-end training pipeline.
def main():
    base = Path(__file__).parent.parent
    run_full_pipeline(
        training_dir   = base/"data/training_dataset",
        evaluation_dir = base/"data/evaluation_dataset",
        output_dir     = base/"ml/models",
        processed_dir  = base/"data/processed",
        
        
    )


if __name__ == "__main__":
    print("\n=== ML Pipeline Started ===")
    main()
