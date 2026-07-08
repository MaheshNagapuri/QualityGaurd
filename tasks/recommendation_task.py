"""
Recommendation task for synthesizing all analyses.

Phase 3 - Sequential execution (runs last, after all parallel agents complete).
"""



# TODO: Implement create_recommendation_task() function
# Purpose: Create Phase 3 task for synthesizing all analyses into final recommendation and quality grade
# Parameters: agent (Agent), product_data (dict), analysis_results (dict with defect_prob and return_rate)
# Returns: Task instance with expected output: overall_assessment, recommendations, approval_status, final_quality_grade

from crewai import Agent, Task
from config.constants import GRADE_THRESHOLDS

def _grade(d, r):
    t = GRADE_THRESHOLDS
    if d < t["EXCELLENT"]["defect_prob"] and r < t["EXCELLENT"]["return_rate"]: return "EXCELLENT"
    if d < t["GOOD"]["defect_prob"]      and r < t["GOOD"]["return_rate"]:      return "GOOD"
    if d < t["ACCEPTABLE"]["defect_prob"]and r < t["ACCEPTABLE"]["return_rate"]:return "ACCEPTABLE"
    return "POOR"

def create_recommendation_task(agent: Agent, product_data: dict, analysis: dict) -> Task:
    dp     = analysis.get("defect_probability", 0)
    rr     = analysis.get("return_rate", 0)
    g      = _grade(float(dp), float(rr))
    status = "APPROVED" if g in ("EXCELLENT","GOOD") else ("REJECTED" if g == "POOR" else "PENDING_REVIEW")
    name   = product_data.get("name") or product_data.get("product_name", "Unknown")
    desc = f"""
Synthesize quality assessment for: {name}
  Defect Probability: {dp}%   Return Rate: {rr}%
  Supply Chain: {analysis.get('supplier_info','N/A')}
  Financial Impact: {analysis.get('financial_impact','N/A')}
  Market Demand: {analysis.get('market_demand','N/A')}
  Competitive: {analysis.get('competitive_position','N/A')}
  Pre-calculated Grade: {g}

Return ONLY valid JSON (no markdown):
{{
  "overall_assessment": "<2 sentence summary>",
  "recommendations": ["<rec 1>", "<rec 2>", "<rec 3>"],
  "approval_status": "{status}",
  "final_quality_grade": "{g}"
}}
"""
    return Task(description=desc, agent=agent,
                expected_output='JSON with overall_assessment, recommendations, approval_status, final_quality_grade')
