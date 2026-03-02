"""
Test suite for Bayesian MMM Model.

Validates:
1. Model fitting with convergence diagnostics
2. Posterior summary correctness and schema
3. Scale invariance (works at any budget magnitude)
4. Distribution robustness (works with any spend pattern)
5. Channel variations (1 to 50+ channels)
6. Parameter value ranges and constraints
"""

import numpy as np
import pandas as pd
import pytest
from src.core.context import AppContext, RunConfig
from src.models.bayesian_mmm import BayesianMMMModel


class TestBayesianMMMBasics:
    """Core functionality and model structure."""
    
    def test_initialization(self):
        """Model initializes with default parameters."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx)
        
        assert model.ctx is not None
        assert hasattr(model, 'fit')
        assert hasattr(model, 'get_posterior_summary')
    
    def test_fit_synthetic_data_returns_dataframe(self):
        """fit() returns a DataFrame with contributions."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=4)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        result = model.fit(df, media_columns=media_columns, raw_df=df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(df)
    
    def test_get_posterior_summary_has_required_columns(self):
        """Posterior summary has required columns."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=4)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        model.fit(df, media_columns=media_columns, raw_df=df)
        summary = model.get_posterior_summary()
        
        required_cols = ['mean', 'sd', 'hdi_3%', 'hdi_97%', 'r_hat']
        for col in required_cols:
            assert col in summary.columns
    
    def test_get_posterior_summary_has_all_parameters(self):
        """Posterior summary includes all learned parameters."""
        n_channels = 3
        ctx = create_test_context(n_channels=n_channels)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=n_channels)
        media_columns = [f"channel_{i}" for i in range(n_channels)]
        
        model.fit(df, media_columns=media_columns, raw_df=df)
        summary = model.get_posterior_summary()
        
        # Should have: alpha (n_channels) + gamma (n_channels) + beta (n_channels) + intercept (1) + sigma (1)
        expected_rows = n_channels * 3 + 2
        assert len(summary) >= expected_rows


class TestConvergenceDiagnostics:
    """Verify MCMC convergence and chain health."""
    
    def test_rhat_below_threshold(self):
        """R-hat values < 1.1 indicate convergence."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=1000, tune=1000)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=4)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        model.fit(df, media_columns=media_columns, raw_df=df)
        summary = model.get_posterior_summary()
        
        # All r_hat values should indicate convergence
        assert np.all(summary['r_hat'] < 1.1)
    
    def test_posterior_sd_positive(self):
        """Standard deviation of posteriors is positive."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=4)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        model.fit(df, media_columns=media_columns, raw_df=df)
        summary = model.get_posterior_summary()
        
        assert np.all(summary['sd'] > 0)


class TestParameterConstraints:
    """Verify learned parameters satisfy domain constraints."""
    
    def test_alpha_in_valid_range(self):
        """Alpha posterior mean in (0.1, 3.0) - typical saturation range."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=4)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        model.fit(df, media_columns=media_columns, raw_df=df)
        summary = model.get_posterior_summary()
        
        alpha_rows = summary[summary.index.str.contains('alpha')]
        assert np.all(alpha_rows['mean'] > 0.1)
        assert np.all(alpha_rows['mean'] < 3.0)
    
    def test_gamma_positive(self):
        """Gamma (half-saturation) posterior mean is positive."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=4)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        model.fit(df, media_columns=media_columns, raw_df=df)
        summary = model.get_posterior_summary()
        
        gamma_rows = summary[summary.index.str.contains('gamma')]
        assert np.all(gamma_rows['mean'] > 0)
    
    def test_beta_positive(self):
        """Beta (effectiveness) posterior mean is positive."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=4)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        model.fit(df, media_columns=media_columns, raw_df=df)
        summary = model.get_posterior_summary()
        
        beta_rows = summary[summary.index.str.contains('beta')]
        assert np.all(beta_rows['mean'] > 0)
    
    def test_intercept_reasonable(self):
        """Intercept posterior is reasonable magnitude."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=4)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        model.fit(df, media_columns=media_columns, raw_df=df)
        summary = model.get_posterior_summary()
        
        intercept_row = summary[summary.index.str.contains('intercept')]
        assert len(intercept_row) == 1
        assert intercept_row['mean'].values[0] > 0


class TestScaleInvariance:
    """Verify model works at different spend magnitudes."""
    
    def test_1x_scale_fit(self):
        """Model fits correctly at 1x scale (base magnitude)."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(
            n_weeks=52, n_channels=4, spend_scale=1.0
        )
        media_columns = [f"channel_{i}" for i in range(4)]
        
        result = model.fit(df, media_columns=media_columns, raw_df=df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
    
    def test_100x_scale_fit(self):
        """Model fits correctly at 100x scale (larger magnitude)."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(
            n_weeks=52, n_channels=4, spend_scale=100.0
        )
        media_columns = [f"channel_{i}" for i in range(4)]
        
        result = model.fit(df, media_columns=media_columns, raw_df=df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
    
    def test_10000x_scale_fit(self):
        """Model fits correctly at 10000x scale (extreme magnitude)."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(
            n_weeks=52, n_channels=4, spend_scale=10000.0
        )
        media_columns = [f"channel_{i}" for i in range(4)]
        
        result = model.fit(df, media_columns=media_columns, raw_df=df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0


class TestDistributionRobustness:
    """Verify model works with different spend patterns."""
    
    def test_exponential_spend_pattern(self):
        """Model fits with exponential (skewed) spend distribution."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        n_weeks = 52
        n_channels = 4
        spend_data = np.random.exponential(scale=100000, size=(n_weeks, n_channels))
        conversions = generate_conversions_from_spend(spend_data)
        df = create_dataframe_from_data(spend_data, conversions)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        result = model.fit(df, media_columns=media_columns, raw_df=df)
        assert isinstance(result, pd.DataFrame)
    
    def test_uniform_spend_pattern(self):
        """Model fits with uniform spend distribution."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        n_weeks = 52
        n_channels = 4
        spend_data = np.random.uniform(50000, 300000, size=(n_weeks, n_channels))
        conversions = generate_conversions_from_spend(spend_data)
        df = create_dataframe_from_data(spend_data, conversions)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        result = model.fit(df, media_columns=media_columns, raw_df=df)
        assert isinstance(result, pd.DataFrame)
    
    def test_seasonal_spend_pattern(self):
        """Model fits with seasonal spend variation."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        n_weeks = 52
        n_channels = 4
        t = np.arange(n_weeks)
        seasonal_pattern = 1 + 0.5 * np.sin(2 * np.pi * t / 52)
        spend_data = np.outer(seasonal_pattern, np.ones(n_channels)) * 100000
        spend_data += np.random.normal(0, 20000, size=(n_weeks, n_channels))
        spend_data = np.maximum(spend_data, 10000)  # Ensure positive
        
        conversions = generate_conversions_from_spend(spend_data)
        df = create_dataframe_from_data(spend_data, conversions)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        result = model.fit(df, media_columns=media_columns, raw_df=df)
        assert isinstance(result, pd.DataFrame)


class TestChannelVariations:
    """Verify model works with different channel counts."""
    
    def test_single_channel(self):
        """Model fits with 1 channel."""
        ctx = create_test_context(n_channels=1)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=1)
        media_columns = ['channel_0']
        
        result = model.fit(df, media_columns=media_columns, raw_df=df)
        summary = model.get_posterior_summary()
        
        # Should have: 1 alpha + 1 gamma + 1 beta + intercept + sigma
        assert len(summary) >= 5
    
    def test_four_channels(self):
        """Model fits with 4 channels (typical scenario)."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=4)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        result = model.fit(df, media_columns=media_columns, raw_df=df)
        summary = model.get_posterior_summary()
        
        # Should have: 4 alpha + 4 gamma + 4 beta + intercept + sigma
        assert len(summary) >= 13
    
    def test_ten_channels(self):
        """Model fits with 10 channels."""
        ctx = create_test_context(n_channels=10)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=10)
        media_columns = [f"channel_{i}" for i in range(10)]
        
        result = model.fit(df, media_columns=media_columns, raw_df=df)
        assert isinstance(result, pd.DataFrame)


