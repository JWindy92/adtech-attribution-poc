# Bayesian Media Mix Modeling (MMM) POC

Privacy-safe, cross-channel attribution and budget optimization for Comcast Advertising.

## Overview

This POC demonstrates an end-to-end Bayesian Media Mix Modeling workflow that:
- Estimates channel contributions with credible intervals
- Models diminishing returns across ad channels
- Optimizes budget allocation based on response curves
- Provides actionable insights through an interactive dashboard

## Project Structure

```
adtech-attribution-pipeline/
├── src/                    # Core application code
│   ├── datasources/       # Data ingestion implementations
│   │   ├── base.py        # DataSource interface
│   │   ├── csv.py         # CSV file source
│   │   └── databricks.py  # Databricks source (stub)
│   ├── transformers/      # Feature transformations
│   │   ├── base.py        # Transformer interface
│   │   ├── passthrough.py # No-op transformer
│   │   └── adstock_saturation.py  # Adstock/saturation (stub)
│   ├── models/            # Attribution models
│   │   ├── base.py        # AttributionModel interface
│   │   ├── spend_proportional.py  # Simple attribution
│   │   └── bayesian_mmm.py        # Bayesian MMM (stub)
│   ├── optimizers/        # Budget optimization
│   │   ├── base.py        # Optimizer interface
│   │   ├── simple.py      # Efficiency-based optimizer
│   │   └── scipy.py       # SciPy optimizer (stub)
│   └── pipeline.py        # Orchestration via dependency injection
├── app/                   # Dashboard application
│   └── dashboard.py       # Streamlit dashboard
├── data/                  # CSV files and datasets
├── tests/                 # Test scripts
│   ├── test_ingestion.py
│   └── test_attribution.py
├── test_pipeline.py       # Full pipeline test
├── test_architecture.py   # Architecture demo
└── requirements.txt       # Python dependencies
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
   streamlit run app/dashboard.py
   ```

## Tech Stack

- **PyMC**: Bayesian inference and MCMC sampling
- **ArviZ**: Posterior analysis and diagnostics
- **Pandas/NumPy**: Data manipulation
- **SciPy**: Optimization algorithms
- **Streamlit**: Interactive dashboard
- **Plotly**: Visualizations

## Development Roadmap

### Stage 1: Initial Setup ✅
- Project structure established
- Placeholder services and modules created

### Stage 2: Simple Data Flow (Days 2-5)
- End-to-end data flow with dummy data
- Basic transforms and stub models
- Dashboard displays dummy outputs

### Stage 3: Business Logic Complete (Days 6-14)
- Full Bayesian MMM implementation
- Response curve modeling and optimization
- Production-ready visualizations
- Scenario planning capabilities

## Key Features

- **Privacy-Safe**: Aggregate-level measurement, no user-level tracking
- **Cross-Channel**: Unified view of CTV, social, search, linear TV
- **Probabilistic**: Credible intervals for uncertainty quantification
- **Actionable**: Optimized budget recommendations

## License

Internal POC - Comcast Advertising
