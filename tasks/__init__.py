"""Tasks module for QualityGuard - Task definitions for AI agents."""

from .product_analysis_task import create_product_analysis_task
from .quality_assessment_task import create_quality_assessment_task
from .supply_chain_task import create_supply_chain_task
from .cost_impact_task import create_cost_impact_task
from .market_trend_task import create_market_trend_task
from .recommendation_task import create_recommendation_task
from .feedback_analysis_task import create_feedback_analysis_task

__all__ = [
    'create_product_analysis_task',
    'create_quality_assessment_task',
    'create_supply_chain_task',
    'create_cost_impact_task',
    'create_market_trend_task',
    'create_recommendation_task',
    'create_feedback_analysis_task',
]
