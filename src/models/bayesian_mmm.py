import pandas as pd
import numpy as np
from typing import List
from src.core.interfaces import AttributionModel

try:
    import pymc as pm
    import arviz as az
    PYMC_AVAILABLE = True
except ImportError:
    PYMC_AVAILABLE = False


class BayesianMMMModel(AttributionModel):
    def __init__(self, samples=2000, tune=1000, target_accept=0.9):
        self.metrics = None
        self.trace = None
        self.model = None
        self.samples = samples
        self.tune = tune
        self.target_accept = target_accept
    
    def fit(self, df: pd.DataFrame, media_columns: List[str], raw_df: pd.DataFrame = None) -> pd.DataFrame:
        if not PYMC_AVAILABLE:
            raise ImportError("PyMC is required for Bayesian MMM. Install with: pip install pymc")
        
        y = df['conversions'].values
        X = df[media_columns].values
        n_channels = len(media_columns)
        
        if raw_df is None:
            raw_df = df
        
        with pm.Model() as self.model:
            intercept = pm.Normal('intercept', mu=y.mean(), sigma=y.std())
            
            betas = pm.HalfNormal('betas', sigma=1, shape=n_channels)
            
            sigma = pm.HalfNormal('sigma', sigma=y.std())
            
            mu = intercept + pm.math.dot(X, betas)
            
            likelihood = pm.Normal('conversions', mu=mu, sigma=sigma, observed=y)
            
            self.trace = pm.sample(
                draws=self.samples,
                tune=self.tune,
                target_accept=self.target_accept,
                return_inferencedata=True,
                progressbar=False
            )
        
        beta_means = self.trace.posterior['betas'].mean(dim=['chain', 'draw']).values
        
        total_spend = raw_df[media_columns].sum()
        contributions = beta_means * total_spend.values
        total_attributed = contributions.sum()
        
        attribution_pct = (contributions / total_attributed) * 100 if total_attributed > 0 else np.zeros(n_channels)
        attributed_conversions = (contributions / total_attributed) * df['conversions'].sum() if total_attributed > 0 else np.zeros(n_channels)
        cost_per_conversion = total_spend.values / attributed_conversions
        cost_per_conversion = np.where(attributed_conversions > 0, cost_per_conversion, np.inf)
        
        self.metrics = pd.DataFrame({
            'channel': media_columns,
            'total_spend': total_spend.values,
            'attribution_pct': attribution_pct,
            'attributed_conversions': attributed_conversions,
            'cost_per_conversion': cost_per_conversion,
            'beta_coefficient': beta_means
        })
        
        return self.metrics
    
    def get_contributions(self) -> pd.DataFrame:
        return self.metrics
    
    def get_posterior_summary(self) -> pd.DataFrame:
        if self.trace is None:
            return None
        return az.summary(self.trace, var_names=['betas', 'intercept'])
