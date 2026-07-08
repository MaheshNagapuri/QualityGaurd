"""
Product analyzer agent for initial product analysis.

Analyzes product features and characteristics using defect classifier.
Phase 1 - Sequential execution (runs first).
"""

from crewai import Agent
from tools.defect_classifier_tool import predict_defect_probability

# TODO: Implement create_product_analyzer_agent() function
# Purpose: Create and return a CrewAI Agent configured for product quality analysis
# with defect probability prediction capability. Agent should use ML model via tool.
# Parameters: llm (LLM instance)
# Returns: Configured Agent instance with appropriate role, goal, backstory, and tools
def create_product_analyzer_agent(llm):
    """
    Create Product Analyzer Agent.

    Parameters
    ----------
    llm : LLM
        CrewAI LLM instance.
    Returns
    -------
    Agent
        Configured CrewAI agent for product defect analysis.
    """
    agent = Agent(
        role = "Product Quality Analyzer",
        goal = (
            """Analyzes product characteristics and predicts the probability 
            of manufacturing defects using machine learning tools"""
        ),
        backstory=(
            "You are a product quality analysis expert specializing in "
            "identifying potential manufacturing defects before products "
            "reach the market. You use machine learning models to assess "
            "product features and estimate defect risks."
        ),
        llm=llm,
        tools = [predict_defect_probability],
    )
    return agent
