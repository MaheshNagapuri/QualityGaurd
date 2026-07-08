"""
Feedback Analysis Task - Processes and analyzes human feedback patterns.

Phase 4 - Sequential execution (runs after all assessments complete, triggered only if feedback exists).
"""

from crewai import Task

# TODO: Implement create_feedback_analysis_task() function
# Purpose: Create Phase 4 optional task for analyzing human feedback patterns and agent performance
# Parameters: agent (Agent instance), feedback_summary (dict with feedback records and rejection data)
# Returns: Task instance with expected output: analysis_status, key_findings, agent_performance, threshold_adjustments, mismatch_count, recommendations, next_actions
def create_feedback_analysis_task(agent, feedback_summary):
    """
    Create feedback analysis task.

    Parameters
    ----------
    agent: Agent
        Feedback analyzer agent instance.
    feedback_summary: dict
        Aggregated feedback data including rejection patterns and decisions.
    Returns
    -------
    Task 
        Configured CrewAI Task for analyzing feedback patterns and recommending improvements.
    """

    description= f"""
    Analyze human feedback from previous product assessments.

    Feedback Summary Data:
    {feedback_summary}

    Your objective is to analyze feedback patterns and determine whether 
    there are weaknesses in the automated quality assessment system.

    Focus on:

    - Patterns in rejected assessments
    - Potential mismatches between predictions and human decisions
    - Agent performance trends 
    - Threshold adjustment recommendations
    - Opportunities to improve decision-making logic

    Required Output JSON:
    {{
        "analysis_status": str,
        "key_findings":list,
        "agent_performance": dict,
        "threshold_adjustments": dict,
        "mismatch_count":int,
        "recommendataions":list,
        "next_actions":list
    }}
    """
    task=Task(
        description=description,
        agent=agent,
        expected_output="JSON containing analysis_status, key_findings, agent_performance, threshold_adjustments, mismatch_count,recommendations, and next_actions."
    )
    return task
