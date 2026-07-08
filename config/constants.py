"""
QualityGuard Configuration Constants.

All hardcoded values centralized here. Update in one place, used everywhere.
"""

# ============================================================================
# GRADE & QUALITY THRESHOLDS
# ============================================================================
GRADE_THRESHOLDS = {
    "EXCELLENT": {"defect_prob": 5, "return_rate": 10},
    "GOOD": {"defect_prob": 15, "return_rate": 25},
    "ACCEPTABLE": {"defect_prob": 40, "return_rate": 50},
    "POOR": {"defect_prob": float("inf"), "return_rate": float("inf")},
}

QUALITY_SCORE_THRESHOLDS = {
    "EXCELLENT": 85,
    "GOOD": 70,
    "ACCEPTABLE": 55,
    "POOR": 0,
}

# ============================================================================
# RISK & FINANCIAL THRESHOLDS
# ============================================================================
RISK_THRESHOLDS = {
    "CRITICAL": 15,  # > 15%
    "HIGH": 10,      # > 10%
    "MEDIUM": 5,     # > 5%
    "LOW": 0,        # <= 5%
}

# Cost impact calculation multipliers
DEFECT_LOSS_PERCENTAGE = 0.5    # 50% loss on defective units
RETURN_LOSS_PERCENTAGE = 0.3    # 30% loss on returned units
HANDLING_COST_PERCENTAGE = 0.15 # 15% handling cost multiplier

# ============================================================================
# INVENTORY & DEFAULTS
# ============================================================================
DEFAULT_INVENTORY = 1000  # Units

# ============================================================================
# VALIDATION BOUNDS (Data Cleaning)
# ============================================================================
VALIDATION_BOUNDS = {
    "product_price_usd": (0, 5000),
    "warranty_period_months": (0, 60),
    "customer_review_count": (0, 5000),
    "customer_average_rating": (1, 5),
    "material_quality_score": (1, 5),
    "supplier_reliability_rating": (1, 5),
    "product_age_days": (0, 3650),  # 10 years max
    "market_demand_index": (0, 100),
}

# ============================================================================
# MODEL HYPERPARAMETERS
# ============================================================================
MODEL_HYPERPARAMETERS = {
    "n_estimators": 50,
    "max_depth": 10,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "random_state": 42,
    "n_jobs": -1,
}

# ML Training parameters
TEST_SIZE = 0.2
RANDOM_STATE = 42

# ============================================================================
# SUPPLIER DATA
# ============================================================================
SUPPLIER_DATA = {
    "USA": {
        "reliability_score": 4.5,
        "lead_time_days": 14,
        "certifications": ["ISO 9001", "ISO 13485"],
        "average_defect_rate": 0.8,
    },
    "CHINA": {
        "reliability_score": 3.8,
        "lead_time_days": 28,
        "certifications": ["ISO 9001", "CCC"],
        "average_defect_rate": 2.1,
    },
    "VIETNAM": {
        "reliability_score": 4.0,
        "lead_time_days": 21,
        "certifications": ["ISO 9001"],
        "average_defect_rate": 1.5,
    },
    "INDIA": {
        "reliability_score": 3.9,
        "lead_time_days": 25,
        "certifications": ["ISO 9001", "BIS"],
        "average_defect_rate": 1.8,
    },
    "MEXICO": {
        "reliability_score": 4.2,
        "lead_time_days": 10,
        "certifications": ["ISO 9001", "ISO 14001"],
        "average_defect_rate": 1.2,
    },
    "GERMANY": {
        "reliability_score": 4.8,
        "lead_time_days": 7,
        "certifications": ["ISO 9001", "ISO 13485", "DIN EN ISO"],
        "average_defect_rate": 0.5,
    },
}

VALID_COUNTRIES = list(SUPPLIER_DATA.keys())  # ["USA", "CHINA", "VIETNAM", "INDIA", "MEXICO", "GERMANY"]

# ============================================================================
# ML FEATURES
# ============================================================================
CATEGORICAL_FEATURES = ["product_manufacturing_country"]

NUMERICAL_FEATURES = [
    "product_price_usd",
    "warranty_period_months",
    "customer_review_count",
    "customer_average_rating",
    "material_quality_score",
    "supplier_reliability_rating",
    "product_age_days",
    "market_demand_index",
]

# Feature order: categorical first, then numerical
ML_FEATURES_ORDERED = CATEGORICAL_FEATURES + NUMERICAL_FEATURES

# ============================================================================
# FILE PATHS & DIRECTORIES
# ============================================================================
DATA_INPUT_DIR = "data/input"
DATA_ASSESSMENTS_DIR = "data/assessments"
DATA_FEEDBACK_DIR = "data/feedback"
ML_MODELS_DIR = "ml/models"
PRODUCTS_FILE = "data/input/products.json"

# ============================================================================
# FEEDBACK ANALYSIS
# ============================================================================
FEEDBACK_REQUIRED_KEYS = [
    "analysis_status",
    "key_findings",
    "agent_performance",
    "threshold_adjustments",
    "mismatch_count",
    "recommendations",
    "next_actions",
]
FEEDBACK_KEYWORDS = {
        "Product Analyzer": ["defect", "defective", "fault", "manufacturing"],
        "Quality Assessor": ["quality", "return", "rating", "score"],
        "Supply Chain":     ["supply", "supplier", "chain", "logistics"],
        "Cost Impact":      ["cost", "financial", "impact", "loss", "budget"],
        "Market Trend":     ["market", "demand", "trend", "competitive"],
    }

# ============================================================================
# STATUS VALUES
# ============================================================================
STATUS_APPROVED = "APPROVED"
STATUS_REJECTED = "REJECTED"
STATUS_PENDING_REVIEW = "PENDING_REVIEW"
STATUS_PENDING_HUMAN_APPROVAL = "PENDING_HUMAN_APPROVAL"

# ============================================================================
# UI CONFIGURATION
# ============================================================================
ASSESSMENT_TABS = [
    "Defect Analysis",
    "Quality Assessment",
    "Supply Chain",
    "Cost Impact",
    "Market Trends",
    "Recommendation",
    "Debug / Raw Data",
]

# ============================================================================
# MODEL NAMES
# ============================================================================
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"

# ============================================================================
# JSON EXTRACTION CONFIGURATION
# ============================================================================
JSON_EXTRACT_STRATEGIES = {
    "json_dict": 1,      # Priority: Try json_dict first
    "regex": 2,          # Priority: Then regex extraction
    "raw_parse": 3,      # Priority: Then raw string parse
}

MAX_JSON_EXTRACT_ATTEMPTS = 5  # Try up to 5 different JSON patterns
