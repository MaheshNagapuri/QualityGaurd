"""
Quality assessor agent for comprehensive quality evaluation.

Assesses product quality using return rate predictions.
Phase 1 - Sequential execution (runs second, after product analyzer).
"""

from crewai import Agent
from tools.return_rate_predictor_tool import predict_return_rate
# TODO: Implement create_quality_assessor_agent() function
# Purpose: Create CrewAI Agent for quality assessment and return rate prediction
# using ML model. Phase 1 agent that runs after product analyzer.
# Parameters: llm (LLM instance)
# Returns: Configured Agent with return rate prediction capabilities and quality scoring logic
def create_quality_assessor_agent(llm):
    """
    Create Quality Assessor Agent.

    Parameters
    ----------
    llm : LLM
        CrewAI LLM instance.

    Returns
    -------
    Agent
        Configured CrewAI agent for quality assessment and return rate prediction.
    """
    agent = Agent(
        role = "Quality Assessment Specialist",
        goal = (
            "Evaluate product quality and predict expected customer return "
            "rates using machine learning tools "
        ),
        backstory=(
            "You are a quality assurance specialist responsible for evaluating  "
            "product reliability and predicting potential return rates based on "
            "customer reviews, ratings, and product features."
        ),
        llm=llm,

        tools = [predict_return_rate]

    )
    return agent
    
