# Bayesian Saturation Parameter Fitting: Correct Approach

## Problem Statement

**Current (incorrect) approach:**
1. Pre-fit saturation parameters (alpha, gamma) from historical spend data using scipy curve_fit
2. Apply saturation transformation to create features: `spend_saturated = f(spend; alpha, gamma)`
3. Fit Bayesian model on saturated features, learning only beta coefficients
4. Use fixed alpha/gamma for optimization (extrapolates parameters outside their fitted range)

**Issue:** Fitting alpha/gamma on historical range (0-300K) then applying them at optimization scale (6.4M) is mathematically invalid. The parameters were optimized for one data range and don't reliably model a completely different range.

---

## Correct Approach: Integrate Parameters into Bayesian Model

**Principle:** Alpha and gamma are **unknown parameters** that should be learned alongside betas through Bayesian inference.

### Architecture Changes

**1. Bayesian Model Structure**
```
Instead of:
  raw_spend → saturate(alpha_fit, gamma_fit) → saturated_spend → fit betas

Do this:
  raw_spend → saturate(alpha, gamma) → betas → predicted_conversions
                     ↑        ↑         ↑
            learned from data (MCMC sampling)
```

**2. Parameters to Learn (via MCMC)**
- `alpha[channel]` - Saturation curve steepness (per channel)
- `gamma[channel]` - Half-saturation point (per channel)  
- `beta[channel]` - Channel effectiveness (per channel, as before)
- `intercept` - Baseline conversions (as before)
- `sigma` - Model noise (as before)

**3. Priors (Critical for Stability)**

Since we're now fitting alpha/gamma with limited data, **informative priors** are essential:

```python
# Example priors (these need domain input):
alpha ~ Uniform(0.1, 3.0)      # Most channels are relatively linear to moderately curved
gamma ~ LogNormal(mu, sigma)   # Half-saturation tends to be log-distributed
                                # Could be center on: industry benchmark, 
                                # expected budget * some percentage, etc.

beta ~ Normal(0, 1)             # Mildly informative (as currently)
```

**Key decision:** What should `gamma` prior be centered on?
- Option A: Industry benchmark (e.g., "typical half-saturation is 30% of max budget")
- Option B: Expected optimization budget (e.g., "we plan to optimize with 6.4M per channel")
- Option C: Historical data plus multiplier (e.g., "fitted gamma * 10", but principled)

---

## Implementation Steps

### Step 1: Modify Bayesian Model (`src/models/bayesian_mmm.py`)

**Add these parameters to the PyMC model:**
- For each channel, add `alpha` and `gamma` with priors
- Embed Hill saturation transformation **inside** the model
- Replace saturated features with raw features + on-the-fly saturation

**Pseudo-code:**
```python
with pm.Model() as model:
    # Learn saturation parameters
    alpha = pm.Uniform('alpha', lower=0.1, upper=3.0, shape=n_channels)
    gamma = pm.LogNormal('gamma', mu=..., sigma=..., shape=n_channels)
    
    # Learn effectiveness
    beta = pm.Normal('beta', mu=0, sigma=1, shape=n_channels)
    
    # Apply saturation inside model
    saturation = spend_raw ** alpha / (gamma ** alpha + spend_raw ** alpha)
    
    # Likelihood
    mu = intercept + (saturation * beta).sum(axis=1)
    likelihood = pm.Normal('y', mu=mu, sigma=sigma, observed=conversions)
```

### Step 2: Data Pipeline Changes

**Old flow:**
```
raw_data → SaturationTransformer.apply_saturation() → saturated_features 
         → Bayesian model fits betas
```

**New flow:**
```
raw_data → Bayesian model:
             - Receives raw_df with raw spend columns
             - Learns alpha, gamma, beta simultaneously
             - Computes saturation internally
```

**Implication:** 
- Remove saturation transformation from pre-processing
- Pass raw spend to model
- Model now handles the saturation math

### Step 3: Priors Discussion

**You need to decide:**
1. **Alpha prior:** Uniform(0.1, 3)? Based on industry data?
2. **Gamma prior:** 
   - What's your belief about half-saturation points before seeing data?
   - Should it be different per channel?
   - Should it center around expected optimization budget?

### Step 4: Optimization Remains the Same

Good news: Optimizer step (`scipy.optimize`) stays identical. Now it uses:
- Alpha, gamma learned from Bayesian posterior
- Betas learned from Bayesian posterior
- These are now credible (they were fit to broader data range)

---

## Why This Solves the Problem

1. **Principled extrapolation:** Alpha/gamma are learned to fit **all available data variability**, not constrained to historical range

2. **Uncertainty quantification:** Bayesian posterior gives credible intervals on parameters—you know how confident you should be about extrapolation

3. **Coherent inference:** Everything (saturation + effectiveness) learned jointly—no separate fitting→extrapolation problem

4. **Priors handle beliefs:** If you have industry knowledge ("channels rarely saturate below 40% of budget"), that goes into priors, not magic multipliers

---

## Caveats & Questions

- **Data requirement:** With only 52 weeks of data, fitting 8 parameters (2 alpha + 2 gamma + 4 betas) is tight. Strong priors essential.
- **Identifiability:** Alpha and gamma are somewhat correlated—might need hierarchical structure
- **Computational cost:** More parameters = more MCMC sampling time
- **Prior sensitivity:** Results will depend on chosen priors more than with pre-fitted params

---

## References

- Google: "Bayesian Methods for Media Mix Modeling with Carryover and Shape Effects" (Jin et al. 2017)
- Google: "Challenges and Opportunities in Media Mix Modeling" (Chan & Perry 2017)
- LightweightMMM: Official Google implementation (fits saturation params inside Bayesian model)
