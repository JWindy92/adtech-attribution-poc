import pandas as pd
import numpy as np
from typing import List
from src.core.interfaces import AttributionModel
from src.core.context import AppContext

try:
    import pymc as pm
    import arviz as az

    PYMC_AVAILABLE = True
except ImportError:
    PYMC_AVAILABLE = False

class BayesianMMMModel(AttributionModel):
    def __init__(self, ctx: AppContext, samples: int = 2000, tune: int = 1000, target_accept: float = 0.9):
        self.ctx = ctx
        self.samples = samples
        self.tune = tune
        self.target_accept = target_accept
        
        # Will be populated by fit()
        self.model = None
        self.trace = None
        self.posterior_summary = None
        self.contributions = None
        
        # Metadata
        self.media_columns = None
        self.spend_data = None
        self.conversions = None

    def fit(self, df: pd.DataFrame, media_columns: List[str], raw_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Fit Bayesian MMM model to data using MCMC sampling.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with media spend columns and conversions column
        media_columns : List[str]
            Names of columns containing media spend data
        raw_df : pd.DataFrame, optional
            Raw spending data (unused in current implementation)
        
        Returns
        -------
        pd.DataFrame
            Weekly contributions by channel (n_weeks x n_channels)
        """
        if not PYMC_AVAILABLE:
            raise RuntimeError("PyMC not available - install with: pip install pymc")
        
        # Store metadata
        self.media_columns = media_columns
        n_channels = len(media_columns)
        
        # Extract spend and conversions
        spend_data = df[media_columns].values  # shape: (n_weeks, n_channels)
        conversions = df['conversions'].values  # shape: (n_weeks,)
        
        self.spend_data = spend_data
        self.conversions = conversions
        
        # Calculate data-driven gamma priors
        from src.core.prior_calculation import calculate_gamma_prior
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        # Build PyMC model
        with pm.Model() as model:
            # Priors for saturation parameters (per channel)
            alpha = pm.Uniform('alpha', lower=0.1, upper=3.0, shape=n_channels)
            gamma = pm.Normal('gamma', mu=gamma_mu, sigma=gamma_sigma, shape=n_channels)
            
            # Priors for effectiveness (per channel)
            beta = pm.Exponential('beta', lam=0.01, shape=n_channels)
            
            # Prior for baseline
            intercept = pm.Normal('intercept', mu=conversions.mean(), sigma=conversions.std())
            
            # Likelihood noise
            sigma = pm.HalfNormal('sigma', sigma=conversions.std())
            
            # Apply Hill saturation transformation
            from src.core.saturation import hill_saturation
            saturated = hill_saturation(spend_data, alpha=alpha, gamma=gamma)  # shape: (n_weeks, n_channels)
            
            # Linear combination: dot product of saturated spend and beta
            mu = intercept + pm.math.dot(saturated, beta)  # shape: (n_weeks,)
            
            # Likelihood
            observed = pm.Normal('observed', mu=mu, sigma=sigma, observed=conversions)
            
            # MCMC sampling
            self.trace = pm.sample(
                draws=self.samples,
                tune=self.tune,
                target_accept=self.target_accept,
                return_inferencedata=True,
                progressbar=True,
                random_seed=42
            )
        
        self.model = model
        
        # Calculate posterior mean contributions per channel per week
        posterior_alpha = self.trace.posterior['alpha'].values.mean(axis=(0, 1))
        posterior_gamma = self.trace.posterior['gamma'].values.mean(axis=(0, 1))
        posterior_beta = self.trace.posterior['beta'].values.mean(axis=(0, 1))
        posterior_intercept = self.trace.posterior['intercept'].values.mean(axis=(0, 1))
        
        saturated_posterior = hill_saturation(spend_data, alpha=posterior_alpha, gamma=posterior_gamma)
        contributions = saturated_posterior * posterior_beta  # (n_weeks, n_channels)
        
        intercept_per_channel = posterior_intercept / n_channels
        total_contributions = contributions + intercept_per_channel

        contribution_columns = [f"{col}_contribution" for col in media_columns]
        contribution_df = pd.DataFrame(
            total_contributions,
            columns=contribution_columns
        )
        
        # Add contribution columns to the ORIGINAL dataframe
        output_df = df.copy()
        for i, col in enumerate(contribution_columns):
            output_df[col] = contribution_df[col]
        
        self.contributions = output_df[contribution_columns] 
        
        # Calculate posterior summary for storage
        self.posterior_summary = az.summary(self.trace)
        
        return output_df

    def get_contributions(self) -> pd.DataFrame:
        """
        Get weekly channel contributions (output of fit).
        
        Returns
        -------
        pd.DataFrame
            Shape: (n_weeks, n_channels)
            Values: Mean posterior contribution of each channel each week
        """
        if self.contributions is None:
            raise RuntimeError("Model not fitted yet. Call fit() first.")
        return self.contributions

    def get_posterior_summary(self) -> pd.DataFrame:
        """
        Get posterior summary with convergence diagnostics.
        
        Returns
        -------
        pd.DataFrame
            Posterior summary from arviz with columns: mean, sd, hdi_low, hdi_high, r_hat, etc.
        """
        if self.posterior_summary is None:
            raise RuntimeError("Model not fitted yet. Call fit() first.")
        return self.posterior_summary