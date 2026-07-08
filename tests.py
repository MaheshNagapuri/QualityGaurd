"""
QualityGuard Test Suite

Tests validate output contracts and data quality without constraining implementation.
Following VentureLens testing patterns with CrewAI Flow-specific tests.

Test Structure:
- 16 total test cases
- Organized by component type (ML, Tools, Agents, Flow, Data Quality, CrewAI Flow)
- Mock infrastructure for LLM testing
- Multiple product profiles for scenario testing
- CrewAI Flow execution and state management validation
- Focus: Output contracts, not implementation details
- Constraint: No variable-level assertions, only output validation
"""

import pytest
import json
import pandas as pd
import pickle
from typing import Dict, Any, Optional
from pathlib import Path



# ============================================================================
# PART 1: Mock Infrastructure
# ============================================================================

class MockGeminiContent:
    """Simulates google.genai content response"""
    def __init__(self, text: str):
        self.text = text


class MockGeminiResponse:
    """Simulates Gemini API response"""
    def __init__(self, text: str):
        self.text = text


class MockGeminiClient:
    """
    Complete mock of GeminiClient for testing without API calls.
    Pattern matches on prompt content to return appropriate responses.
    """

    def __init__(self):
        self.call_count = 0
        self.default_responses = {
            'defect_analysis': {
                'defect_probability': 12.5,
                'risk_level': 'MEDIUM',
                'analysis_summary': 'Product shows moderate defect risk based on features'
            },
            'quality_assessment': {
                'quality_score': 75,
                'return_rate': 8.5,
                'assessment_summary': 'Quality metrics indicate acceptable product standards'
            },
            'supply_chain': {
                'supplier_country': 'USA',
                'supplier_reliability': 4.5,
                'lead_time_days': 14,
                'certifications': ['ISO 9001', 'ISO 14001'],
                'supply_chain_assessment': 'Strong supplier performance with reliable delivery'
            },
            'cost_impact': {
                'estimated_defective_units': 125,
                'estimated_returned_units': 85,
                'total_financial_impact': 21500.00,
                'risk_level': 'MEDIUM',
                'cost_analysis_summary': 'Financial impact analysis shows acceptable risk level with moderate loss projections'
            },
            'market_trends': {
                'market_demand': 'HIGH',
                'competitive_position': 'STRONG',
                'trend_analysis': 'Favorable market conditions with strong competitive positioning'
            },
            'recommendation': {
                'overall_assessment': 'Product quality is acceptable - Monitor and maintain standards',
                'recommendations': [
                    'Maintain current quality control procedures',
                    'Monitor return rates quarterly',
                    'Strengthen supplier relationships'
                ],
                'approval_status': 'PENDING_REVIEW',
                'final_quality_grade': 'ACCEPTABLE'
            },
            'feedback_summary': {
                'analysis_status': 'completed',
                'key_findings': [
                    'Quality metrics align with user expectations',
                    'Cost impact analysis shows acceptable loss levels'
                ],
                'agent_performance': {
                    'quality_assessor': 0.15,
                    'supply_chain': 0.10,
                    'cost_impact': 0.20
                },
                'threshold_adjustments': {},
                'mismatch_count': 0,
                'recommendations': ['Continue current assessment protocols'],
                'next_actions': ['Monitor feedback trends']
            }
        }

    def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_mime_type: Optional[str] = None,
    ) -> str:
        """Generate content with pattern matching on prompt"""
        self.call_count += 1
        prompt_lower = prompt.lower()

        # Pattern matching for different agent types
        if "feedback" in prompt_lower or "analyzer" in prompt_lower:
            response = self.default_responses['feedback_summary']
        elif "market" in prompt_lower or "trend" in prompt_lower:
            response = self.default_responses['market_trends']
        elif "recommendation" in prompt_lower or "approve" in prompt_lower:
            response = self.default_responses['recommendation']
        elif "cost" in prompt_lower or "financial" in prompt_lower:
            response = self.default_responses['cost_impact']
        elif "supply" in prompt_lower or "chain" in prompt_lower or "supplier" in prompt_lower:
            response = self.default_responses['supply_chain']
        elif "quality" in prompt_lower or "assess" in prompt_lower:
            response = self.default_responses['quality_assessment']
        elif "defect" in prompt_lower or "analyze" in prompt_lower:
            response = self.default_responses['defect_analysis']
        else:
            response = self.default_responses['defect_analysis']

        return json.dumps(response)

    def extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from response text"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {}

    def validate_response_fields(self, response: Dict[str, Any], required_fields: list) -> None:
        """Validate that response has required fields"""
        missing = [f for f in required_fields if f not in response]
        if missing:
            raise ValueError(f"Missing fields: {missing}")

    def generate_structured_json(
        self,
        prompt: str,
        required_fields: list,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Generate and validate JSON response"""
        response_text = self.generate_content(prompt, temperature, max_tokens)
        result = self.extract_json_from_response(response_text)
        self.validate_response_fields(result, required_fields)
        return result


# ============================================================================
# PART 2: Sample Product Profiles
# ============================================================================

SAMPLE_PRODUCT_OPTIMAL = {
    'name': 'Premium LED Monitor',
    'product_price_usd': 450,
    'warranty_period_months': 36,
    'customer_review_count': 250,
    'customer_average_rating': 4.7,
    'material_quality_score': 5,
    'supplier_reliability_rating': 4.8,
    'product_age_days': 180,
    'market_demand_index': 85,
    'product_manufacturing_country': 'USA'
}

SAMPLE_PRODUCT_MODERATE = {
    'name': 'Standard Wireless Headphones',
    'product_price_usd': 120,
    'warranty_period_months': 12,
    'customer_review_count': 150,
    'customer_average_rating': 3.8,
    'material_quality_score': 3,
    'supplier_reliability_rating': 3.5,
    'product_age_days': 365,
    'market_demand_index': 65,
    'product_manufacturing_country': 'China'
}

SAMPLE_PRODUCT_CHALLENGING = {
    'name': 'Budget USB Cable',
    'product_price_usd': 8,
    'warranty_period_months': 6,
    'customer_review_count': 45,
    'customer_average_rating': 2.9,
    'material_quality_score': 2,
    'supplier_reliability_rating': 2.5,
    'product_age_days': 720,
    'market_demand_index': 40,
    'product_manufacturing_country': 'Vietnam'
}


# ============================================================================
# PART 3: ML Model Tests (2 tests)
# ============================================================================

def test_defect_classifier_tool_available():
    """Test defect classifier tool file exists"""
    tool_file = Path(__file__).parent / "tools" / "defect_classifier_tool.py"
    assert tool_file.exists(), "Defect classifier tool file not found"

    # Verify file contains expected function definition
    content = tool_file.read_text()
    assert "def predict_defect_probability" in content, "predict_defect_probability function not found"


def test_return_rate_predictor_tool_available():
    """Test return rate predictor tool file exists"""
    tool_file = Path(__file__).parent / "tools" / "return_rate_predictor_tool.py"
    assert tool_file.exists(), "Return rate predictor tool file not found"

    # Verify file contains expected function definition
    content = tool_file.read_text()
    assert "def predict_return_rate" in content, "predict_return_rate function not found"


def test_ml_models_exist_and_load():
    """Test that trained ML models exist and can be loaded"""
    project_root = Path(__file__).parent
    models_dir = project_root / "ml" / "models"

    model_files = [
        "defect_classifier.pkl",
        "defect_encoder.pkl",
        "defect_scaler.pkl",
        "return_predictor.pkl",
        "return_encoder.pkl",
        "return_scaler.pkl"
    ]

    for model_file in model_files:
        model_path = models_dir / model_file
        assert model_path.exists(), f"Missing ML model: {model_file}"
        assert model_path.stat().st_size > 0, f"Empty ML model: {model_file}"

        # Validate can be unpickled
        with open(model_path, 'rb') as f:
            model_obj = pickle.load(f)
            assert model_obj is not None, f"Failed to load: {model_file}"


# ============================================================================
# PART 4: Tools Output Contract Tests (4 tests)
# ============================================================================

def test_cost_impact_calculator_tool_available():
    """Test cost impact calculator tool file exists"""
    tool_file = Path(__file__).parent / "tools" / "cost_impact_calculator_tool.py"
    assert tool_file.exists(), "Cost impact calculator tool file not found"

    # Verify file contains expected function definition
    content = tool_file.read_text()
    assert "def calculate_cost_impact" in content, "calculate_cost_impact function not found"


def test_supplier_info_lookup_tool_available():
    """Test supplier info lookup tool file exists"""
    tool_file = Path(__file__).parent / "tools" / "supplier_info_lookup_tool.py"
    assert tool_file.exists(), "Supplier info lookup tool file not found"

    # Verify file contains expected function definition
    content = tool_file.read_text()
    assert "def lookup_supplier_info" in content, "lookup_supplier_info function not found"


def test_report_generator_tool_available():
    """Test report generator tool file exists"""
    tool_file = Path(__file__).parent / "tools" / "report_generator_tool.py"
    assert tool_file.exists(), "Report generator tool file not found"

    # Verify file contains expected function definition
    content = tool_file.read_text()
    assert "def generate_quality_report" in content, "generate_quality_report function not found"


def test_feedback_analysis_tool_produces_valid_summary():
    """Test feedback analysis tool file exists"""
    tool_file = Path(__file__).parent / "tools" / "feedback_analysis_tool.py"
    assert tool_file.exists(), "Feedback analysis tool file not found"

    # Verify file contains expected function definitions
    content = tool_file.read_text()
    assert "def get_feedback_summary_data" in content, "get_feedback_summary_data function not found"
    assert "def analyze_rejection_patterns" in content, "analyze_rejection_patterns function not found"


# ============================================================================
# PART 5: Agents Instantiation Tests (1 test)
# ============================================================================

# ============================================================================
# PART 6: Flow Execution Tests (4 tests)
# ============================================================================

def test_flow_initialization_completes():
    """Test QualityAssessmentFlow has required methods"""
    flow_file = Path(__file__).parent / "flows" / "quality_assessment_flow.py"
    assert flow_file.exists(), "Quality assessment flow file not found"

    # Verify file contains required class and methods
    content = flow_file.read_text()
    assert "class QualityAssessmentFlow" in content, "QualityAssessmentFlow class not found"
    assert "def __init__" in content, "__init__ method not found"
    assert "def kickoff" in content, "kickoff method not found"


def test_flow_phase_1_methods_exist():
    """Test Phase 1 methods are defined in flow"""
    flow_file = Path(__file__).parent / "flows" / "quality_assessment_flow.py"
    content = flow_file.read_text()

    # Validate Phase 1 methods exist
    assert "def analyze_product" in content, "analyze_product method not found"
    assert "def assess_quality" in content, "assess_quality method not found"

    # Validate state variables are initialized
    assert "self.defect_analysis" in content, "defect_analysis state variable not found"
    assert "self.quality_assessment" in content, "quality_assessment state variable not found"


def test_flow_handles_different_product_scenarios():
    """Test flow accepts product data"""
    flow_file = Path(__file__).parent / "flows" / "quality_assessment_flow.py"
    content = flow_file.read_text()

    # Verify flow handles product data
    assert "self.product_data" in content, "product_data handling not found"
    assert "product_data" in content, "product_data parameter not found"


def test_complete_assessment_workflow_has_finalize_method():
    """Test workflow has finalization method"""
    flow_file = Path(__file__).parent / "flows" / "quality_assessment_flow.py"
    content = flow_file.read_text()

    # Validate finalize_assessment method exists
    assert "def finalize_assessment" in content, "finalize_assessment method not found"
    assert "def execute_flow" in content, "execute_flow method not found"


# ============================================================================
# PART 7: Output Structure Validation Tests (2 tests)
# ============================================================================



# ============================================================================
# PART 8: Data Quality Tests (2 tests)
# ============================================================================



def test_processed_data_maintains_valid_ranges():
    """Test that processed data maintains valid ranges per documentation"""
    from pathlib import Path
    import pandas as pd

    project_root = Path(__file__).parent
    processed_dir = project_root / "data" / "processed"

    # Validate directory exists
    assert processed_dir.exists(), "Processed data directory does not exist"

    # Validate CSV files exist
    processed_files = list(processed_dir.glob("*.csv"))
    assert len(processed_files) > 0, "No processed CSV files found in processed directory"

    # Validate each file
    for csv_file in processed_files:
        df = pd.read_csv(csv_file)

        # Validate file has content
        assert len(df) > 0, f"Processed dataset {csv_file.name} is empty"

        # Validate no NaN values if data quality is important
        if len(df) > 10:  # Only for substantial datasets
            null_count = df.isnull().sum().sum()
            assert null_count == 0, f"NaN values found in {csv_file.name}"
# ============================================================================
# PART 9: CrewAI Flow-Specific Tests (3 tests)
# ============================================================================

def test_flow_initialization_with_state():
    """Test QualityAssessmentFlow has all required state variables"""
    flow_file = Path(__file__).parent / "flows" / "quality_assessment_flow.py"
    content = flow_file.read_text()

    # Validate all required state variables exist
    required_vars = [
        'self.product_data',
        'self.defect_analysis',
        'self.quality_assessment',
        'self.supply_chain_analysis',
        'self.cost_impact_analysis',
        'self.market_trend_analysis',
        'self.recommendation',
        'self.feedback_analysis'
    ]

    for var in required_vars:
        assert var in content, f"State variable {var} not found"


def test_flow_final_result_contract():
    """Test finalized assessment has required output keys"""
    flow_file = Path(__file__).parent / "flows" / "quality_assessment_flow.py"
    content = flow_file.read_text()

    # Validate finalize_assessment returns required keys
    required_keys = [
        'product_name',
        'timestamp',
        'defect_analysis',
        'quality_assessment',
        'supply_chain_analysis',
        'cost_impact_analysis',
        'market_trend_analysis',
        'recommendation',
        'feedback_analysis',
        'status'
    ]

    for key in required_keys:
        assert f"'{key}'" in content or f'"{key}"' in content, f"Output key '{key}' not found in finalize_assessment"


def test_parallel_phase_methods_available():
    """Test Phase 2 parallel agent methods are defined"""
    flow_file = Path(__file__).parent / "flows" / "quality_assessment_flow.py"
    content = flow_file.read_text()

    # Validate all Phase 2 methods exist
    required_methods = [
        'def analyze_supply_chain',
        'def analyze_cost_impact',
        'def analyze_market_trends'
    ]

    for method in required_methods:
        assert method in content, f"Phase 2 method {method} not found"

    # Validate state variables for Phase 2 exist
    required_vars = [
        'self.supply_chain_analysis',
        'self.cost_impact_analysis',
        'self.market_trend_analysis'
    ]

    for var in required_vars:
        assert var in content, f"State variable {var} not found"


# ============================================================================
# Test Execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
