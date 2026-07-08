"""
Recommendation agent for generating assessment recommendations.

Synthesizes all analysis and generates final recommendations.
Phase 3 - Sequential execution (runs last, after all parallel agents complete).
"""

from crewai import Agent
from tools.report_generator_tool import generate_quality_report

# TODO: Implement create_recommendation_agent() function
# Purpose: Create and return a CrewAI Agent configured for final recommendation synthesis
# using quality report generation. Agent synthesizes all phase analyses and outputs final grade.
# Parameters: llm (LLM instance)
# Returns: Configured Agent instance with report generator tool for quality recommendations
def create_recommendation_agent(llm):
    """
    Create Recommendation Agent.

    Parameters
    ----------
    llm : LLM
        CrewAI LLM instance.

    Returns
    -------
    Agent
        Configured CrewAI agent responsible for synthesizing all analysis
        and generating final quality recommendations.
    """
    agent = Agent(
        role="Quality Recommendation Specialist",
        goal = (
            "Synthesize all analysis results including defect probability, "
            "return rate, supply chain reliability, financial impact, and "
            "market trends to produce a final quality assessment report "
            "and actionable recommendations"
            
        ),
        backstory=(
            "You are a senior product quality advisor responsible for "
            "combining insights from engineering, finance, supply chain, "
            "and market analysis to determaine whether a product should be "
            "approved, improved, or rejected before market release."
        ),
        llm=llm,

        tools=[generate_quality_report],

    )
    return agent
