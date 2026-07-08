"""
Supply chain agent for supplier analysis.

Analyzes supplier reliability and sourcing strategies.
Phase 2 - Parallel execution (runs with cost and market agents).
"""

from crewai import Agent
from tools.supplier_info_lookup_tool import lookup_supplier_info

# TODO: Implement create_supply_chain_agent() function
# Purpose: Create and return a CrewAI Agent configured for supply chain analysis
# with supplier lookup capability. Agent should analyze supplier reliability and sourcing risks.
# Parameters: llm (LLM instance)
# Returns: Configured Agent instance with supplier info lookup tool integration
def create_supply_chain_agent(llm):
    """
    Create Supply Chain Analysis Agent.

    Parameters
    ----------
    llm : LLM
        CrewAI LLM instance.

    Returns
    -------
    Agent
        Configured CrewAI agent for supply chain and supplier reliability analysis.
    """
    agent = Agent(
        role="Supply Chain Analyst",
        goal = (
            "Evaluate supplier reliability, manufacturing country risks, "
            "lead times, and certifications to assess supply chain stability "
        ),
        backstory=(
            "You are an expert supply chain strategist responsible for "
            "analyzing supplier reliability and sourcing risks. You use "
            "supplier databases and certification information to determine "
            "whether manufacturing sources are reliable and sustainable."
        ),
        llm=llm,

        tools=[lookup_supplier_info],

       
    )
    return agent
    