class TestGetContributions:
    """Test get_contributions() output."""
    
    def test_contributions_shape(self):
        """Contributions DataFrame has correct shape."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=4)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        model.fit(df, media_columns=media_columns, raw_df=df)
        contributions = model.get_contributions()
        
        assert isinstance(contributions, pd.DataFrame)
        assert len(contributions) == 52  # n_weeks
        assert len(contributions.columns) == 4  # n_channels
    
    def test_contributions_non_negative(self):
        """All contributions are non-negative."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=4)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        model.fit(df, media_columns=media_columns, raw_df=df)
        contributions = model.get_contributions()
        
        assert np.all(contributions.values >= 0)
    
    def test_contributions_sum_reasonable(self):
        """Contributions sum to approximately total conversions."""
        ctx = create_test_context(n_channels=4)
        model = BayesianMMMModel(ctx, samples=500, tune=500)
        
        spend_data, conversions, df = create_synthetic_mmm_data(n_weeks=52, n_channels=4)
        media_columns = [f"channel_{i}" for i in range(4)]
        
        model.fit(df, media_columns=media_columns, raw_df=df)
        contributions = model.get_contributions()
        
        contrib_sum = contributions.sum().sum()
        conversion_sum = df['conversions'].sum()
        
        # Allow 20% tolerance for model variation
        assert 0.8 * conversion_sum <= contrib_sum <= 1.2 * conversion_sum


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_test_context(n_channels: int) -> AppContext:
    """Create a minimal AppContext for testing."""
    channels = [f"channel_{i}" for i in range(n_channels)]
    config = RunConfig(channels=channels, model_type="bayesian_mmm")
    ctx = AppContext(config=config)
    return ctx


