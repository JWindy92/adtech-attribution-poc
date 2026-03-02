# Complete Rebuild Plan: Bayesian MMM from First Principles

## Goal
Build a production-ready Bayesian Media Mix Model that:
- Handles any real-world ad spend data (no hardcoding)
- Uses industry-standard approaches (Google, Meta, Analytic Partners papers)
- Is thoroughly tested with schema validation
- Produces realistic budget optimization recommendations

---

## Architecture Overview

```
Raw Data (CSVDataSource)
    ↓
[Optional: Adstock Transformer] ← Carryover effects (known from domain)
    ↓
Bayesian MMM Model
    ├─ Learn: alpha (curve shape), gamma (saturation point), beta (channel power)
    ├─ Input: spend data + conversions
    └─ Output: Posterior trace + summary DataFrame
    ↓
ScipyOptimizer
    ├─ Input: betas + saturation params + total_budget
    └─ Output: Optimized allocation + objective value
    ↓
Results (CSV + visualizations)
```

---

## Phase 1: Mathematical Foundation (Core Functions)

### 1.1 Hill Saturation Function
**Location:** `src/core/saturation.py`

```
Function: hill_saturation(spend, alpha, gamma)
Input: 
  - spend: ndarray, shape (n_time_periods, n_channels) OR (n_channels,) OR scalar
  - alpha: ndarray shape (n_channels,) or scalar
  - gamma: ndarray shape (n_channels,) or scalar
Output:
  - saturated_spend: same shape as input spend
Formula: saturated = spend^alpha / (gamma^alpha + spend^alpha)
```

**Test Suite:** `tests/core/test_saturation.py`
- ✓ Saturated value at spend=0 is 0
- ✓ Saturated value increases with spend
- ✓ Saturated value approaches 1 asymptotically
- ✓ alpha=1 (linear) produces linear saturation (no ceiling)
- ✓ alpha>1 (curved) produces S-curve
- ✓ Shape invariance: scale spend by 1000, alpha/gamma must scale appropriately
- ✓ NaN/Inf handling: negative spend raises error, negative gamma raises error
- ✓ Broadcasting works correctly for vectorized operations

---

### 1.2 Scale-Adaptive Prior Calculation
**Location:** `src/core/prior_calculation.py`

```
Function: calculate_gamma_prior(raw_spend_data)
Input: ndarray shape (n_weeks, n_channels)
Output: 
  - gamma_mu: ndarray shape (n_channels,) [log scale]
  - gamma_sigma: float [width parameter]
Logic:
  1. gamma_mu[ch] = log(mean(raw_spend_data[:, ch]))
  2. gamma_sigma = 1.0 (industry standard)
Principle: Priors are centered on observed data, works at any scale
```

**Test Suite:** `tests/core/test_prior_calculation.py`
- ✓ Returns correct shapes
- ✓ gamma_mu[ch] = log(mean(spend[ch])) exactly
- ✓ Scale invariance: data * 1000 → mu increases by log(1000)
- ✓ Single week of data works
- ✓ Single channel works
- ✓ 100+ channels works (enterprise scale)
- ✓ Output is always finite (no NaN/Inf)

---

### 1.3 AdstockTransformer Integration
**Location:** `src/transformers/adstock_transformer.py` (EXISTING - verify works)

```
Input: raw_df with spend columns
Output: df with spend columns transformed via Adstock
Purpose: Captures carryover effects from past spend
Note: Parameters passed via DEFAULT_ADSTOCK_PARAMS (domain knowledge)
```

**Verification Tests:** `tests/transformers/test_adstock.py`
- ✓ Existing tests pass
- ✓ Schema: output has all input columns
- ✓ No data loss: output same shape as input
- ✓ Output ≤ input (decay effect)

---

## Phase 2: Bayesian Model

### 2.1 BayesianMMM Class
**Location:** `src/models/bayesian_mmm.py`

