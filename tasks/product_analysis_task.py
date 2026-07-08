"""
Product analysis task for defect prediction.

Phase 1 - Sequential execution (runs first).
"""


# # TODO: Implement create_product_analysis_task() function
# # Purpose: Create Phase 1 task for defect probability prediction using ML classifier
# # Parameters: agent (Agent instance), product_data (dict with product features)
# # Returns: Task instance with expected output: defect_probability, analysis_summary, risk_level
# def create_product_analysis_task(agent, product_data):

from crewai import Agent, Task

def create_product_analysis_task(agent: Agent, product_data: dict) -> Task:
    p = product_data
    desc = f"""
Call the predict_defect_probability tool with these exact values:
  product_price_usd: {p.get('product_price_usd', 0)}
  warranty_period_months: {p.get('warranty_period_months', 0)}
  customer_review_count: {p.get('customer_review_count', 0)}
  customer_average_rating: {p.get('customer_average_rating', 3.0)}
  material_quality_score: {p.get('material_quality_score', 3)}
  supplier_reliability_rating: {p.get('supplier_reliability_rating', 3.0)}
  product_age_days: {p.get('product_age_days', 180)}
  market_demand_index: {p.get('market_demand_index', 50.0)}
  product_manufacturing_country: {p.get('product_manufacturing_country', 'USA')}

Return ONLY valid JSON (no markdown):
{{"defect_probability": <float>, "risk_level": "<CRITICAL|HIGH|MEDIUM|LOW>", "analysis_summary": "<string>"}}

Risk levels: CRITICAL>15%, HIGH>10%, MEDIUM>5%, LOW<=5%
"""
    return Task(description=desc, agent=agent,
                expected_output='JSON with defect_probability, risk_level, analysis_summary')
