"""
Feedback Analysis Tool - Tool for agents to analyze feedback patterns.

Provides feedback analysis capabilities to the feedback analyzer agent.
"""

from crewai.tools import tool

# TODO: Implement four feedback analysis tools as CrewAI tools
# Purpose: Provide agent-accessible functions for feedback pattern analysis, mismatch detection,
# threshold recommendations, and feedback summarization to support Phase 4 feedback analysis
# Functions needed: analyze_rejection_patterns(), detect_prediction_mismatches(),
# recommend_threshold_adjustments(), get_feedback_summary() with @tool decorators
# Returns: Each tool returns Dict with analysis results for agent consumption


import os
from pathlib import Path
import json
from config.constants import GRADE_THRESHOLDS

def _feedback_dir() -> Path:
    env = os.environ.get("QUALITYGUARD_FEEDBACK_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "data" / "feedback"


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_decision(data: dict) -> str:
    decision = str(data.get("decision", "")).strip().upper()
    if decision in {"APPROVED", "REJECTED"}:
        return decision

    status = str(data.get("status", "")).strip().upper()
    if status == "APPROVED":
        return "APPROVED"
    if status in {"REJECTED", "NEEDS_REVIEW"}:
        return "REJECTED"
    return ""


def _predicted_decision(record: dict):
    """
    Convert model outputs into an approval/rejection signal.
    Uses GOOD thresholds as the practical acceptance bar.
    """
    defect = _to_float(record.get("defect_probability"))
    ret = _to_float(record.get("return_rate"))
    defect_limit = GRADE_THRESHOLDS["GOOD"]["defect_prob"]   # 15
    return_limit = GRADE_THRESHOLDS["GOOD"]["return_rate"]   # 25

    if defect is None and ret is None:
        return None, "Missing both defect_probability and return_rate."

    if defect is not None and defect >= defect_limit:
        return "REJECTED", f"Defect {defect:.2f}% >= {defect_limit}%."
    if ret is not None and ret >= return_limit:
        return "REJECTED", f"Return {ret:.2f}% >= {return_limit}%."
    return "APPROVED", "Both defect and return are below GOOD thresholds."


# ---------------------------------------
# CORE DATA FUNCTION
# ---------------------------------------
def get_feedback_summary_data():
    """Load and summarize feedback data."""
    feedback_dir = _feedback_dir()
    total_feedback = 0
    rejections = 0
    approvals = 0
    records = []

    if feedback_dir.exists():
        for file in feedback_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)

                decision = _normalize_decision(data)
                if not decision:
                    continue

                total_feedback += 1

                if decision == "REJECTED":
                    rejections += 1
                else:
                    approvals += 1

                records.append({
                    "assessment_id": data.get("assessment_id"),
                    "product_name": data.get("product_name", "Unknown"),
                    "decision": decision,
                    "defect_probability": _to_float(data.get("defect_probability")),
                    "return_rate": _to_float(data.get("return_rate")),
                    "final_quality_grade": data.get("final_quality_grade"),
                    "feedback": data.get("feedback", ""),
                    "timestamp": data.get("timestamp"),
                })

            except Exception:
                continue

    rejection_rate = (rejections / total_feedback) if total_feedback else 0

    return {
        "total_feedback": total_feedback,
        "rejections": rejections,
        "approvals": approvals,
        "rejection_rate": rejection_rate,
        "feedback_records": records,
    }


# ---------------------------------------
# SUPPORT FUNCTION 
# ---------------------------------------
def get_threshold_adjustments_data():
    """Return placeholder threshold adjustment data."""
    return {
        "status": "completed",
        "total_recommendations": 0,
        "recommendations": []
    }


# ---------------------------------------
# TOOL 1
# ---------------------------------------
@tool("Analyze Rejection Patterns")
def analyze_rejection_patterns(dummy: str = "") -> dict:
    """Summarize rejection trends."""
    summary = get_feedback_summary_data()

    return {
        "status": "completed",
        "total_feedback": summary["total_feedback"],
        "rejection_rate": summary["rejection_rate"]
    }


# ---------------------------------------
# TOOL 2
# ---------------------------------------
@tool("Detect Prediction Mismatches")
def detect_prediction_mismatches(dummy: str = "") -> dict:
    """Return mismatch analysis."""
    summary = get_feedback_summary_data()
    mismatches = []
    for rec in summary.get("feedback_records", []):
        predicted, reason = _predicted_decision(rec)
        human = rec.get("decision", "")
        if predicted is None:
            continue
        if predicted != human:
            mismatches.append({
                "assessment_id": rec.get("assessment_id"),
                "product_name": rec.get("product_name"),
                "human_decision": human,
                "predicted_decision": predicted,
                "defect_probability": rec.get("defect_probability"),
                "return_rate": rec.get("return_rate"),
                "reason": reason,
            })

    return {
        "status": "completed",
        "total_feedback": summary.get("total_feedback", 0),
        "mismatch_count": len(mismatches),
        "total_mismatches": len(mismatches),  # backward-compatible key
        "mismatches": mismatches,
    }


# ---------------------------------------
# TOOL 3
# ---------------------------------------
@tool("Recommend Threshold Adjustments")
def recommend_threshold_adjustments(dummy: str = "") -> dict:
    """Suggest threshold changes."""
    return {
        "status": "completed",
        "total_recommendations": 0,
        "recommendations": []
    }


# ---------------------------------------
# TOOL 4
# ---------------------------------------
@tool("Get Feedback Summary")
def get_feedback_summary(dummy: str = "") -> dict:
    """Return feedback summary stats."""
    return get_feedback_summary_data()
