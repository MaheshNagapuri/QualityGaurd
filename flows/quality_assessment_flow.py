
"""
Quality assessment flow orchestrator.

Coordinates 6 agents in hybrid sequential-parallel execution:
- Phase 1: Product Analyzer > Quality Assessor (sequential)
- Phase 2: Supply Chain, Cost Impact, Market Trend agents (parallel)
- Phase 3: Recommendation agent (sequential, waits for Phase 2)
- Phase 4: Feedback Analyzer (user-triggered, separate)
"""


import re
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from crewai import LLM, Crew, Process

logger = logging.getLogger(__name__)

from agents.product_analyzer_agent  import create_product_analyzer_agent
from agents.quality_assessor_agent  import create_quality_assessor_agent
from agents.supply_chain_agent      import create_supply_chain_agent
from agents.cost_impact_agent       import create_cost_impact_agent
from agents.market_trend_agent      import create_market_trend_agent
from agents.recommendation_agent    import create_recommendation_agent
from agents.feedback_analyzer_agent import create_feedback_analyzer_agent

from tasks.product_analysis_task    import create_product_analysis_task
from tasks.quality_assessment_task  import create_quality_assessment_task
from tasks.supply_chain_task        import create_supply_chain_task
from tasks.cost_impact_task         import create_cost_impact_task
from tasks.market_trend_task        import create_market_trend_task
from tasks.recommendation_task      import create_recommendation_task
from tasks.feedback_analysis_task   import create_feedback_analysis_task

from tools.feedback_analysis_tool     import get_feedback_summary_data
from tools.defect_classifier_tool     import predict_defect_probability
from tools.return_rate_predictor_tool import predict_return_rate
from utils.json_extractor             import extract_json_from_output, get_value
from config.constants                 import SUPPLIER_DATA, GRADE_THRESHOLDS,FEEDBACK_KEYWORDS


# ─────────────────────────────────────────────────────────────────────────────
# Module-level fallback LLM (set when Groq fails mid-run)
# ─────────────────────────────────────────────────────────────────────────────
_fallback_llm = None


# Create or reuse a cached Gemini fallback LLM, with optional key rotation on demand.
def _get_fallback_llm(force_rotate: bool = False):
    """
    Get or create Gemini fallback LLM.
    - First call: creates and caches LLM using first working Gemini key
    - force_rotate=True: discards cache and tries next Gemini key
    """
    global _fallback_llm
    if _fallback_llm is not None and not force_rotate:
        return _fallback_llm
    try:
        from utils.gemini_client import _try_gemini_fallback
        _fallback_llm = _try_gemini_fallback()
        logger.info("✅ Gemini fallback LLM created successfully")
        return _fallback_llm
    except Exception as e:
        logger.error(f"❌ Gemini fallback LLM creation failed: {e}")
        _fallback_llm = None
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Module-level helpers
# ─────────────────────────────────────────────────────────────────────────────

# Parse a percentage-like value from numeric, dict, JSON, or free-form text with a default fallback.
def _parse_percent(text, default, key=None):
    if text is None:
        return default

    if isinstance(text, (int, float)):
        return float(text)

    if isinstance(text, dict) and key in text:
        try:
            return float(text[key])
        except (TypeError, ValueError):
            pass

    parsed = extract_json_from_output(text)
    if isinstance(parsed, dict):
        if key and key in parsed:
            try:
                return float(parsed[key])
            except (TypeError, ValueError):
                pass
        for fallback_key in ("defect_probability", "return_rate"):
            if fallback_key in parsed:
                try:
                    return float(parsed[fallback_key])
                except (TypeError, ValueError):
                    continue

    m = re.search(r"(-?\d+(?:\.\d+)?)", str(text))
    return float(m.group(1)) if m else default


# Map defect and return rates to EXCELLENT/GOOD/ACCEPTABLE/POOR using configured thresholds.
def _determine_grade(defect, ret):
    t = GRADE_THRESHOLDS
    if defect < t["EXCELLENT"]["defect_prob"] and ret < t["EXCELLENT"]["return_rate"]: return "EXCELLENT"
    if defect < t["GOOD"]["defect_prob"]      and ret < t["GOOD"]["return_rate"]:      return "GOOD"
    if defect < t["ACCEPTABLE"]["defect_prob"]and ret < t["ACCEPTABLE"]["return_rate"]:return "ACCEPTABLE"
    return "POOR"


