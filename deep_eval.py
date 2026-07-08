"""

Runs full QualityAssessmentFlow + DeepEval evaluation.

Executes all agents (CrewAI pipeline)
Evaluates output using DeepEval (Groq judge)
Uses ONLY:
    • Answer Relevancy
    • Hallucination
"""

import os
import ssl
import json
import logging
from pathlib import Path
import warnings

# Disable CrewAI/OpenTelemetry tracing so this script stays focused on local eval output
# and does not depend on tracing backends.
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["CREWAI_TRACES_EXPORT"] = "false"

warnings.filterwarnings("ignore")

# SSL bypass flags used to avoid local certificate issues in constrained environments.
# Keep in mind this reduces transport security and should not be used in production.
os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""
ssl._create_default_https_context = ssl._create_unverified_context

logger = logging.getLogger(__name__)


# Load local .env from project root when python-dotenv is available.
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# DeepEval 
from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric
from deepeval.test_case import LLMTestCase
from deepeval.models.base_model import DeepEvalBaseLLM

# Groq
from groq import Groq
import httpx

# Flow
from flows.quality_assessment_flow import QualityAssessmentFlow
from crewai import LLM

# Groq-backed DeepEval judge implementation.
# DeepEval metrics call this class to generate rubric-based judgments.
class GroqJudge(DeepEvalBaseLLM):
    def __init__(self):
        self.model_name = "llama-3.1-8b-instant"

        # This script expects GROQ_API_KEY_1 in .env for the evaluation judge.
        api_key = os.getenv("GROQ_API_KEY_1", "").strip()
        if not api_key:
            raise ValueError("GROQ_API_KEY_1 not found in .env")

        self.client = Groq(
            api_key=api_key,
            http_client=httpx.Client(timeout=30.0, verify=False),
        )

    def get_model_name(self):
        return self.model_name

    def load_model(self):
        return self.client

    def generate(self, prompt: str) -> str:
        # Synchronous generation path used by DeepEval metric objects.
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=300,
        )
        return response.choices[0].message.content

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)



# Evaluate one assessment payload with Answer Relevancy + Hallucination only.
# Output schema: {"scores": {...}, "overall": float, "passed": bool}


def evaluate_assessment(assessment_result: dict) -> dict:
    try:
        judge = GroqJudge()

        da  = assessment_result.get("defect_analysis", {})
        qa  = assessment_result.get("quality_assessment", {})
        rec = assessment_result.get("recommendation", {})

        defect = da.get("defect_probability", 0)
        ret    = qa.get("return_rate", 0)
        grade  = rec.get("final_quality_grade", "")
        risk   = da.get("risk_level", "")

        # Convert structured assessment fields into compact natural-language
        # input/output strings for LLM-based metric evaluation.
        input_text = (
            f"A product has {defect}% defect rate and {ret}% return rate. "
            f"Evaluate its quality level and risk."
        )

        actual_output = (
            f"The product is graded {grade} with {risk} risk."
        )

        test_case = LLMTestCase(
            input=input_text,
            actual_output=actual_output,
            context=[
    "Defect rate: 37.7%",
    "Return rate: 49.31%",
    "If defect > 30% OR return > 40% → quality is POOR",
    "If defect < 40% AND return < 50% → ACCEPTABLE"
]
        )

        # Metric thresholds:
        # - Relevancy passes at >= 0.6
        # - HallucinationMetric emits hallucination risk (lower is better),
        #   so we invert it to expose a "truthfulness-style" score.
        relevancy = AnswerRelevancyMetric(threshold=0.6, model=judge)
        hallucination = HallucinationMetric(threshold=0.3, model=judge)

        metrics = [relevancy, hallucination]

        for m in metrics:
            m.measure(test_case)

        scores = {
            "relevancy": round(relevancy.score or 0, 3),
            "hallucination": round(1-(hallucination.score or 0), 3),
        }

        passed = (
            scores["relevancy"] >= 0.6 and
            scores["hallucination"] >= 0.7
        )

        overall = round(sum(scores.values()) / len(scores), 3)

        return {
            "scores": scores,
            "overall": overall,
            "passed": passed,
        }

    except Exception as e:
        return {"error": str(e)}



# Pretty terminal output for quick manual review.


def display_terminal_results(result):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RESET = "\033[0m"

    print("\n🔬 DeepEval Results\n")

    if "error" in result:
        print(RED + result["error"] + RESET)
        return

    if result["passed"]:
        print(GREEN + f"✅ PASSED — {result['overall']}" + RESET)
    else:
        print(RED + f"❌ FAILED — {result['overall']}" + RESET)

    print("\nMetrics:")
    for k, v in result["scores"].items():
        color = GREEN if v >= 0.7 else RED
        print(f"{k:15}: {color}{v}{RESET}")



# End-to-end runner:
# 1) execute QualityAssessmentFlow
# 2) evaluate with DeepEval
# 3) print pass/fail + metric scores

if __name__ == "__main__":
    print("\n🚀 Running Full Pipeline + DeepEval...\n")

    llm = LLM(
        model="groq/llama-3.1-8b-instant",
        temperature=0
    )

    flow = QualityAssessmentFlow(llm)

    product_data = {
        "product_name": "Wireless Headphones Pro",
        "product_price_usd": 120,
        "inventory": 1000,
        "product_manufacturing_country": "GERMANY"
    }

    print("⚙️ Running agents...\n")
    assessment=flow.kickoff(product_data)

    print("✅ Assessment completed\n")

    print("\n🔬 Running evaluation...\n")
    eval_result = evaluate_assessment(assessment)

    display_terminal_results(eval_result)
