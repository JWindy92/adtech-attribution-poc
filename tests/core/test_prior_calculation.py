"""
Test suite for scale-adaptive gamma prior calculation.

Validates:
1. Correct mathematical computation
2. Scale invariance (works at any budget magnitude)
3. Distribution robustness (works with any spend pattern)
4. Edge cases (single week, many channels)
5. Error handling (invalid inputs)
"""

import numpy as np
import pytest
from src.core.prior_calculation import calculate_gamma_prior


class TestGammaPriorBasics:
    """Core functionality and correctness."""
    
    def test_returns_correct_shapes(self):
        """Output shapes match input."""
        spend_data = np.array([
            [100000, 200000, 150000],
            [120000, 180000, 160000],
            [110000, 210000, 140000],
        ])  # (3 weeks, 3 channels)
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert gamma_mu.shape == (3,)
        assert isinstance(gamma_sigma, (float, np.floating))
    
    def test_gamma_mu_equals_log_mean_spend(self):
        """gamma_mu[ch] = log(mean_spend[ch])."""
        spend_data = np.array([
            [100000, 200000],
            [150000, 300000],
            [200000, 250000],
        ])
        
        gamma_mu, _ = calculate_gamma_prior(spend_data)
        
        expected_mu = np.log(spend_data.mean(axis=0))
        np.testing.assert_array_almost_equal(gamma_mu, expected_mu)
    
    def test_gamma_sigma_is_one(self):
        """gamma_sigma is always 1.0 (industry standard)."""
        spend_data = np.random.exponential(scale=100000, size=(52, 4))
        
        _, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert gamma_sigma == 1.0
    
    def test_gamma_mu_values_sign(self):
        """gamma_mu values are finite and reasonable."""
        spend_data = np.array([
            [1000, 100000, 1000000],
            [2000, 150000, 1500000],
            [1500, 120000, 1200000],
        ])
        
        gamma_mu, _ = calculate_gamma_prior(spend_data)
        
        # All values should be real log values
        assert np.all(np.isfinite(gamma_mu))
        # Larger spend channels should have larger log values
        assert gamma_mu[0] < gamma_mu[1] < gamma_mu[2]


class TestScaleInvariance:
    """Verify scale-adaptive property: works at any magnitude."""
    
    def test_1x_and_1000x_scale_differ_by_log_multiplier(self):
        """Scaling all spend by K increases log-prior by log(K)."""
        spend_data_1x = np.array([
            [100000, 200000],
            [150000, 250000],
            [120000, 180000],
        ])
        
        spend_data_1000x = spend_data_1x * 1000
        
        mu_1x, _ = calculate_gamma_prior(spend_data_1x)
        mu_1000x, _ = calculate_gamma_prior(spend_data_1000x)
        
        expected_diff = np.log(1000)
        actual_diff = mu_1000x - mu_1x
        
        np.testing.assert_array_almost_equal(actual_diff, [expected_diff, expected_diff])
    
    def test_tiny_scale(self):
        """Works correctly at very small budget scale."""
        spend_data = np.array([
            [0.1, 0.2],
            [0.15, 0.25],
            [0.12, 0.18],
        ])  # Spend in dollars (very small)
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert np.all(np.isfinite(gamma_mu))
        assert gamma_sigma == 1.0
        # Means should be in log space of small numbers (negative logs)
        assert np.all(gamma_mu < 0)
    
    def test_huge_scale(self):
        """Works correctly at very large budget scale."""
        spend_data = np.array([
            [1e10, 2e10],
            [1.5e10, 2.5e10],
            [1.2e10, 1.8e10],
        ])  # Spend in billions
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert np.all(np.isfinite(gamma_mu))
        assert gamma_sigma == 1.0
        # Means should be in log space of large numbers (positive logs)
        assert np.all(gamma_mu > 20)
    
    def test_100x_scale_increase(self):
        """Scaling by 100 increases mu by log(100)."""
        base_spend = np.array([[1000, 5000], [2000, 6000]])
        scaled_spend = base_spend * 100
        
        mu_base, _ = calculate_gamma_prior(base_spend)
        mu_scaled, _ = calculate_gamma_prior(scaled_spend)
        
        expected_increase = np.log(100)
        actual_increase = mu_scaled - mu_base
        
        np.testing.assert_array_almost_equal(actual_increase, [expected_increase, expected_increase])


class TestChannelVariation:
    """Verify handling of different channel characteristics."""
    
    def test_varying_channel_magnitudes(self):
        """Handles channels with very different spend levels."""
        spend_data = np.array([
            [1000, 1000000, 100000000],      # 3 orders of magnitude difference
            [1500, 1200000, 120000000],
            [800, 900000, 80000000],
        ])
        
        gamma_mu, _ = calculate_gamma_prior(spend_data)
        
        # Means should reflect the magnitude differences
        assert gamma_mu[0] < gamma_mu[1] < gamma_mu[2]
        
        # Differences should be approximately log(10) ≈ 2.3
        assert np.isclose(gamma_mu[1] - gamma_mu[0], np.log(1000), rtol=0.01)
        assert np.isclose(gamma_mu[2] - gamma_mu[1], np.log(100), rtol=0.01)
    
    def test_high_variance_channels(self):
        """Handles channels with high spend variance."""
        spend_data = np.array([
            [10000, 500000],     # Channel 0: low, Channel 1: high
            [500000, 600000],    # Flipped: high, even higher
            [5000, 100000],      # Back to low/high
        ])
        
        gamma_mu, _ = calculate_gamma_prior(spend_data)
        
        # Mean should still be in reasonable range (log space)
        assert np.all(np.isfinite(gamma_mu))