```python
class BayesianMMM:
    def __init__(self, ctx: AppContext, n_samples=2000, n_tune=1000, target_accept=0.95):
        # Store config + parameters
        
    def fit(self, spend_data: pd.DataFrame, conversions: np.ndarray) -> None:
        """
        Learn posterior of (alpha, gamma, beta, intercept, sigma) from data.
        
        Input:
          - spend_data: shape (n_weeks, n_channels), raw or adstocked spend
          - conversions: shape (n_weeks,), observed conversions
        
        Output:
          - Sets self.trace (arviz InferenceData)
          - Stored in ctx.state["trace"]
        
        Process:
          1. Calculate gamma_priors from spend_data
          2. Define PyMC model:
             - alpha ~ Uniform(0.1, 3.0) per channel [universal]
             - gamma ~ LogNormal(gamma_mu, gamma_sigma) per channel [scale-adaptive]
             - beta ~ HalfNormal(...) per channel [effectiveness]
             - intercept ~ Normal(...) [baseline]
             - sigma ~ HalfNormal(...) [noise]
          3. Apply Hill saturation inside model
          4. Likelihood: conversions ~ Normal(mu, sigma)
          5. Sample with NUTS
        """
        
    def get_posterior_summary(self) -> pd.DataFrame:
        """
        Return: DataFrame with columns:
          [variable, mean, sd, hdi_3%, hdi_97%, ...]
        Schema validation: Must have alpha, gamma, beta, intercept rows
        """
```

**Test Suite:** `tests/models/test_bayesian_mmm.py`

**Unit Tests:**
- ✓ Schema validation: posterior_summary has required columns
- ✓ Schema validation: posterior_summary has row per parameter
- ✓ Alpha values in [0.1, 3.0]
- ✓ Gamma values > 0
- ✓ Beta values > 0
- ✓ Intercept finite
- ✓ Convergence: r_hat < 1.1 for all parameters

**Integration Tests:**
- ✓ Synthetic data where ground truth is known: recovered correct betas
- ✓ Data at 100x scale produces equivalent results (numerical stability)
- ✓ Handles 1 channel, 2 channels, 50 channels
- ✓ Handles 10 weeks, 52 weeks, 500 weeks of data
- ✓ Different spend distributions (uniform, exponential, bimodal)

**Failure Mode Tests:**
- ✓ Raises error if spend has negative values
- ✓ Raises error if conversions have negative values
- ✓ Raises error if spend/conversions shape mismatch
- ✓ Graceful handling if data has no variance

---

## Phase 3: Optimizer

### 3.1 ScipyOptimizer Class
**Location:** `src/optimizers/scipy.py`

```python
class ScipyOptimizer:
    def __init__(self, ctx: AppContext, min_channel_budget=1000):
        # Store config
        
    def optimize(
        self, 
        beta_coefficients: np.ndarray,      # shape (n_channels,)
        alpha_coefficients: np.ndarray,     # shape (n_channels,)
        gamma_coefficients: np.ndarray,     # shape (n_channels,)
        total_budget: float
    ) -> dict:
        """
        Maximize: sum(beta * hill_saturation(allocation, alpha, gamma))
        Subject to: sum(allocation) = total_budget, allocation >= min_per_channel
        
        Input:
          - Coefficients from Bayesian posterior (means)
          - total_budget: total to allocate
        
        Output: dict with keys:
          - "allocation": ndarray (n_channels,) [optimized spend per channel]
          - "objective": float [objective value at optimum]
          - "success": bool [SLSQP converged]
          - "message": str [SLSQP message]
        
        Returns: Schema-validated dict (see test suite)
        """
```

**Test Suite:** `tests/optimizers/test_scipy_optimizer.py`

**Unit Tests:**
- ✓ Hill saturation function correct
- ✓ Budget constraint: sum(allocation) == total_budget
- ✓ Min spend per channel respected
- ✓ Objective is always finite
- ✓ Schema: output dict has required keys

**Integration Tests:**
- ✓ Single channel: allocates entire budget to that channel
- ✓ Two channels with different betas: allocates more to high-beta
- ✓ Saturation effect: diminishing returns modeled correctly
- ✓ Known solution: recovers optimal for toy problems (e.g., linear, no saturation)
- ✓ Scale invariance: same allocations at 1x and 1000x budget scale

