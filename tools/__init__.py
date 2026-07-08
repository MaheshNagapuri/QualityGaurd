"""Tools module for QualityGuard - Custom tools for AI agents."""

from .defect_classifier_tool import predict_defect_probability
from .return_rate_predictor_tool import predict_return_rate
from .cost_impact_calculator_tool import calculate_cost_impact
from .supplier_info_lookup_tool import lookup_supplier_info
from .report_generator_tool import generate_quality_report
from .feedback_analysis_tool import (
    analyze_rejection_patterns,
    detect_prediction_mismatches,
    get_threshold_adjustments_data,
    recommend_threshold_adjustments,
    get_feedback_summary_data,
    get_feedback_summary,
)

__all__ = [
    'predict_defect_probability',
    'predict_return_rate',
    'calculate_cost_impact',
    'lookup_supplier_info',
    'generate_quality_report',
    'analyze_rejection_patterns',
    'detect_prediction_mismatches',
    'get_threshold_adjustments_data',
    'recommend_threshold_adjustments',
    'get_feedback_summary_data',
    'get_feedback_summary',
]