# Compute a coarse risk band from the average of defect and return percentages.
def _risk_level(defect, ret):
    c = (defect + ret) / 2
    if c > 15: return "CRITICAL"
    if c > 10: return "HIGH"
    if c > 5:  return "MEDIUM"
    return "LOW"


# Identify fatal auth errors that should trigger immediate fallback provider switching.
def _is_fatal_error(err: str) -> bool:
    """Returns True if error means API key is invalid — should switch LLM immediately."""
    return any(k in err for k in [
        "invalid_api_key", "invalid api key", "unauthorized",
        "401", "403", "authentication", "permission denied", "access denied"
    ])


# Identify rate-limit and quota errors that should be retried with backoff.
def _is_rate_limit_error(err: str) -> bool:
    """Returns True if error means quota/rate limit hit."""
    return any(k in err for k in [
        "429", "rate limit", "quota", "resource exhausted", "too many"
    ])


# Execute a callable with retry logic, rate-limit backoff, and automatic Gemini fallback on fatal errors.
def _run_with_retry(fn, max_retries=3, base_wait=15):
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            err = str(e).lower()

            if _is_fatal_error(err):
                # ── Invalid key → switch to Gemini immediately ──
                logger.warning(
                    f"⚠️ Fatal API error on attempt {attempt + 1}: {e}\n"
                    f"→ Switching to Gemini fallback LLM..."
                )
                fallback = _get_fallback_llm()
                if fallback is None:
                    logger.error("❌ No Gemini fallback available — giving up")
                    return None
                # Retry once with fallback now set in module global
                try:
                    return fn()
                except Exception as retry_e:
                    logger.error(f"❌ Gemini fallback also failed: {retry_e}")
                    return None

            elif _is_rate_limit_error(err):
                if attempt < max_retries - 1:
                    wait = base_wait * (2 ** attempt)  # 15s → 30s → 60s
                    logger.warning(
                        f"⚠️ Rate limit (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {wait}s..."
                    )
                    # ── If already on Gemini fallback, rotate to next key ──
                    if _fallback_llm is not None:
                        logger.warning("Already on Gemini fallback — rotating to next Gemini key...")
                        _get_fallback_llm(force_rotate=True)

                    time.sleep(wait)
                else:
                    logger.error(f"Agent failed after {attempt + 1} attempt(s): {e}")
                    return None

            else:
                logger.error(f"Agent failed after {attempt + 1} attempt(s): {e}")
                return None

    return None


# Derive key findings from feedback totals, rejection rate, and rejection comment themes.
def _compute_findings(summary: dict) -> list:
    """Build key findings from raw feedback data — no agent needed, never returns None."""
    total      = summary.get("total_feedback", 0)
    rejections = summary.get("rejections", 0)
    approvals  = summary.get("approvals", 0)
    rej_rate   = summary.get("rejection_rate", 0.0)
    records    = summary.get("feedback_records", [])

    findings = []

    findings.append(
        f"Reviewed {total} assessment(s): {approvals} approved, "
        f"{rejections} rejected ({rej_rate:.0%} rejection rate)."
    )

    if rej_rate > 0.5:
        findings.append(
            f"High rejection rate of {rej_rate:.0%} — AI thresholds may be "
            f"too lenient and need tightening."
        )
    elif rej_rate > 0.2:
        findings.append(
            f"Moderate rejection rate of {rej_rate:.0%} — some misalignment "
            f"between AI predictions and human decisions."
        )
    elif rejections == 0:
        findings.append(
            "All assessments approved — AI predictions align well with human decisions."
        )
    else:
        findings.append(
            f"Low rejection rate of {rej_rate:.0%} — system is performing well."
        )

    rej_comments = [
        r.get("feedback", "") or ""
        for r in records
        if str(r.get("decision", "")).upper() in ("REJECTED", "NEEDS_REVIEW")
    ]
    all_text = " ".join(rej_comments).lower()

    if "defect" in all_text or "fault" in all_text:
        findings.append("Rejection comments mention defects — defect probability threshold may need tightening.")
    elif "supply" in all_text or "supplier" in all_text:
        findings.append("Rejection comments mention supply chain — supplier scoring may need review.")
    elif "cost" in all_text or "financial" in all_text:
        findings.append("Rejection comments reference financial impact — cost thresholds may need adjustment.")
    elif rej_comments:
        findings.append(f"Analysed {len(rej_comments)} rejection comment(s) — no dominant issue pattern detected.")
    else:
        findings.append("No written rejection comments recorded.")

    return findings


