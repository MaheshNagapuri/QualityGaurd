# QualityGuard: AI-Powered Product Quality Assessment System

**QualityGuard** is an intelligent product quality assessment platform that leverages AI agents, machine learning models, and multi-agent reasoning to evaluate products comprehensively. It provides real-time quality predictions, risk assessments, financial impact analysis, and actionable recommendations to optimize product quality and supply chain decisions.

## 🎯 Overview

QualityGuard uses a sophisticated multi-agent architecture powered by **CrewAI** and **Google Gemini AI** to orchestrate intelligent analysis across multiple dimensions:

- **Defect Classification**: ML-based prediction of product defect probability
- **Return Rate Prediction**: Time-series forecasting of customer return rates
- **Quality Grading**: Comprehensive quality assessment (EXCELLENT → POOR)
- **Supply Chain Analysis**: Supplier evaluation and sourcing recommendations
- **Cost Impact Analysis**: Financial impact modeling for defects and returns
- **Market Trend Analysis**: Market conditions and competitive positioning
- **Feedback Analytics**: Customer feedback analysis and sentiment tracking

## 🏗️ Architecture

### Multi-Agent System (4-Phase Execution)

```
Phase 1: Sequential Analysis
├── Product Analyzer Agent
│   └── Analyzes defect probability using ML models
└── Quality Assessor Agent
    └── Evaluates overall product quality

Phase 2: Parallel Analysis (Concurrent)
├── Supply Chain Agent
│   └── Evaluates suppliers and logistics
├── Cost Impact Agent
│   └── Calculates financial implications
└── Market Trend Agent
    └── Analyzes market conditions

Phase 3: Sequential Synthesis
└── Recommendation Agent
    └── Synthesizes all insights into actionable recommendations

Phase 4: Feedback Loop (User-Triggered)
└── Feedback Analyzer Agent
    └── Analyzes customer feedback for improvements
```

### Technology Stack

| Component                 | Technology       |
| ------------------------- | ---------------- |
| **AI Framework**    | CrewAI           |
| **LLM Provider**    | Google Gemini AI |
| **ML Pipeline**     | Scikit-learn     |
| **Data Processing** | Pandas, NumPy    |
| **UI Framework**    | Streamlit        |
| **Python Version**  | 3.8+             |

## 📦 Project Structure

```
Project/
├── main.py                          # Streamlit UI entry point
├── tests.py                         # Unit tests
├── agents/                          # AI agents
│   ├── product_analyzer_agent.py    # Defect analysis
│   ├── quality_assessor_agent.py    # Quality assessment
│   ├── supply_chain_agent.py        # Supply chain analysis
│   ├── cost_impact_agent.py         # Cost calculations
│   ├── market_trend_agent.py        # Market analysis
│   ├── recommendation_agent.py      # Recommendations
│   └── feedback_analyzer_agent.py   # Feedback analysis
├── flows/                           # Orchestration logic
│   └── quality_assessment_flow.py   # Main flow controller
├── tasks/                           # Agent task definitions
│   ├── product_analysis_task.py
│   ├── quality_assessment_task.py
│   ├── supply_chain_task.py
│   ├── cost_impact_task.py
│   ├── market_trend_task.py
│   ├── recommendation_task.py
│   └── feedback_analysis_task.py
├── ml/                              # ML pipeline
│   ├── train_pipeline.py            # Training orchestrator
│   ├── data_cleaning/               # Data preprocessing
│   │   ├── clean_defect_classifier_data.py
│   │   └── clean_return_rate_predictor_data.py
│   ├── train_model/                 # Model training
│   │   ├── train_defect_classifier.py
│   │   └── train_return_rate_predictor.py
│   └── evaluation/                  # Model evaluation
│       └── evaluate_models.py
├── tools/                           # Tool implementations
│   ├── defect_classifier_tool.py    # Defect prediction
│   ├── return_rate_predictor_tool.py # Return forecasting
│   ├── cost_impact_calculator_tool.py
│   ├── feedback_analysis_tool.py
│   ├── report_generator_tool.py
│   └── supplier_info_lookup_tool.py
├── config/                          # Configuration
│   └── constants.py                 # All configuration constants
├── utils/                           # Utilities
│   ├── gemini_client.py             # LLM initialization
│   └── json_extractor.py            # JSON parsing utilities
└── data/                            # Data directory
    ├── input/
    │   └── products.json
    ├── training_dataset/
    │   ├── defect_classifier_training.csv
    │   └── return_rate_predictor_training.csv
    └── evaluation_dataset/
        ├── defect_classifier_evaluation.csv
        └── return_rate_predictor_evaluation.csv
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip or conda package manager
- Google Gemini API key (for AI capabilities)

### Installation

1. **Clone the repository** (if applicable)

   ```powershell
   cd QUALITYGUARD-MaheshNagapuri\hackathon
   ```
2. **Create a virtual environment**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. **Install dependencies**

   ```powershell
   pip install -r requirements.txt
   ```

   Or manually install from `installation.txt`:

   ```powershell
   pip install crewai[google-genai] crewai-tools google-generativeai pandas numpy scikit-learn streamlit python-dotenv
   ```
4. **Set up environment variables**

   Create a `.env` file in the `Project/` directory:

   ```
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```
5. **Prepare data**

   Ensure the following files exist:

   - `data/input/products.json` - Product catalog
   - `data/training_dataset/` - Training data files
   - `data/evaluation_dataset/` - Evaluation data files

### Running the Application

1. **Start the Streamlit UI**

   ```powershell
   cd Project
   streamlit run main.py
   ```

   The application will open at `http://localhost:8501`
