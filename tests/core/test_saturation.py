"""
Comprehensive test suite for Hill saturation function.

Validates:
1. Mathematical correctness at known points
2. Edge cases (zero, infinity, boundary values)
3. Numerical stability (extremely large/small values)
4. Shape preservation and broadcasting
5. Error handling for invalid inputs
"""

import numpy as np
import pytest
from src.core.saturation import hill_saturation


class TestHillSaturationBasics:
    """Core mathematical properties."""
    
    def test_zero_spend_gives_zero_saturation(self):
        """At zero spend, saturation should be zero."""
        result = hill_saturation(0, alpha=1.0, gamma=100)
        assert result == 0.0
    
    def test_saturation_at_gamma_is_half(self):
        """At spend=gamma, saturation should be 0.5 for any alpha."""
        gamma = 150.0
        for alpha in [0.5, 1.0, 1.5, 2.0, 3.0]:
            result = hill_saturation(gamma, alpha=alpha, gamma=gamma)
            assert np.isclose(result, 0.5, rtol=1e-10)
    
    def test_linear_case_alpha_one(self):
        """When alpha=1 (linear), saturation = spend / (gamma + spend)."""
        gamma = 100.0
        spend = 50.0
        result = hill_saturation(spend, alpha=1.0, gamma=gamma)
        expected = spend / (gamma + spend)
        assert np.isclose(result, expected)
    
    def test_saturation_monotonic_increasing(self):
        """Saturation increases with spend."""
        alpha = 1.0
        gamma = 100.0
        spends = np.array([0, 10, 50, 100, 500, 1000, 10000])
        saturations = hill_saturation(spends, alpha=alpha, gamma=gamma)
        
        # Check monotonic increase
        assert np.all(np.diff(saturations) >= 0)
    
    def test_saturation_bounded_between_zero_one(self):
        """Saturation is always in [0, 1]."""
        alpha = 1.5
        gamma = 200.0
        spends = np.array([0, 1, 10, 100, 1000, 1e6, 1e12])
        saturations = hill_saturation(spends, alpha=alpha, gamma=gamma)
        
        assert np.all(saturations >= 0.0)
        assert np.all(saturations <= 1.0)
    
    def test_saturation_asymptotic_to_one(self):
        """As spend → ∞, saturation → 1."""
        alpha = 1.0
        gamma = 100.0
        large_spend = 1e10
        result = hill_saturation(large_spend, alpha=alpha, gamma=gamma)
        
        assert result > 0.9999
        assert result < 1.0


class TestShapeAndBroadcasting:
    """Verify output shapes match input patterns."""
    
    def test_scalar_inputs_return_scalar(self):
        """Scalar spend, alpha, gamma → scalar output."""
        result = hill_saturation(100.0, alpha=1.0, gamma=150.0)
        assert isinstance(result, (float, np.floating))
        assert np.isscalar(result) or result.shape == ()
    
    def test_array_spend_scalar_params(self):
        """Array spend, scalar params → same shape array."""
        spend = np.array([10, 50, 100, 500])
        result = hill_saturation(spend, alpha=1.0, gamma=100.0)
        
        assert result.shape == spend.shape
        assert result.dtype == np.float64
    
    def test_2d_spend_array(self):
        """2D spend array (weeks x channels) handled correctly."""
        spend = np.array([[100, 200], [150, 250], [50, 300]])  # (3, 2)
        alpha = 1.0
        gamma = 100.0
        result = hill_saturation(spend, alpha=alpha, gamma=gamma)
        
        assert result.shape == (3, 2)
        assert np.all(result >= 0)
        assert np.all(result <= 1)
    
    def test_broadcasting_alpha_gamma_per_channel(self):
        """Per-channel alpha/gamma broadcasts correctly."""
        spend = np.array([[100, 200], [150, 250]])  # (2 weeks, 2 channels)
        alpha = np.array([0.8, 1.2])  # Per channel
        gamma = np.array([150, 100])  # Per channel
        
        result = hill_saturation(spend, alpha=alpha, gamma=gamma)
        
        # Result should be (2, 2) with appropriate per-channel saturation
        assert result.shape == (2, 2)
        # Channel 0 should have lower saturation (higher gamma, lower alpha)
        assert np.all(result[:, 0] <= result[:, 1])
    
    def test_single_row_2d_array(self):
        """Single-row 2D array handled correctly."""
        spend = np.array([[100, 200, 300]])  # (1, 3)
        alpha = 1.0
        gamma = 150.0
        result = hill_saturation(spend, alpha=alpha, gamma=gamma)
        
        assert result.shape == (1, 3)
    
    def test_single_column_2d_array(self):
        """Single-column 2D array handled correctly."""
        spend = np.array([[100], [200], [300]])  # (3, 1)
        alpha = 1.0
        gamma = 150.0
        result = hill_saturation(spend, alpha=alpha, gamma=gamma)
        
        assert result.shape == (3, 1)


