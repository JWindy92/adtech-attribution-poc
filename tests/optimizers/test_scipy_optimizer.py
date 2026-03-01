import numpy as np
import pytest
from src.core.context import AppContext, RunConfig
from src.optimizers import ScipyOptimizer


@pytest.fixture
def optimizer():
    """Create a ScipyOptimizer instance for testing."""
    ctx = AppContext(config=RunConfig(
        model_type="test",
        channels=["channel_a", "channel_b"],
    ))
    return ScipyOptimizer(ctx=ctx)


class TestHillSaturation:
    """Test suite for the Hill saturation function."""
    
    def test_hill_saturation_zero_input(self, optimizer):
        """Zero spend should result in zero saturation."""
        result = optimizer.hill_saturation(0, alpha=1.5, gamma=100)
        assert result == 0.0
    
    def test_hill_saturation_half_saturation_point(self, optimizer):
        """At x=gamma, Hill function should equal 0.5."""
        result = optimizer.hill_saturation(100, alpha=1.5, gamma=100)
        assert np.isclose(result, 0.5, rtol=1e-6)
    
    def test_hill_saturation_monotonic_increase(self, optimizer):
        """Higher spend should produce higher saturation (monotonicity)."""
        spend_values = np.array([10, 50, 100, 200, 500])
        results = optimizer.hill_saturation(spend_values, alpha=1.5, gamma=100)
        
        # Check that results are monotonically increasing
        assert np.all(np.diff(results) > 0), "Hill saturation should monotonically increase"
    
    def test_hill_saturation_bounded_zero_one(self, optimizer):
        """Hill saturation output should always be in [0, 1]."""
        spend_values = np.array([0, 1, 10, 100, 1000, 10000])
        results = optimizer.hill_saturation(spend_values, alpha=2.0, gamma=100)
        
        assert np.all(results >= 0), "Hill saturation should be >= 0"
        assert np.all(results <= 1), "Hill saturation should be <= 1"
    
    def test_hill_saturation_large_spend_approaches_one(self, optimizer):
        """Very large spend should approach saturation of 1."""
        large_spend = 1e10
        result = optimizer.hill_saturation(large_spend, alpha=1.5, gamma=100)
        assert result > 0.99, "Large spend should approach saturation of 1"
    
    def test_hill_saturation_alpha_affects_steepness(self, optimizer):
        """Higher alpha should increase steepness of curve."""
        spend = 50
        result_low_alpha = optimizer.hill_saturation(spend, alpha=0.5, gamma=100)
        result_high_alpha = optimizer.hill_saturation(spend, alpha=2.0, gamma=100)
        
        # At spend < gamma, higher alpha should give lower saturation
        assert result_high_alpha < result_low_alpha
    
    def test_hill_saturation_gamma_affects_shape(self, optimizer):
        """Higher gamma shifts the half-saturation point."""
        spend = 100
        result_low_gamma = optimizer.hill_saturation(spend, alpha=1.5, gamma=50)
        result_high_gamma = optimizer.hill_saturation(spend, alpha=1.5, gamma=200)
        
        # At spend=100, low gamma means we're past saturation point, high gamma means we're before it
        assert result_low_gamma > result_high_gamma
    
    def test_hill_saturation_vectorized(self, optimizer):
        """Hill saturation should work with numpy arrays."""
        spend_array = np.array([0, 25, 50, 100, 200])
        alpha_array = np.array([1.5, 1.5, 1.5, 1.5, 1.5])
        gamma_array = np.array([100, 100, 100, 100, 100])
        
        results = optimizer.hill_saturation(spend_array, alpha_array, gamma_array)
        
        assert len(results) == len(spend_array)
        assert np.all(results >= 0)
        assert np.all(results <= 1)
    
    def test_hill_saturation_symmetry_with_parameters(self, optimizer):
        """Test consistent behavior across different alpha/gamma combinations."""
        spend = 100
        result_1 = optimizer.hill_saturation(spend, alpha=1.0, gamma=100)
        result_2 = optimizer.hill_saturation(spend, alpha=1.0, gamma=100)
        
        assert result_1 == result_2, "Same inputs should produce same outputs"