# Build practical next-step recommendations from rejection trends and feedback text signals.
def _compute_recommendations(summary: dict) -> list:
    """Build recommendations from raw feedback data — never returns empty."""
    rej_rate = summary.get("rejection_rate", 0.0)
    total    = summary.get("total_feedback", 0)
    records  = summary.get("feedback_records", [])
    all_text = " ".join(r.get("feedback", "") or "" for r in records).lower()

    recs = []
    if rej_rate > 0.5:
        recs.append("Tighten defect probability and return rate thresholds — current settings are too permissive.")
        recs.append("Retrain ML models with recent feedback data to improve prediction accuracy.")
    elif rej_rate > 0.2:
        recs.append("Review ACCEPTABLE grade products — consider stricter criteria for borderline cases.")
        recs.append("Collect more reviewer feedback with written comments to identify rejection patterns.")
    else:
        recs.append("System is performing well — continue monitoring rejection rate monthly.")
        recs.append("Consider testing more edge-case products for robust ML model coverage.")

    if "supply" in all_text:
        recs.append("Update supplier data — reviewer concerns suggest supply chain scoring may be outdated.")
    if total < 5:
        recs.append("Collect at least 10 assessments before drawing conclusions from feedback analysis.")

    return recs


# Estimate per-agent performance by counting keyword mentions in reviewer feedback text.
def _compute_agent_performance(summary: dict) -> dict:
    """Compute agent performance scores from feedback comment text."""
    records = summary.get("feedback_records", [])
    total   = max(summary.get("total_feedback", 1), 1)

    keyword_map = FEEDBACK_KEYWORDS
    mention_counts = {agent: 0 for agent in keyword_map}
    for r in records:
        text = (r.get("feedback", "") or "").lower()
        if not text:
            continue
        for agent, keywords in keyword_map.items():
            if any(k in text for k in keywords):
                mention_counts[agent] += 1

    performance = {}
    for agent, count in mention_counts.items():
        score = max(0.50, 0.85 - (count / total) * 0.35)
        performance[agent] = round(score, 2)

    return performance


# Recommend defect and return threshold adjustments based on rejection patterns and comments.
def _compute_threshold_adjustments(summary: dict) -> dict:
    """Compute threshold adjustment recommendations from feedback data."""
    records    = summary.get("feedback_records", [])
    rej_rate   = summary.get("rejection_rate", 0.0)
    rejections = summary.get("rejections", 0)
    adjustments = {}

    rej_comments = [
        r.get("feedback", "") or ""
        for r in records
        if str(r.get("decision", "")).upper() in ("REJECTED", "NEEDS_REVIEW")
    ]
    all_text = " ".join(rej_comments).lower()

    if rej_rate > 0.3 or "defect" in all_text or "fault" in all_text:
        current_defect     = 15
        recommended_defect = max(5, int(current_defect * (1 - rej_rate * 0.3)))
        adjustments["defect_probability"] = {
            "current":     current_defect,
            "recommended": recommended_defect,
            "reason":      f"Rejection rate of {rej_rate:.0%} suggests defect threshold is too permissive.",
        }
    else:
        adjustments["defect_probability"] = {
            "current":     15,
            "recommended": 15,
            "reason":      "Current threshold appears appropriate based on feedback patterns.",
        }

    if rej_rate > 0.3 or "return" in all_text or "quality" in all_text:
        current_return     = 25
        recommended_return = max(10, int(current_return * (1 - rej_rate * 0.25)))
        adjustments["return_rate"] = {
            "current":     current_return,
            "recommended": recommended_return,
            "reason":      f"{rejections} rejection(s) suggest return rate threshold needs tightening.",
        }
    else:
        adjustments["return_rate"] = {
            "current":     25,
            "recommended": 25,
            "reason":      "Current threshold appears appropriate based on feedback patterns.",
        }

    return adjustments


