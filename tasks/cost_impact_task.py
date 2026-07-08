"""
Cost impact analysis task for financial risk assessment.

Phase 2 - Parallel execution (runs simultaneously with supply chain and market agents).
"""



# TODO: Implement create_cost_impact_task() function
# Purpose: Create Phase 2 parallel task for financial impact analysis using defect and return rates
# Parameters: agent (Agent), product_data (dict), defect_prob (float), return_rate (float)
# Returns: Task instance with expected output: estimated_defective_units, estimated_returned_units, total_financial_impact, risk_level, cost_analysis_summary

from crewai import Agent, Task

def create_cost_impact_task(agent: Agent, product_data: dict, defect_prob: float, return_rate: float) -> Task:
    price = product_data.get("product_price_usd", 100)
    inv   = product_data.get("inventory", 1000)
    desc = f"""
Call calculate_cost_impact tool with:
  defect_probability: {defect_prob}
  return_rate: {return_rate}
  product_price: {price}
  inventory_units: {inv}

Return ONLY valid JSON (no markdown):
{{
  "estimated_defective_units": <int>,
  "estimated_returned_units": <int>,
  "total_financial_impact": <float>,
  "risk_level": "<CRITICAL|HIGH|MEDIUM|LOW>",
  "cost_breakdown": "<string>"
}}
"""
    return Task(description=desc, agent=agent,
                expected_output='JSON with cost impact fields')
