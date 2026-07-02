"""
Cost impact agent for financial analysis.

Analyzes financial impact of quality risks and defects.
Phase 2 - Parallel execution (runs with supply chain and market agents).
"""

from crewai import Agent
from tools.cost_impact_calculator_tool import calculate_cost_impact

# TODO: Implement create_cost_impact_agent() function
# Purpose: Create and return a CrewAI Agent configured for financial impact analysis
# using cost calculator tool. Agent should evaluate economic impact of quality risks.
# Parameters: llm (LLM instance)
# Returns: Configured Agent instance with cost impact calculation capabilities
def create_cost_impact_agent(llm):
    """
    Create Cost Impact Analysis Agent.

    Parameters
    ----------
    llm : LLM
        CrewAI LLM instance.

    Returns
    -------
    Agent
        Configured CrewAI agent for financial risk and cost impact analysis.
    """
    agent = Agent(
        role="Financial Impact Analyst",
        goal = (
            "Evaluate the financial risks for associated with product defects "
            "and return rates by calculating potential revenue losses and "
            "inventory impact."
        ),
        backstory=(
            "You are a financial analyst specializing in product risk assessment. "
            "Your responsibility is to estimate the economic impact of product  "
            "quality issues, including defects and returns, and help decision "
            "makers understand potential financial exposure."
        ),
        llm=llm,

        tools=[calculate_cost_impact],

        verbose=False
    )
    return agent
    
