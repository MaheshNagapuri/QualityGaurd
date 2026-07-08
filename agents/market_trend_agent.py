"""
Market trend agent for market analysis.

Analyzes market trends and competitive positioning.
Phase 2 - Parallel execution (runs with supply chain and cost agents).
"""

from crewai import Agent

# TODO: Implement create_market_trend_agent() function
# Purpose: Create and return a CrewAI Agent configured for market trend analysis
# with demand and competitive positioning insights. Agent runs in parallel Phase 2.
# Parameters: llm (LLM instance)
# Returns: Configured Agent instance with market analysis capabilities
def create_market_trend_agent(llm):
    """
    Create Market Trend Analysis Agent.

    Parameters
    ----------
    llm : LLM
        CrewAI LLM instance.

    Returns
    -------
    Agent
        Configured CrewAI agent for market trend and competitive analysis.
    """
    agent = Agent(
        role="Market Treand Analyst",
        goal = (
            "Analyze market demand, customer sentiment and competitive "
            "positioning to determine market opportunities and risks."
            
        ),
        backstory=(
            "You are a market intelligence expert responsible for identifying "
            "product demand trends and evaluating competitive positioning. "
            "You analyze market signals such as demand index, customer reviews, "
            "pricing, and industry trends to determine market visibility."
        ),
        llm=llm,

        tools=[],

        verbose=False
    )
    return agent
