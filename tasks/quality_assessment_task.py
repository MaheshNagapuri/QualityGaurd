"""
Quality assessment task for return rate prediction.

Phase 1 - Sequential execution (runs second, after product analysis).
"""



# TODO: Implement create_quality_assessment_task() function
# Purpose: Create Phase 1 task for return rate prediction and quality score calculation
# Parameters: agent (Agent instance), product_data (dict with product features)
# Returns: Task instance with expected output: return_rate, quality_score, assessment_summary

from crewai import Agent, Task

def create_quality_assessment_task(agent: Agent, product_data: dict) -> Task:
    p = product_data
    desc = f"""
Call the predict_return_rate tool with these exact values:
  product_price_usd: {p.get('product_price_usd', 0)}
  warranty_period_months: {p.get('warranty_period_months', 0)}
  customer_review_count: {p.get('customer_review_count', 0)}
  customer_average_rating: {p.get('customer_average_rating', 3.0)}
  material_quality_score: {p.get('material_quality_score', 3)}
  supplier_reliability_rating: {p.get('supplier_reliability_rating', 3.0)}
  product_age_days: {p.get('product_age_days', 180)}
  market_demand_index: {p.get('market_demand_index', 50.0)}
  product_manufacturing_country: {p.get('product_manufacturing_country', 'USA')}

Calculate quality_score = 100 - return_rate (clamped 0-100).
Return ONLY valid JSON (no markdown):
{{"return_rate": <float>, "quality_score": <float>, "assessment_summary": "<string>"}}
"""
    return Task(description=desc, agent=agent,
                expected_output='JSON with return_rate, quality_score, assessment_summary')