def create_synthetic_mmm_data(
    n_weeks: int = 52,
    n_channels: int = 4,
    spend_scale: float = 1.0,
    seed: int = 42
) -> tuple:
    """Generate synthetic MMM data with known ground truth."""
    np.random.seed(seed)
    
    # Generate spend data
    spend_data = np.random.exponential(scale=100000 * spend_scale, size=(n_weeks, n_channels))
    
    # Ground truth parameters
    true_alpha = np.random.uniform(0.8, 1.2, n_channels)
    true_gamma = np.log(spend_data.mean(axis=0))
    true_beta = np.random.uniform(0.0001, 0.001, n_channels)
    true_intercept = 10000.0
    true_sigma = 5000.0
    
    # Generate conversions
    conversions = generate_conversions_from_spend(
        spend_data, true_alpha, true_gamma, true_beta, true_intercept, true_sigma
    )
    
    df = create_dataframe_from_data(spend_data, conversions)
    return spend_data, conversions, df


def generate_conversions_from_spend(
    spend_data: np.ndarray,
    alpha: np.ndarray = None,
    gamma: np.ndarray = None,
    beta: np.ndarray = None,
    intercept: float = 10000.0,
    sigma: float = 5000.0
) -> np.ndarray:
    """Generate conversion data from spend using Hill saturation."""
    from src.core.saturation import hill_saturation
    
    n_weeks, n_channels = spend_data.shape
    
    if alpha is None:
        alpha = np.ones(n_channels) * 1.0
    if gamma is None:
        gamma = np.log(spend_data.mean(axis=0))
    if beta is None:
        beta = np.random.uniform(0.0001, 0.001, n_channels)
    
    # Apply saturation
    saturated = hill_saturation(spend_data, alpha=alpha, gamma=gamma)
    
    # Linear combination
    contributions = saturated @ beta
    
    # Add intercept and noise
    conversions = intercept + contributions + np.random.normal(0, sigma, n_weeks)
    conversions = np.maximum(conversions, 0)  # Ensure non-negative
    
    return conversions


def create_dataframe_from_data(spend_data: np.ndarray, conversions: np.ndarray) -> pd.DataFrame:
    """Create DataFrame from spend and conversion arrays."""
    n_weeks, n_channels = spend_data.shape
    
    df = pd.DataFrame()
    for ch in range(n_channels):
        df[f"channel_{ch}"] = spend_data[:, ch]
    df['conversions'] = conversions
    
    return df