# Normalize feedback-agent output and fill missing fields with deterministic computed fallbacks.
def _sanitize_feedback_result(parsed: dict, summary: dict) -> dict:
    """Sanitize agent output — replace any None/null fields with computed fallbacks."""
    findings = parsed.get("key_findings")
    if not findings or not isinstance(findings, list):
        findings = []
    findings = [str(f) for f in findings
                if f is not None and str(f).strip() not in ("", "None", "null")]
    if not findings:
        findings = _compute_findings(summary)

    perf = parsed.get("agent_performance")
    if not perf or not isinstance(perf, dict):
        perf = {}
    else:
        perf = {k: float(v) for k, v in perf.items() if v is not None}
    if not perf:
        perf = _compute_agent_performance(summary)

    adj = parsed.get("threshold_adjustments")
    if not adj or not isinstance(adj, dict):
        adj = {}
    if not adj:
        adj = _compute_threshold_adjustments(summary)

    mismatch = parsed.get("mismatch_count")
    if mismatch is None:
        mismatch = parsed.get("total_mismatches")
    if mismatch is None and isinstance(parsed.get("mismatches"), list):
        mismatch = len(parsed.get("mismatches"))
    try:
        mismatch = int(mismatch) if mismatch is not None else 0
    except (ValueError, TypeError):
        mismatch = 0

    recs = parsed.get("recommendations")
    if not recs or not isinstance(recs, list):
        recs = []
    recs = [str(r) for r in recs
            if r is not None and str(r).strip() not in ("", "None", "null")]
    if not recs:
        recs = _compute_recommendations(summary)

    actions = parsed.get("next_actions")
    if not actions or not isinstance(actions, list):
        actions = []
    actions = [str(a) for a in actions
               if a is not None and str(a).strip() not in ("", "None", "null")]
    if not actions:
        actions = [
            "Review and adjust quality thresholds based on findings.",
            "Re-run analysis after collecting more feedback.",
        ]

    return {
        "analysis_status":       parsed.get("analysis_status") or "completed",
        "key_findings":          findings,
        "agent_performance":     perf,
        "threshold_adjustments": adj,
        "mismatch_count":        mismatch,
        "recommendations":       recs,
        "next_actions":          actions,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main flow class
# ─────────────────────────────────────────────────────────────────────────────

class QualityAssessmentFlow:

    # Initialize runtime state for product context, phase outputs, and fallback caches.
    def __init__(self, llm: LLM):
        self.llm          = llm
        self.product_data = {}
        self._defect_raw  = None
        self._quality_raw = None
        self._supply_raw  = None
        self._cost_raw    = None
        self._market_raw  = None
        self._rec_raw     = None
        self._defect_fallback_cache = None
        self._return_fallback_cache = None

    # Return the currently active LLM, preferring module-level fallback when available.
    def _get_active_llm(self) -> LLM:
        """
        Returns the best available LLM:
        - If Groq failed mid-run → returns Gemini fallback
        - Otherwise → returns original Groq LLM
        """
        return _fallback_llm if _fallback_llm is not None else self.llm

    # Run all assessment phases for one product and return the finalized result payload.
    def kickoff(self, product_data: dict) -> dict:
        self.product_data = product_data
        self._run_phases()
        return self.finalize_assessment()

    # Orchestrate phase execution: sequential core analysis, parallel domain analysis, then recommendation.
    def _run_phases(self):
        # Phase 1 — Sequential
        logger.info("Phase 1 [Sequential]: Product Analyzer...")
        self._defect_raw = _run_with_retry(
            lambda: self._run_crew(create_product_analyzer_agent, create_product_analysis_task)
        )

        logger.info("Phase 1 [Sequential]: Quality Assessor...")
        self._quality_raw = _run_with_retry(
            lambda: self._run_crew(create_quality_assessor_agent, create_quality_assessment_task)
        )

        # Phase 2 — Parallel
        logger.info("Phase 2 [Parallel]: Supply Chain | Cost Impact | Market Trend...")
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(
                    _run_with_retry,
                    lambda: self._run_crew(create_supply_chain_agent, create_supply_chain_task)
                ): "supply",
                executor.submit(
                    _run_with_retry,
                    lambda: self._analyze_cost_impact()
                ): "cost",
                executor.submit(
                    _run_with_retry,
                    lambda: self._run_crew(create_market_trend_agent, create_market_trend_task)
                ): "market",
            }
            for future in as_completed(futures):
                key = futures[future]
                try:
                    result = future.result()
                    if result is None:
                        logger.warning(f"Phase 2 [{key}] failed after retries — using fallback values")
                        continue
                    if key == "supply":
                        self._supply_raw = result
                        logger.info("Phase 2: Supply Chain done ✓")
                    elif key == "cost":
                        self._cost_raw = result
                        logger.info("Phase 2: Cost Impact done ✓")
                    elif key == "market":
                        self._market_raw = result
                        logger.info("Phase 2: Market Trend done ✓")
                except Exception as e:
                    logger.error(f"Phase 2 [{key}] unexpected error: {e}")

        # Phase 3 — Sequential
        logger.info("Phase 3 [Sequential]: Recommendation Agent...")
        self._rec_raw = _run_with_retry(lambda: self._run_recommendation())

    # Create and execute a single-agent Crew task using the active LLM and current product data.
    def _run_crew(self, agent_fn, task_fn):
        """Run a single agent crew — always uses best available LLM."""
        llm   = self._get_active_llm()
        agent = agent_fn(llm)
        task  = task_fn(agent, self.product_data)
        crew  = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        return crew.kickoff()

    # Run the cost-impact phase using parsed defect and return predictions from phase 1 outputs.
    def _analyze_cost_impact(self):
        if self._defect_raw is None or self._quality_raw is None:
            logger.warning("Using default values for cost impact — Phase 1 outputs missing")
        defect_prob = _parse_percent(self._defect_raw, 10.0)
        return_rate = _parse_percent(self._quality_raw, 15.0)
        llm   = self._get_active_llm()
        agent = create_cost_impact_agent(llm)
        task  = create_cost_impact_task(agent, self.product_data, defect_prob, return_rate)
        crew  = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        return crew.kickoff()

    # Aggregate prior phase outputs and run the recommendation agent for final decision synthesis.
    def _run_recommendation(self):
        defect_prob = _parse_percent(self._defect_raw, 10.0)
        return_rate = _parse_percent(self._quality_raw, 15.0)
        d = extract_json_from_output(self._supply_raw) or {}
        analysis = {
            "defect_probability":   defect_prob,
            "return_rate":          return_rate,
            "financial_impact":     str(get_value(extract_json_from_output(self._cost_raw) or {}, "total_financial_impact", "N/A")),
            "supplier_info":        get_value(d, "supply_chain_assessment", "N/A"),
            "supplier_reliability": get_value(d, "supplier_reliability", 4.0),
            "market_demand":        get_value(extract_json_from_output(self._market_raw) or {}, "market_demand", "N/A"),
            "competitive_position": get_value(extract_json_from_output(self._market_raw) or {}, "competitive_position", "N/A"),
        }
        llm   = self._get_active_llm()
        agent = create_recommendation_agent(llm)
        task  = create_recommendation_task(agent, self.product_data, analysis)
        crew  = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        return crew.kickoff()

    # Analyze saved human feedback with safe fallbacks for no-data, parse issues, and runtime failures.
    def analyze_feedback(self) -> dict:
        try:
            summary = get_feedback_summary_data()

            if summary["total_feedback"] == 0:
                return {
                    "analysis_status":       "no_data",
                    "key_findings":          ["No feedback data available yet."],
                    "agent_performance":     {},
                    "threshold_adjustments": {},
                    "mismatch_count":        0,
                    "recommendations":       ["Collect more feedback first."],
                    "next_actions":          ["Approve or reject pending assessments."],
                }

            computed_findings = _compute_findings(summary)
            computed_recs     = _compute_recommendations(summary)

            llm    = self._get_active_llm()
            agent  = create_feedback_analyzer_agent(llm)
            task   = create_feedback_analysis_task(agent, summary)
            crew   = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
            result = crew.kickoff()
            parsed = extract_json_from_output(result) or {}

            sanitized = _sanitize_feedback_result(parsed, summary)

            if not sanitized["key_findings"]:
                sanitized["key_findings"] = computed_findings
            if not sanitized["recommendations"]:
                sanitized["recommendations"] = computed_recs
            if not sanitized["agent_performance"]:
                sanitized["agent_performance"] = _compute_agent_performance(summary)
            if not sanitized["threshold_adjustments"]:
                sanitized["threshold_adjustments"] = _compute_threshold_adjustments(summary)

            return sanitized

        except Exception as e:
            logger.error(f"Feedback analysis error: {e}")
            try:
                summary = get_feedback_summary_data()
                return {
                    "analysis_status":       "completed",
                    "key_findings":          _compute_findings(summary),
                    "agent_performance":     {},
                    "threshold_adjustments": {},
                    "mismatch_count":        0,
                    "recommendations":       _compute_recommendations(summary),
                    "next_actions":          ["Check logs for error details.", "Re-run analysis."],
                }
            except Exception:
                return {
                    "analysis_status":       "error",
                    "key_findings":          [f"Analysis failed: {str(e)}"],
                    "agent_performance":     {},
                    "threshold_adjustments": {},
                    "mismatch_count":        0,
                    "recommendations":       [],
                    "next_actions":          [],
                }

    # Merge all raw phase outputs into the final structured assessment response with computed defaults.
    def finalize_assessment(self) -> dict:
        defect_prob   = _parse_percent(self._defect_raw,  10.0)
        return_rate   = _parse_percent(self._quality_raw, 15.0)
        quality_score = round(max(0, min(100, 100 - (defect_prob + return_rate) / 2)), 1)
        grade         = _determine_grade(defect_prob, return_rate)

        defect_d   = extract_json_from_output(self._defect_raw) or {}
        agent_risk = defect_d.get("risk_level")
        risk       = agent_risk if agent_risk in ("LOW", "MEDIUM", "HIGH", "CRITICAL") else _risk_level(defect_prob, return_rate)

        supply_d = extract_json_from_output(self._supply_raw) or {}
        cost_d   = extract_json_from_output(self._cost_raw)   or {}
        market_d = extract_json_from_output(self._market_raw) or {}
        rec_d    = extract_json_from_output(self._rec_raw)    or {}

        country  = self.product_data.get("product_manufacturing_country", "USA").upper()
        sup_info = SUPPLIER_DATA.get(country, SUPPLIER_DATA["USA"])

        product_name = (
            self.product_data.get("name") or
            self.product_data.get("product_name") or
            "Unknown Product"
        )

        price      = self.product_data.get("product_price_usd", 100)
        inventory  = self.product_data.get("inventory", 1000)
        def_units  = round(inventory * defect_prob / 100)
        ret_units  = round(inventory * return_rate / 100)
        fin_impact = round(def_units * price * 0.5 + ret_units * price * 0.3, 2)

        return {
            "product_name": product_name,
            "timestamp":    datetime.utcnow().isoformat(),
            "status":       "PENDING_REVIEW",

            "defect_analysis": {
                "defect_probability": defect_prob,
                "risk_level":         risk,
                "analysis_summary":   get_value(
                    defect_d,
                    "analysis_summary",
                    f"ML prediction: {defect_prob:.1f}% defect probability."
                ),
            },
            "quality_assessment": {
                "return_rate":        return_rate,
                "quality_score":      quality_score,
                "assessment_summary": get_value(
                    extract_json_from_output(self._quality_raw) or {},
                    "assessment_summary",
                    f"Predicted return rate: {return_rate:.1f}%."
                ),
            },
            "supply_chain_analysis": {
                "supplier_country":        country,
                "supplier_reliability":    get_value(supply_d, "supplier_reliability",    sup_info["reliability_score"]),
                "lead_time_days":          get_value(supply_d, "lead_time_days",           sup_info["lead_time_days"]),
                "certifications":          get_value(supply_d, "certifications",           sup_info["certifications"]),
                "supply_chain_assessment": get_value(
                    supply_d, "supply_chain_assessment",
                    f"Sourced from {country}. Reliability {sup_info['reliability_score']}/5."
                ),
            },
            "cost_impact_analysis": {
                "estimated_defective_units": get_value(cost_d, "estimated_defective_units", def_units),
                "estimated_returned_units":  get_value(cost_d, "estimated_returned_units",  ret_units),
                "total_financial_impact":    get_value(cost_d, "total_financial_impact",     fin_impact),
                "risk_level":                get_value(cost_d, "risk_level",                 risk),
                "cost_breakdown": (
                    get_value(cost_d, "cost_breakdown") or
                    f"Direct Loss: ${def_units*price*0.5:,.2f} | "
                    f"Return Loss: ${ret_units*price*0.3:,.2f} | "
                    f"Total: ${fin_impact:,.2f}"
                ),
            },
            "market_trend_analysis": {
                "market_demand":        get_value(market_d, "market_demand",        "N/A"),
                "competitive_position": get_value(market_d, "competitive_position", "N/A"),
                "trend_analysis":       get_value(market_d, "trend_analysis",       "Market analysis completed."),
            },
            "recommendation": {
                "overall_assessment":  get_value(rec_d, "overall_assessment",  f"Grade: {grade}. Score: {quality_score}/100."),
                "recommendations":     get_value(rec_d, "recommendations",     ["Review quality control", "Monitor supplier performance"]),
                "approval_status":     get_value(rec_d, "approval_status",     "PENDING_REVIEW"),
                "final_quality_grade": get_value(rec_d, "final_quality_grade", grade),
            },
            "_raw_defect":  str(self._defect_raw  or ""),
            "_raw_quality": str(self._quality_raw or ""),
            "_raw_supply":  str(self._supply_raw  or ""),
            "_raw_cost":    str(self._cost_raw    or ""),
            "_raw_market":  str(self._market_raw  or ""),
            "_raw_rec":     str(self._rec_raw     or ""),
        }