class TestEdgeCases:
    """Handle boundary conditions gracefully."""
    
    def test_single_channel(self):
        """Works with just one channel."""
        spend_data = np.array([
            [100000],
            [150000],
            [120000],
        ])
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert gamma_mu.shape == (1,)
        assert gamma_sigma == 1.0
        assert np.isclose(gamma_mu[0], np.log(123333.33), rtol=0.01)
    
    def test_many_channels(self):
        """Works with 100+ channels (enterprise scale)."""
        n_channels = 150
        spend_data = np.random.exponential(scale=100000, size=(52, n_channels))
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert gamma_mu.shape == (n_channels,)
        assert gamma_sigma == 1.0
        assert np.all(np.isfinite(gamma_mu))
    
    def test_exactly_two_weeks(self):
        """Works with minimum allowed data (2 weeks)."""
        spend_data = np.array([
            [100000, 200000],
            [150000, 250000],
        ])
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert gamma_mu.shape == (2,)
        expected_mu = np.log([125000, 225000])
        np.testing.assert_array_almost_equal(gamma_mu, expected_mu)
    
    def test_many_weeks(self):
        """Works with long historical periods."""
        spend_data = np.random.exponential(scale=100000, size=(500, 4))
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert gamma_mu.shape == (4,)
        assert np.all(np.isfinite(gamma_mu))


class TestErrorHandling:
    """Verify proper error handling."""
    
    def test_negative_spend_raises_error(self):
        """Negative spend values should raise ValueError."""
        spend_data = np.array([
            [100000, 200000],
            [-50000, 250000],  # Negative!
            [120000, 180000],
        ])
        
        with pytest.raises(ValueError, match="must be non-negative"):
            calculate_gamma_prior(spend_data)
    
    def test_all_zero_channel_raises_error(self):
        """Channel with all zero spend should raise ValueError."""
        spend_data = np.array([
            [0, 200000],
            [0, 250000],
            [0, 180000],
        ])
        
        with pytest.raises(ValueError, match="zero total spend"):
            calculate_gamma_prior(spend_data)
    
    def test_single_week_raises_error(self):
        """Less than 2 weeks of data should raise ValueError."""
        spend_data = np.array([[100000, 200000]])  # Only 1 week
        
        with pytest.raises(ValueError, match="≥ 2 weeks"):
            calculate_gamma_prior(spend_data)
    
    def test_wrong_dimension_raises_error(self):
        """1D input should raise ValueError."""
        spend_data = np.array([100000, 200000, 150000])
        
        with pytest.raises(ValueError, match="2D"):
            calculate_gamma_prior(spend_data)
    
    def test_3d_input_raises_error(self):
        """3D input should raise ValueError."""
        spend_data = np.random.exponential(scale=100000, size=(52, 4, 2))
        
        with pytest.raises(ValueError, match="2D"):
            calculate_gamma_prior(spend_data)


class TestRealWorldData:
    """Test with realistic patterns."""
    
    def test_exponential_spend_distribution(self):
        """Realistic: some channels get much more spent than others."""
        np.random.seed(42)
        spend_data = np.random.exponential(scale=100000, size=(52, 4))
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert gamma_mu.shape == (4,)
        assert gamma_sigma == 1.0
        assert np.all(np.isfinite(gamma_mu))
    
    def test_bimodal_seasonal_spend(self):
        """Realistic: seasonal spikes in spending."""
        np.random.seed(42)
        spend_data = np.concatenate([
            np.random.normal(100000, 10000, size=(26, 2)),  # Low season
            np.random.normal(300000, 30000, size=(26, 2)),  # High season
        ])
        spend_data = np.abs(spend_data)  # Ensure non-negative
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert gamma_mu.shape == (2,)
        assert np.all(np.isfinite(gamma_mu))
    
    def test_four_channel_sample_mmm_data(self):
        """Realistic 4-channel MMM scenario."""
        np.random.seed(42)
        # Different channels have different typical spend levels
        ctv = np.random.exponential(scale=50000, size=52)
        social = np.random.exponential(scale=200000, size=52)
        search = np.random.exponential(scale=150000, size=52)
        linear_tv = np.random.exponential(scale=80000, size=52)
        
        spend_data = np.column_stack([ctv, social, search, linear_tv])
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert gamma_mu.shape == (4,)
        # Social should have highest mu (highest typical spend)
        assert gamma_mu[1] > gamma_mu[0]
        assert gamma_mu[1] > gamma_mu[2]
        assert gamma_mu[1] > gamma_mu[3]
        
        assert np.all(np.isfinite(gamma_mu))
        assert gamma_sigma == 1.0


class TestDistributionRobustness:
    """Verify function works with different spend distributions."""
    
    def test_uniform_distribution(self):
        """Works with uniform spend distribution."""
        spend_data = np.random.uniform(50000, 200000, size=(52, 3))
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert gamma_mu.shape == (3,)
        assert np.all(np.isfinite(gamma_mu))
    
    def test_lognormal_distribution(self):
        """Works with log-normal distribution (naturally skewed)."""
        spend_data = np.random.lognormal(mean=11, sigma=0.5, size=(52, 3))
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        assert gamma_mu.shape == (3,)
        assert np.all(np.isfinite(gamma_mu))
    
    def test_constant_spend(self):
        """Works when channel has constant spend (no variance)."""
        spend_data = np.array([
            [100000, 200000],
            [100000, 200000],
            [100000, 200000],
        ])  # Constant spend
        
        gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        
        expected_mu = np.log([100000, 200000])
        np.testing.assert_array_almost_equal(gamma_mu, expected_mu)