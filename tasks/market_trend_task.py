"""
Market trend analysis task for competitive intelligence.

Phase 2 - Parallel execution (runs simultaneously with supply chain and cost agents).
"""


# TODO: Implement create_market_trend_task() function
# Purpose: Create Phase 2 parallel task for market demand and competitive positioning analysis
# Parameters: agent (Agent instance), product_data (dict with market and customer metrics)
# Returns: Task instance with expected output: market_demand, competitive_position, trend_analysis


from crewai import Agent, Task

def create_market_trend_task(agent: Agent, product_data: dict) -> Task:
    mdi     = product_data.get("market_demand_index", 50)
    rating  = product_data.get("customer_average_rating", 3.0)
    reviews = product_data.get("customer_review_count", 100)
    price   = product_data.get("product_price_usd", 100)
    desc = f"""
Analyze market positioning:
  market_demand_index: {mdi}  (0-30=LOW, 30-60=MODERATE, 60-85=HIGH, 85-100=VERY HIGH)
  customer_average_rating: {rating}
  customer_review_count: {reviews}
  product_price_usd: {price}

Competitive: DOMINANT(rating>=4.5 & reviews>=1000), STRONG(>=4.0 & >=500), MODERATE(>=3.5 & >=100), else WEAK.

Return ONLY valid JSON (no markdown):
{{"market_demand": "<level>", "competitive_position": "<position>", "trend_analysis": "<2 sentences>"}}
"""
    return Task(description=desc, agent=agent,
                expected_output='JSON with market_demand, competitive_position, trend_analysis')