2. **Train ML Models** (optional, if needed)

   ```powershell
   python -c "from ml.train_pipeline import TrainPipeline; pipeline = TrainPipeline(); pipeline.run()"
   ```
3. **Run Tests**

   ```powershell
   python -m pytest tests.py -v
   ```

## 💡 Usage Guide

### Main UI Tabs

#### 1. **New Assessment**

- Select a product from the catalog
- System analyzes defect probability and return rate
- View quality grade (EXCELLENT, GOOD, ACCEPTABLE, POOR)
- Review AI-generated recommendations
- Approve or reject assessment (human-in-the-loop)
- Receive supply chain and cost impact insights

#### 2. **Assessment History**

- View all past product assessments
- Filter by date, status, or quality grade
- Re-evaluate previous assessments
- Track decision trends over time

#### 3. **Feedback Analysis**

- Submit customer feedback for analysis
- AI analyzes sentiment and themes
- Identify common issues and improvement areas
- Generate insights for product improvement

#### 4. **Model Evaluation**

- View defect classifier performance metrics
- View return rate predictor performance metrics
- Compare model accuracy across evaluation datasets
- Retraining recommendations

## 🎓 Key Features

### AI-Powered Analysis

- **Multi-Agent Reasoning**: 7 specialized agents working in coordinated phases
- **Hybrid Execution**: Sequential and parallel processing for efficiency
- **Context-Aware Recommendations**: Agents understand product context and market dynamics

### Machine Learning Pipeline

- **Automatic Data Cleaning**: Handles missing values, outliers, normalization
- **Model Training**: Scikit-learn models for defect and return rate prediction
- **Evaluation Metrics**: Accuracy, precision, recall, RMSE, MAE, R² scores

### Quality Assessment

- **Grade Thresholds**: EXCELLENT (defect <5%), GOOD (defect <15%), ACCEPTABLE (defect <40%), POOR
- **Risk Levels**: CRITICAL (>15%), HIGH (>10%), MEDIUM (>5%), LOW (≤5%)
- **Quality Score**: Composite metric from 0-100

### Financial Analysis

- **Defect Loss**: 50% loss on defective units
- **Return Loss**: 30% loss on returned units
- **Handling Costs**: 15% handling cost multiplier
- **ROI Calculations**: Cost-benefit analysis for quality improvements

## 🔧 Configuration

All configuration is centralized in `config/constants.py`. Key settings:

- **Grade Thresholds**: Adjust quality grade boundaries
- **Risk Thresholds**: Customize risk level cutoffs
- **Cost Multipliers**: Fine-tune financial impact calculations
- **Inventory Defaults**: Set default inventory levels
- **Validation Bounds**: Configure data validation ranges

## 📊 Data Formats

### Product Input Format (products.json)

```json
{
  "product_id": "P001",
  "product_name": "Product Name",
  "category": "Category",
  "product_price_usd": 100.0,
  "warranty_period_months": 12,
  "customer_review_count": 500,
  "average_customer_rating": 4.5,
  "market_demand": "HIGH",
  "supplier_reliability": "HIGH",
  "country": "USA"
}
```

### Assessment Result Format

```json
{
  "assessment_id": "unique_id",
  "product_id": "P001",
  "timestamp": "2024-03-12T10:30:00",
  "defect_probability": 8.5,
  "return_rate": 12.3,
  "quality_grade": "GOOD",
  "quality_score": 75,
  "risk_level": "MEDIUM",
  "cost_impact": 5000.0,
  "recommendations": ["..."],
  "human_approval": true
}
```

## 🧪 Testing

Run the test suite:

```powershell
python -m pytest tests.py -v
```

Tests cover:

- ML model training and evaluation
- Agent execution and output validation
- Flow orchestration correctness
- Tool functionality
- Data cleaning and validation

## 📈 Performance Metrics

- **Defect Classifier Accuracy**: ~92% on evaluation set
- **Return Rate Predictor R² Score**: ~0.88
- **Assessment Time**: ~30-45 seconds per product
- **Throughput**: Handle multiple concurrent assessments

## 🔐 Security & Best Practices

1. **API Key Management**

   - Store Google API key in `.env` (never commit)
   - Use environment variables for all sensitive data
2. **Data Privacy**

   - Customer feedback stored securely
   - Assessment data encrypted at rest (recommended)
   - GDPR compliance for customer information
3. **Model Governance**

   - Regular model retraining (monthly recommended)
   - Continuous monitoring of prediction drift
   - Version control for model artifacts

## 🤝 Contributing

To contribute to QualityGuard:

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📚 Documentation

- **Agent Documentation**: See docstrings in `agents/` directory
- **ML Pipeline**: See `ml/README.md` (if available)
- **API Reference**: See inline documentation in `tools/` directory
- **Configuration Guide**: See `config/constants.py` for all settings

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Google API Key not found"

- **Solution**: Create `.env` file with `GOOGLE_API_KEY=your_key`

**Issue**: "Models not found"

- **Solution**: Run the ML training pipeline: `python ml/train_pipeline.py`

**Issue**: "Products.json missing"

- **Solution**: Ensure `data/input/products.json` exists with valid product data

**Issue**: Streamlit app not loading

- **Solution**: Check port 8501 is available, or use `streamlit run main.py --server.port 8502`

## 🙏 Acknowledgments

- Built with **CrewAI** framework
- Powered by **Google Gemini AI**
- ML models developed with **Scikit-learn**
- UI built with **Streamlit**

---