**Failure Mode Tests:**
- ✓ Handles negative betas gracefully (shouldn't happen but robust)
- ✓ Handles zero budget (returns zeros)
- ✓ Handles very small total_budget vs min_channel_budget

---

## Phase 4: Integration Layer

### 4.1 Context Management
**Location:** `src/core/context.py` (EXISTING - verify)

**Schema Requirements:**
```python
ctx.state must provide:
  - "raw_df": raw spend + conversions
  - "trace": Bayesian posterior (after model.fit)
  - "posterior_summary": summary DataFrame (after model.fit)
  - "beta_means": Beta coefficients for optimization
  - "alpha_means": Alpha coefficients for optimization
  - "gamma_means": Gamma coefficients for optimization
```

### 4.2 Pipeline Orchestration
**Location:** `src/runner/context_runner.py` (REWRITE)

**Minimal runner:**
```python
def main():
    # 1. Load
    datasource = CSVDataSource(ctx, ...)
    datasource.load_data(...)
    
    # 2. Optional: Apply Adstock (carryover effects)
    adstock = AdstockTransformer(ctx)
    adstocked_df = adstock.apply_transforms(ctx.state.get("raw_df"), channels)
    
    # 3. Fit model (learns saturation + effectiveness)
    model = BayesianMMM(ctx, n_samples=2000, n_tune=1000)
    model.fit(adstocked_df[channels], adstocked_df["conversions"])
    
    # 4. Extract posterior means
    posterior = ctx.state.get("posterior_summary")
    beta_means = posterior.loc["betas", "mean"].values
    alpha_means = posterior.loc["alpha", "mean"].values
    gamma_means = posterior.loc["gamma", "mean"].values
    
    # 5. Optimize
    optimizer = ScipyOptimizer(ctx)
    result = optimizer.optimize(
        beta_coefficients=beta_means,
        alpha_coefficients=alpha_means,
        gamma_coefficients=gamma_means,
        total_budget=total_budget
    )
    
    # 6. Output
    optimized_df = pd.DataFrame({
        "channel": channels,
        "current_spend": current_spend,
        "optimized_spend": result["allocation"],
        "change_pct": (result["allocation"] - current_spend) / current_spend * 100
    })
    optimized_df.to_csv("optimization_output.csv")
    posterior.to_csv("posterior_summary.csv")
```

---

## Data Schemas (Schema Validation Tests)

### Posterior Summary DataFrame
```
Required Columns: mean, sd, hdi_3%, hdi_97%, r_hat, ess_bulk, ess_tail
Required Rows: 
  - alpha[0], alpha[1], ..., alpha[n_channels-1]
  - gamma[0], gamma[1], ..., gamma[n_channels-1]
  - beta[0], beta[1], ..., beta[n_channels-1]
  - intercept
  - sigma
Properties:
  - All numeric columns are finite (no NaN/Inf)
  - r_hat < 1.1 (convergence check)
  - ess_bulk > 400 (effective sample size)
```

### Optimization Result Dict
```
Keys: ["allocation", "objective", "success", "message"]
Types:
  - allocation: ndarray, shape (n_channels,), float64
  - objective: float
  - success: bool
  - message: str
Properties:
  - allocation.sum() ≈ total_budget (within tolerance)
  - objective is finite
  - all allocations >= min_channel_budget
```

---

## Testing Strategy

### 1. Unit Tests (Pure Functions)
- Math correctness
- Edge cases
- Numerical stability

### 2. Schema Validation Tests
- All DataFrame/dict outputs have required columns/keys
- Types are correct
- Values are in expected ranges

### 3. Integration Tests
- End-to-end: load → model → optimize
- Results are sensible (allocation matches effectiveness)

### 4. Scale Tests
- 1x budget, 100x budget, 10000x budget
- 1 channel, 50 channels
- 10 weeks, 500 weeks
- Small spend (thousands), large spend (millions)

### 5. Real-World Data Simulation
- Exponential spend distribution
- Non-stationary trends
- Seasonal patterns
- Missing weeks
- Zero-spend channels

---

## Success Criteria

1. ✓ All tests pass across scales
2. ✓ Optimizer recommends allocations that reflect beta differences (high-beta channels get more)
3. ✓ Model convergence: r_hat < 1.1 across all parameters
4. ✓ Saturation effect present: doubling budget doesn't double output
5. ✓ Production ready: handles any real-world ad spend pattern
6. ✓ No hardcoded values (all data-driven)

---

## Key Principles (NO EXCEPTIONS)

1. **Scale Invariance**: Algorithm works at any spend magnitude
2. **Distribution Agnostic**: Works with any spend distribution (uniform, exponential, etc.)
3. **Data-Driven Priors**: All priors calculated from observed data
4. **Robustness**: Handles edge cases gracefully with clear error messages
5. **Transparency**: Every output validated with schema tests
6. **Production Grade**: Industry-standard, no quick hacks

---

## References

- Google: Jin et al. (2017) - "Bayesian Methods for Media Mix Modeling with Carryover and Shape Effects"
- Google: Chan & Perry (2017) - "Challenges and Opportunities in Media Mix Modeling"
- LightweightMMM: Official Google implementation
- PyMC Documentation & Best Practices
