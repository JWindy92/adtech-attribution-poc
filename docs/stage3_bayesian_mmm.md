# Stage 3: Bayesian MMM Implementation

## Components Implemented

### 1. Adstock & Saturation Transformer
**File**: `src/transformers/adstock_saturation.py`

**Purpose**: Apply adstock (carryover effects) and saturation (diminishing returns) transformations to media spend data.

**Features**:
- **Adstock**: Geometric decay model for lagged effects (e.g., TV ads have lasting impact)
- **Saturation**: Hill equation for diminishing returns (e.g., doubling spend doesn't double conversions)
- Configurable per-channel parameters

**Example**:
```python
from src.transformers.adstock_saturation import AdstockSaturationTransformer

adstock_params = {
    'ctv_spend': {'decay': 0.7, 'max_lag': 8},
    'search_spend': {'decay': 0.3, 'max_lag': 2}
}

saturation_params = {
    'ctv_spend': {'alpha': 1.2, 'gamma': 100000},
    'search_spend': {'alpha': 1.5, 'gamma': 40000}
}

transformer = AdstockSaturationTransformer(adstock_params, saturation_params)
```

### 2. Bayesian MMM Model
**File**: `src/models/bayesian_mmm.py`

**Purpose**: Hierarchical Bayesian regression using PyMC for probabilistic attribution.

**Features**:
- MCMC sampling for posterior distributions
- Credible intervals via ArviZ
- Channel coefficient estimation with uncertainty quantification
- Interpretable beta coefficients

**Example**:
```python
from src.models.bayesian_mmm import BayesianMMMModel

model = BayesianMMMModel(samples=2000, tune=1000, target_accept=0.9)
attribution = model.fit(df, media_columns)

posterior_summary = model.get_posterior_summary()
```

### 3. SciPy Optimizer
**File**: `src/optimizers/scipy.py`

**Purpose**: Constrained optimization for budget allocation using scipy.optimize.

**Features**:
- SLSQP algorithm for nonlinear constrained optimization
- Maximizes total conversions given budget constraint
- Respects channel min/max bounds

**Example**:
```python
from src.optimizers.scipy import ScipyOptimizer

optimizer = ScipyOptimizer(min_channel_budget=1000)
optimization = optimizer.optimize(metrics, total_budget=1000000)
```

## Testing

### Run Bayesian Pipeline Test
```bash
python tests/test_bayesian_pipeline.py
```

This will:
1. Load synthetic MMM data (104 weeks)
2. Apply adstock/saturation transformations
3. Run Bayesian MCMC sampling (~1-2 minutes)
4. Display attribution results with posterior summaries
5. Optimize budget allocation

### Launch Dashboard
```bash
streamlit run app/dashboard_bayesian.py
```

Features:
- Toggle between Spend-Proportional and Bayesian MMM
- View attribution percentages
- See cost per conversion by channel
- Compare current vs optimal budget allocation
- Explore posterior distributions (Bayesian mode)

## Data Flow

```
CSV Data (synthetic_mmm_data.csv)
    ↓
Adstock Transformation (carryover effects)
    ↓
Saturation Transformation (diminishing returns)
    ↓
Bayesian Regression (PyMC MCMC sampling)
    ↓
Attribution Metrics (with credible intervals)
    ↓
SciPy Optimization (constrained budget allocation)
```

## Parameters Tuning

### Adstock Parameters
- `decay`: [0, 1] - Higher = longer carryover (TV typically 0.6-0.8)
- `max_lag`: weeks - How far back effects persist (TV: 6-8, Search: 1-2)

### Saturation Parameters
- `alpha`: shape parameter (>1 = rapid saturation, <1 = slow saturation)
- `gamma`: half-saturation point (typical spend level where returns diminish)

### MCMC Sampling
- `samples`: posterior draws (trade-off: accuracy vs speed)
- `tune`: adaptation steps (typically 500-1000)
- `target_accept`: acceptance rate (0.8-0.95 for better convergence)

## Dependencies

Required packages (already in requirements.txt):
- `pymc>=5.10.0` - Bayesian modeling
- `arviz>=0.17.0` - Posterior analysis
- `scipy>=1.11.0` - Optimization

## Architecture

All components follow the ABC (Abstract Base Class) pattern:
- `Transformer` → AdstockSaturationTransformer
- `AttributionModel` → BayesianMMMModel
- `Optimizer` → ScipyOptimizer

Pluggable via `Pipeline` dependency injection.
