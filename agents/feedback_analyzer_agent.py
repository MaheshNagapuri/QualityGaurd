"""
Feedback Analyzer Agent - Processes human feedback to improve decisions.

Analyzes feedback patterns and generates actionable insights for quality improvement.
"""

from crewai import Agent
from tools.feedback_analysis_tool import(
    analyze_rejection_patterns,
    detect_prediction_mismatches,
    recommend_threshold_adjustments,
    get_feedback_summary
)

# TODO: Implement create_feedback_analyzer_agent() function
# Purpose: Create and return a CrewAI Agent configured for feedback analysis and pattern detection.
# Agent should analyze rejection patterns, detect prediction mismatches, and recommend adjustments.
# Parameters: llm (LLM instance)
# Returns: Configured Agent instance with feedback analysis tools for Phase 4 processing
def create_feedback_analyzer_agent(llm):
    """
    Create Feedback Analyzer Agent.

    Parameters
    ----------
    llm : LLM
        CrewAI LLM instance.

    Returns
    -------
    Agent
        Configured CrewAI agent responsible for analyzing feedback patterns,
        identifying prediction mismatches, and recommending improvements.
    """
    agent = Agent(
        role="Feedback Analysis Specialist",
        goal = (
            "Analyze human feedback and rejection patterns to identify weaknesses "
            "in product quality prediction and recommend improvements to decision "
            "thresholds and evaluation logic."
            
        ),
        backstory=(
            "You are a quality intelligence analyst specializing in feedback-driven "
            "improvement systems. Your job is to study human review feedback, "
            "identify patterns in rejected assessments, detect prediction mismatches, "
            "and recommend adjustments to improve automated product quality decisions"
        ),
        llm=llm,

        tools=[analyze_rejection_patterns,
                detect_prediction_mismatches,
                recommend_threshold_adjustments,
                get_feedback_summary],

        verbose=False
    )
    return agent
