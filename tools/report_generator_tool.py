"""
Report generator tool for creating assessment recommendations.

Generates comprehensive quality assessment reports and recommendations.
"""

from crewai.tools import tool

# TODO: Implement generate_quality_report() as CrewAI tool
# Purpose: Generate comprehensive quality assessment report with grade determination and recommendations
# Parameters: product_name, defect_probability, return_rate, supplier_country, supplier_score, financial_impact, overall_assessment
# Returns: Formatted quality report string ready for human review with quality grade and recommendations

from config.constants import QUALITY_SCORE_THRESHOLDS

@tool("Generate Quality Report")
def generate_quality_report(
    product_name: str,
    defect_probability: float,
    return_rate: float,
    supplier_country: str,
    supplier_score: float,
    financial_impact: float,
    overall_assessment: str
) -> str:
    """Generate a formatted quality assessment report and recommendations."""
    try:
        quality_score = 100 - ((defect_probability + return_rate) / 2)
        if quality_score >= QUALITY_SCORE_THRESHOLDS["EXCELLENT"]:
            quality_grade= "EXCELLENT"
        elif quality_score >= QUALITY_SCORE_THRESHOLDS["GOOD"]:
            quality_grade= "GOOD"
        elif quality_score >= QUALITY_SCORE_THRESHOLDS["ACCEPTABLE"]:
            quality_grade= "ACCEPTABLE"
        else:
            quality_grade= "POOR"
        recommendations = []
        if defect_probability > 10:
            recommendations.append("Investigate manufacturing process to reduce defect probability.")
        if return_rate > 10:
            recommendations.append("Review warranty terms and customer support policies.")
        if supplier_score < 3.5:
            recommendations.append("Evaluate supplier reliability and consider alternative sourcing.")
        if financial_impact > 50000:
            recommendations.append("Mitigate financial risk by improving quality control before scaling inventory.")
        if not recommendations:
            recommendations.append("Maintain current product quality monitoring procedures.")
        recommendation_text = "\n".join([f"- {r}" for r in recommendations])
        report= f"""
        Quality Assessment Report
        --------------------------------------------------------
        Product Name: {product_name}

        Quality Metrics
        - Defect Probability:
        {defect_probability:.2f}%
        - Return Rate: {return_rate:.2f}%
        - Quality Score: {quality_score:.2f}%
        - Quality Grade: {quality_grade}

        Supply Chain
        - Supplier Country: {supplier_country}
        - Supplier Reliability Score: {supplier_score}/5

        Financial Impact
        - Estimated Financial Impact: ${financial_impact:,.2f}

        Overall Assessment
        {overall_assessment}

        Recommendations
        {recommendation_text}
        """.strip()
        return report
    except Exception as e:
        return f"Error generating quality report: {str(e)}"
