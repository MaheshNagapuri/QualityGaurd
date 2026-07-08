"""
Supply chain analysis task for supplier evaluation.

Phase 2 - Parallel execution (runs simultaneously with cost and market agents).
"""



# TODO: Implement create_supply_chain_task() function
# Purpose: Create Phase 2 parallel task for supplier analysis and supply chain assessment
# Parameters: agent (Agent instance), product_data (dict with supplier country and details)
# Returns: Task instance with expected output: supplier_country, supplier_reliability, lead_time_days, certifications, supply_chain_assessment
# def create_supply_chain_task(agent, product_data):


from crewai import Agent, Task

def create_supply_chain_task(agent: Agent, product_data: dict) -> Task:
    country = product_data.get("product_manufacturing_country", "USA").upper()
    desc = f"""
Call lookup_supplier_info with country: "{country}"

Return ONLY valid JSON (no markdown):
{{
  "supplier_country": "{country}",
  "supplier_reliability": <float 0-5>,
  "lead_time_days": <int>,
  "certifications": ["<cert1>", "<cert2>"],
  "supply_chain_assessment": "<2 sentence risk analysis>"
}}
"""
    return Task(description=desc, agent=agent,
                expected_output='JSON with supplier_country, supplier_reliability, lead_time_days, certifications, supply_chain_assessment')
