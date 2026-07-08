"""
Supplier information lookup tool for supply chain analysis.

Retrieves supplier metrics and certification data by manufacturing country.
"""

from crewai.tools import tool

# TODO: Implement lookup_supplier_info() as CrewAI tool
# Purpose: Retrieve supplier metrics (reliability, lead time, certifications) by manufacturing country
# Parameters: manufacturing_country (str - country name for supplier lookup)
# Returns: String with formatted supplier information including reliability score and certifications

from config.constants import SUPPLIER_DATA

@tool("Supplier Info Lookup")
def lookup_supplier_info(manufacturing_country: str) -> str:
    """Look up supplier reliability, lead time, and certifications by country."""
    try:
        country = manufacturing_country.upper()
        supplier = SUPPLIER_DATA.get(country)

        if not supplier:
            return f"Supplier information not available for country: {manufacturing_country}"
        reliability = supplier.get("reliability_score", "N/A")
        lead_time = supplier.get("lead_time_days", "N/A")
        certifications = supplier.get("certifications", [])
        defect_rate = supplier.get("average_defect_rate", "N/A")
        cert_list = ", ".join(certifications) if certifications else "None"
        return f"""
        Supplier Information
        - Supplier Country: {country}
        - Supplier Reliability: {reliability}/5
        - Lead Time: {lead_time} days
        - Certifications: {cert_list}
        - Average Defect Rate: {defect_rate}%
        """.strip()

    except Exception as e:
        return f"Error retrieving supplier information: {str(e)}"
