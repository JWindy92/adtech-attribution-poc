import numpy as np
import pandas as pd
import pytest
from src.core.context import AppContext, RunConfig
from src.transformers import SaturationTransformer


@pytest.fixture
def ctx():
    return AppContext(config=RunConfig(
        model_type="test",
        channels=["channel_a", "channel_b"],
    ))


class TestSaturationParamsCalculation:
    """Test suite for saturation parameter fitting."""
    
    def test_params_fit_with_clear_saturation(self, ctx):
        """When data shows clear saturation, gamma should be moderate (not at max bound)."""
        # Create data with clear saturation: conversions slow down at high spend
        df = pd.DataFrame({
            "week": range(10),
            "conversions": [10, 25, 35, 42, 48, 52, 55, 57, 58, 59],  # Clearly saturating
            "channel_a": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
            "channel_b": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        })
        
        transformer = SaturationTransformer(ctx=ctx)
        transformer.calculate_saturation_params(df, media_columns=["channel_a", "channel_b"])
        
        # Gamma should be reasonable relative to spend range (100-1000)
        gamma_a = transformer.saturation_params["channel_a"]["gamma"]
        gamma_b = transformer.saturation_params["channel_b"]["gamma"]
        
        # Gamma should be bounded and not at the extreme upper limit (10x max spend = 10,000)
        assert gamma_a < 5000, f"Gamma {gamma_a} should not be at extreme upper bound with clear saturation"
        assert gamma_b < 5000, f"Gamma {gamma_b} should not be at extreme upper bound with clear saturation"
    
    def test_params_fit_with_linear_data(self, ctx):
        """When data is linear (no saturation), gamma will be pushed to max bound."""
        # Create perfectly linear data: conversions scale directly with spend
        df = pd.DataFrame({
            "week": range(10),
            "conversions": np.linspace(10, 100, 10),  # Perfect linear scaling
            "channel_a": np.linspace(100, 1000, 10),
            "channel_b": np.linspace(100, 1000, 10),
        })
        
        transformer = SaturationTransformer(ctx=ctx)
        transformer.calculate_saturation_params(df, media_columns=["channel_a", "channel_b"])
        
        # With linear data, gamma should hit near the upper bound
        gamma_a = transformer.saturation_params["channel_a"]["gamma"]
        max_spend_a = df["channel_a"].max()
        upper_bound = max_spend_a * 10
        
        # Gamma should be very close to upper bound for linear data
        assert gamma_a > max_spend_a * 5, f"Linear data should push gamma high, got {gamma_a}"
    
    def test_alpha_is_reasonable(self, ctx):
        """Alpha should stay within [0.1, 10.0] bounds."""
        df = pd.DataFrame({
            "week": range(10),
            "conversions": [10, 25, 35, 42, 48, 52, 55, 57, 58, 59],
            "channel_a": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
            "channel_b": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        })
        
        transformer = SaturationTransformer(ctx=ctx)
        transformer.calculate_saturation_params(df, media_columns=["channel_a", "channel_b"])
        
        alpha_a = transformer.saturation_params["channel_a"]["alpha"]
        alpha_b = transformer.saturation_params["channel_b"]["alpha"]
        
        assert 0.1 <= alpha_a <= 10.0, f"Alpha {alpha_a} outside bounds"
        assert 0.1 <= alpha_b <= 10.0, f"Alpha {alpha_b} outside bounds"
    
    def test_params_vary_by_channel(self, ctx):
        """Different channels with different spending patterns should get different params."""
        df = pd.DataFrame({
            "week": range(10),
            "conversions": [10, 25, 35, 42, 48, 52, 55, 57, 58, 59],
            "channel_a": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],  # Linear
            "channel_b": [100, 300, 400, 420, 430, 435, 437, 438, 438, 439],   # Saturates fast
        })
        
        transformer = SaturationTransformer(ctx=ctx)
        transformer.calculate_saturation_params(df, media_columns=["channel_a", "channel_b"])
        
        gamma_a = transformer.saturation_params["channel_a"]["gamma"]
        gamma_b = transformer.saturation_params["channel_b"]["gamma"]
        
        # Channel B saturates faster, so should have lower gamma
        assert gamma_b < gamma_a, "Fast-saturating channel should have lower gamma"
    
    def test_extremely_linear_synthetic_data(self, ctx):
        """Highlight the issue: synthetic data with perfect linearity causes inflated gammas."""
        # This is what happens with the synthetic_mmm_data.csv
        df = pd.DataFrame({
            "week": range(52),  # Full year of data
            "conversions": np.repeat(100, 52),  # Constant conversions (unrealistic)
            "channel_a": np.linspace(10000, 100000, 52),  # Linear increase
            "channel_b": np.linspace(10000, 100000, 52),
        })
        
        transformer = SaturationTransformer(ctx=ctx)
        transformer.calculate_saturation_params(df, media_columns=["channel_a", "channel_b"])
        
        gamma_a = transformer.saturation_params["channel_a"]["gamma"]
        max_spend_a = df["channel_a"].max()
        
        print(f"\nSynthetic linear data:")
        print(f"  Max spend: {max_spend_a}")
        print(f"  Fitted gamma: {gamma_a}")
        print(f"  Gamma/max_spend ratio: {gamma_a / max_spend_a:.2f}")
        
        # This illustrates the problem: with constant conversions, gamma inflates
        assert gamma_a > max_spend_a * 5, "Linear/flat data produces very high gammas"