# ---------------------------------------------------------------------------- #
#                          Saturation Objective Tests                          #
# ---------------------------------------------------------------------------- #

class TestSaturationObjective:
    """Test suite for the saturation_objective function."""
    
    def test_objective_different_allocations_produce_different_values(self, optimizer):
        """Different allocations should produce different objective values."""
        alphas = np.array([1.5, 1.0])
        gammas = np.array([100, 150])
        baseline_revenue = np.array([1000, 500])
        
        allocation_1 = np.array([5000, 5000])  # Equal split
        allocation_2 = np.array([8000, 2000])  # Unequal split
        
        obj_1 = optimizer.saturation_objective(allocation_1, alphas, gammas, baseline_revenue)
        obj_2 = optimizer.saturation_objective(allocation_2, alphas, gammas, baseline_revenue)
        
        assert obj_1 != obj_2, "Different allocations should produce different objectives"
    
    def test_objective_higher_allocation_to_high_return_channel_improves_objective(self, optimizer):
        """Shifting budget to channel with higher conversions should improve objective."""
        # Use gamma=5000 so spend amounts (5000-7000) are in the meaningful range of the saturation curve.
        # If gamma is too small relative to spend, both allocations hit near-maximum saturation and
        # the difference becomes negligible. With gamma=5000, we're in the pre-saturation zone where
        # the Hill function is sensitive to allocation changes.
        alphas = np.array([1.5, 1.5])
        gammas = np.array([5000, 5000])
        baseline_revenue = np.array([1000, 500])  # First channel has higher conversions
        
        equal_allocation = np.array([5000, 5000])
        more_to_channel_1 = np.array([7000, 3000])  # More to high-return channel
        
        obj_equal = optimizer.saturation_objective(equal_allocation, alphas, gammas, baseline_revenue)
        obj_optimized = optimizer.saturation_objective(more_to_channel_1, alphas, gammas, baseline_revenue)
        
        # Remember: objective is negated, so better = more negative
        assert obj_optimized < obj_equal, "Allocating more to high-return channel should improve objective"
    
    def test_objective_all_zero_allocation(self, optimizer):
        """Zero allocation should result in zero objective."""
        alphas = np.array([1.5, 1.0])
        gammas = np.array([100, 150])
        baseline_revenue = np.array([1000, 500])
        
        allocation = np.array([0, 0])
        obj = optimizer.saturation_objective(allocation, alphas, gammas, baseline_revenue)
        
        assert obj == 0.0, "Zero allocation should produce zero objective"
    
    def test_objective_respects_saturation_differences(self, optimizer):
        """Channels with different saturation curves should respond differently to allocation changes."""
        alphas = np.array([0.5, 2.0])  # Different saturation curves
        gammas = np.array([100, 100])
        baseline_revenue = np.array([1000, 1000])  # Same baseline
        
        equal_allocation = np.array([5000, 5000])
        more_to_channel_1 = np.array([7000, 3000])
        more_to_channel_2 = np.array([3000, 7000])
        
        obj_equal = optimizer.saturation_objective(equal_allocation, alphas, gammas, baseline_revenue)
        obj_more_ch1 = optimizer.saturation_objective(more_to_channel_1, alphas, gammas, baseline_revenue)
        obj_more_ch2 = optimizer.saturation_objective(more_to_channel_2, alphas, gammas, baseline_revenue)
        
        # The two unequal allocations should not be equally good due to different saturation
        assert obj_more_ch1 != obj_more_ch2, "Different saturation curves should produce different objective values"
    
    def test_objective_increases_with_higher_baseline_revenue(self, optimizer):
        """Channels with higher baseline revenue should contribute more to objective."""
        alphas = np.array([1.5, 1.5])
        gammas = np.array([100, 100])
        
        allocation = np.array([5000, 5000])
        
        baseline_revenue_low = np.array([100, 100])
        baseline_revenue_high = np.array([1000, 1000])
        
        obj_low = optimizer.saturation_objective(allocation, alphas, gammas, baseline_revenue_low)
        obj_high = optimizer.saturation_objective(allocation, alphas, gammas, baseline_revenue_high)
        
        # More negative = better, so higher baseline should be more negative
        assert obj_high < obj_low, "Higher baseline revenue should produce better (more negative) objective"