class TestNumericalStability:
    """Verify numerical robustness at extremes."""
    
    def test_very_large_spend(self):
        """Function stable for spend >> typical values."""
        alpha = 1.0
        gamma = 100.0
        large_spend = 1e15
        
        result = hill_saturation(large_spend, alpha=alpha, gamma=gamma)
        
        assert np.isfinite(result)
        assert 0.9999 < result < 1.0
    
    def test_very_small_spend(self):
        """Function stable for spend << gamma."""
        alpha = 1.0
        gamma = 1e10
        small_spend = 1.0
        
        result = hill_saturation(small_spend, alpha=alpha, gamma=gamma)
        
        assert np.isfinite(result)
        assert result > 0
        assert result < 0.01
    
    def test_extreme_alpha_values(self):
        """Function stable with extreme alpha values."""
        gamma = 100.0
        spend = 150.0
        
        # Very small alpha (nearly linear everywhere)
        result_small_alpha = hill_saturation(spend, alpha=0.1, gamma=gamma)
        assert np.isfinite(result_small_alpha)
        
        # Very large alpha (steep S-curve)
        result_large_alpha = hill_saturation(spend, alpha=5.0, gamma=gamma)
        assert np.isfinite(result_large_alpha)
        
        # Large alpha should produce higher saturation (steeper curve)
        assert result_large_alpha > result_small_alpha
    
    def test_1x_and_1000x_scale_consistency(self):
        """Results scale consistently across magnitude differences."""
        alpha = 1.0
        
        # 1x scale
        spend_1x = np.array([10, 50, 100])
        gamma_1x = 75.0
        result_1x = hill_saturation(spend_1x, alpha=alpha, gamma=gamma_1x)
        
        # 1000x scale (same relative proportions)
        spend_1000x = spend_1x * 1000
        gamma_1000x = gamma_1x * 1000
        result_1000x = hill_saturation(spend_1000x, alpha=alpha, gamma=gamma_1000x)
        
        # Results should be identical (scale invariant)
        np.testing.assert_array_almost_equal(result_1x, result_1000x)


class TestErrorHandling:
    """Verify graceful error handling."""
    
    def test_negative_spend_raises_error(self):
        """Negative spend should raise ValueError."""
        with pytest.raises(ValueError, match="spend must be non-negative"):
            hill_saturation(-10.0, alpha=1.0, gamma=100.0)
    
    def test_negative_spend_array_raises_error(self):
        """Array with any negative spend should raise ValueError."""
        spend = np.array([10, -5, 100])
        with pytest.raises(ValueError, match="spend must be non-negative"):
            hill_saturation(spend, alpha=1.0, gamma=100.0)
    
    def test_zero_gamma_raises_error(self):
        """Zero gamma should raise ValueError."""
        with pytest.raises(ValueError, match="gamma must be positive"):
            hill_saturation(100.0, alpha=1.0, gamma=0.0)
    
    def test_negative_gamma_raises_error(self):
        """Negative gamma should raise ValueError."""
        with pytest.raises(ValueError, match="gamma must be positive"):
            hill_saturation(100.0, alpha=1.0, gamma=-50.0)
    
    def test_array_with_zero_gamma_raises_error(self):
        """Array with any zero/negative gamma should raise ValueError."""
        gamma = np.array([100, 0, 150])
        with pytest.raises(ValueError, match="gamma must be positive"):
            hill_saturation(100.0, alpha=1.0, gamma=gamma)


class TestAlphaEffects:
    """Verify alpha parameter behavior."""
    
    def test_alpha_increases_saturation_effect(self):
        """Higher alpha produces more saturation (steeper curve)."""
        spend = 150.0
        gamma = 100.0
        
        result_low = hill_saturation(spend, alpha=0.5, gamma=gamma)
        result_mid = hill_saturation(spend, alpha=1.0, gamma=gamma)
        result_high = hill_saturation(spend, alpha=2.0, gamma=gamma)
        
        # At spend > gamma, higher alpha should give higher saturation
        assert result_low < result_mid < result_high
    
    def test_alpha_near_zero_approaches_constant(self):
        """Very small alpha produces nearly constant output."""
        alpha = 0.001
        gamma = 100.0
        spends = np.array([1, 10, 100, 1000, 1e6])
        
        saturations = hill_saturation(spends, alpha=alpha, gamma=gamma)
        
        # With very small alpha, saturation should change slowly
        # (nearly constant across spend range)
        relative_range = (saturations.max() - saturations.min()) / saturations.mean()
        assert relative_range < 0.01


class TestRealWorldScenarios:
    """Test realistic ad spend patterns."""
    
    def test_four_channel_mmm_scenario(self):
        """Typical 4-channel MMM with weekly data (52 weeks)."""
        n_weeks = 52
        n_channels = 4
        
        # Generate realistic spend (exponential distribution)
        np.random.seed(42)
        spend = np.random.exponential(scale=100000, size=(n_weeks, n_channels))
        
        # Per-channel parameters (typical ranges)
        alpha = np.array([0.8, 1.1, 0.9, 1.2])  # Mostly linear/slight curve
        gamma = np.array([150000, 200000, 120000, 250000])
        
        result = hill_saturation(spend, alpha=alpha, gamma=gamma)
        
        # Verify shape and bounds
        assert result.shape == (n_weeks, n_channels)
        assert np.all(result >= 0)
        assert np.all(result <= 1)
        
        # Verify no NaN/Inf
        assert np.all(np.isfinite(result))
    
    def test_zero_spend_channel(self):
        """One channel with no spend (common in real data)."""
        spend = np.array([
            [100000, 0, 50000],
            [150000, 0, 75000],
            [120000, 0, 60000],
        ])
        
        alpha = np.array([1.0, 1.0, 1.0])
        gamma = np.array([100000, 100000, 100000])
        
        result = hill_saturation(spend, alpha=alpha, gamma=gamma)
        
        # Zero-spend channel should always produce zero saturation
        assert np.all(result[:, 1] == 0)
        
        # Other channels should have positive saturation
        assert np.all(result[:, 0] > 0)
        assert np.all(result[:, 2] > 0)