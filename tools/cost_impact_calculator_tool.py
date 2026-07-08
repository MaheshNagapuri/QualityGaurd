"""
Cost impact calculator tool for financial analysis of quality risks.

Calculates financial impact of defects and returns on inventory and revenue.
"""

from crewai.tools import tool

# TODO: Implement calculate_cost_impact() as CrewAI tool
# Purpose: Calculate financial impact (affected units, costs, risk level) from defect and return rates
# Parameters: defect_probability, return_rate, product_price_usd, units_in_inventory (float/int)
# Returns: String with formatted cost analysis including total financial impact and risk classification

@tool("Calculate Cost Impact")
def calculate_cost_impact(
    defect_probability: float,
    return_rate: float,
    product_price_usd: float,
    units_in_inventory: int
) -> str:
    """Estimate the financial impact of predicted defects and returns."""
    try:
        defect_ratio = defect_probability / 100
        return_ratio = return_rate / 100
        estimated_defective_units = units_in_inventory * defect_ratio
        estimated_returned_units= units_in_inventory * return_ratio
        total_affected_units = estimated_defective_units + estimated_returned_units

        defect_loss = estimated_defective_units * product_price_usd * 0.5
        return_loss = estimated_returned_units * product_price_usd * 0.3
        handling_costs = total_affected_units * product_price_usd * 0.15
        total_financial_impact = defect_loss + return_loss + handling_costs
        combined_risk = defect_probability + return_rate

        if combined_risk > 30:
            risk_level = "CRITICAL"
        elif combined_risk > 20:
            risk_level = "HIGH"
        elif combined_risk > 10:
            risk_level= "MEDIUM"
        else:
            risk_level= "LOW"
        return f"""
        Cost Impact Analysis
        -Estimated Defective Units:
        {estimated_defective_units:.0f}
        -Estimated Returned Units:
        {estimated_returned_units:.0f}
        -Total Affected Units:
        {total_affected_units:.0f}
        -Direct Loss: ${defect_loss:.2f}
        -Handling Costs: ${handling_costs:.2f}
        -Total Financial Impact: ${total_financial_impact:.2f}
        -Risk Level: {risk_level}
        """.strip()
    except Exception as e:
        return f"Error calculating cost impact: {str(e)}"
