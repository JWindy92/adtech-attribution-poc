# Bayesian Media Mix Modeling (MMM) POC

Internal directional intelligence for inventory performance, pricing, and yield optimization at Comcast Advertising.

## Overview

**Our Position**: Comcast Advertising is an **ad inventory seller** (CTV, Linear TV, digital). We sell inventory to advertisers who use external attribution vendors (e.g., Clarivoy) for measurement.

**This POC Purpose**: Build internal analytics to supplement vendor attribution and drive business strategy:
- **Estimate incremental lift** from our inventory (CTV, Linear TV)
- **Identify upsell opportunities** by detecting saturation vs. headroom
- **Optimize pricing** based on marginal ROI, not just CPM
- **Enable sales teams** with data-driven proof of inventory value
- **Prevent churn** by flagging over-saturated advertisers before they cut spend

**Critical**: All outputs are for **internal use only** — directional intelligence to guide pricing, yield, packaging, and sales strategy. We are not replacing advertiser-facing attribution vendors.

## Project Structure

```
adtech-attribution-pipeline/
├── src/                    # Core application code
│   ├── datasources/       # Data ingestion implementations
│   │   ├── base.py        # DataSource interface
│   │   ├── csv.py         # CSV file source ✓
│   │   └── databricks.py  # Databricks source (stub)
│   ├── transformers/      # Feature transformations
│   │   ├── base.py        # Transformer interface
│   │   ├── passthrough.py # No-op transformer ✓
│   │   └── adstock_saturation.py  # Adstock/saturation ✓
│   ├── models/            # Attribution models
│   │   ├── base.py        # AttributionModel interface
│   │   ├── spend_proportional.py  # Simple attribution ✓
│   │   └── bayesian_mmm.py        # Bayesian MMM ✓
│   ├── optimizers/        # Budget optimization
│   │   ├── base.py        # Optimizer interface
│   │   ├── simple.py      # Efficiency-based optimizer ✓
│   │   └── scipy.py       # SciPy optimizer ✓
│   └── pipeline.py        # Orchestration via dependency injection ✓
├── app/                   # Dashboard applications
│   ├── dashboard.py       # Streamlit dashboard (simple)
│   └── dashboard_bayesian.py  # Bayesian MMM dashboard ✓
├── data/                  # CSV files and synthetic data generators
│   ├── generate_synthetic_data.py  # MMM dataset generator ✓
│   ├── generate_event_stream.py    # Event-level data example ✓
│   ├── synthetic_mmm_data.csv      # 104 weeks realistic data ✓
│   └── dummy_media_data.csv        # Original simple dataset
├── docs/                  # Documentation
│   ├── attribution_landscape.md    # Attribution methods overview ✓
│   ├── data_landscape.md           # Data hierarchy guide ✓
│   └── stage3_bayesian_mmm.md      # Bayesian implementation docs ✓
├── tests/                 # Test scripts
│   ├── test_pipeline.py            # Full pipeline test ✓
│   ├── test_architecture.py        # Architecture demo ✓
│   └── test_bayesian_pipeline.py   # Bayesian pipeline test ✓
├── run_bayesian_mmm.py    # Quick start runner ✓
└── requirements.txt       # Python dependencies ✓
```

## Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard:**
   ```bash
   # Simple spend-proportional dashboard
   streamlit run app/dashboard.py
   
   # Bayesian MMM dashboard (recommended)
   streamlit run app/dashboard_bayesian.py
   ```

4. **Or run the Bayesian pipeline directly:**
   ```bash
   python run_bayesian_mmm.py
   ```

## Tech Stack

- **PyMC**: Bayesian inference and MCMC sampling
- **ArviZ**: Posterior analysis and diagnostics
- **Pandas/NumPy**: Data manipulation
- Dependencies installed

### Stage 2: Simple Data Flow ✅
- End-to-end data flow with realistic synthetic data
- Passthrough transformer and spend-proportional attribution
- Simple efficiency-based optimizer
- Working Streamlit dashboard

### Stage 3: Bayesian MMM Implementation ✅
- Adstock/saturation transformers (carryover + diminishing returns)
- Bayesian hierarchical regression with PyMC
- SciPy constrained optimization
- Enhanced dashboard with model comparison
- Posterior distribution analysiDays 2-5)
- End-to-end data flow with dummy data
- Basic transforms and stub models
- Dashboard displays dummy outputs

### Stage 3: Business Logic Complete (Days 6-14)
- Full Bayesian MMM implementation
- Response curve modeling and optimization
- Production-ready visualizations
- Scenario planning capabilities

## Key Features

- **Privacy-Safe**: Aggregate-level analysis, no user-level tracking
- **Cross-Channel**: Unified view of our inventory (CTV, Linear TV) + competitor channels
- **Probabilistic**: Credible intervals for uncertainty quantification
- **Actionable**: Upsell opportunities, pricing insights, saturation detection
- **Directional**: Supplements vendor attribution, guides internal strategy

## Quick Start

### Test the Bayesian Pipeline
```bash
python tests/test_bayesian_pipeline.py
```

### Run End-to-End
```bash
python run_bayesian_mmm.py
```

This will:
1. Load 104 weeks of synthetic data with realistic MMM properties
2. Apply adstock (carryover) and saturation (diminishing returns) transformations
3. Run Bayesian MCMC sampling to estimate channel contributions
4. Optimize budget allocation using constrained optimization
5. Display attribution metrics and posterior distributions

### Launch Interactive Dashboard
```bash
streamlit run app/dashboard_bayesian.py
```

Toggle between:
- **Spend-Proportional**: Simple baseline attribution
- **Bayesian MMM**: Advanced model with uncertainty quantification

## Understanding the Data

See documentation:
- [Attribution Landscape](.copilot/enrichment/attribution_landscape.md) - Overview of MTA, MMM, Incrementality Testing
- [Data Landscape](docs/data_landscape.md) - Event-level vs aggregate data, SQL examples
- [Stage 3 Implementation](docs/stage3_bayesian_mmm.md) - Bayesian MMM technical details

## License

Internal POC - Comcast Advertising
