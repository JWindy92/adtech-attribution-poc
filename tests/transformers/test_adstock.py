import pandas as pd
import numpy as np
import pytest
from pathlib import Path
from typing import List
from src.core.context import AppContext,RunConfig
from src.transformers import AdstockTransformer

@pytest.fixture
def ctx():
    return AppContext(config=RunConfig(
        model_type="test",
        channels=["spend"],
    ))

def test_adstock_constant_input(ctx):
    adstock_params = {"spend": {"decay": 0.5, "max_lag": 3}}
    """Constant spend should increase then plateau due to decay accumulation."""
    df = pd.DataFrame({
        "week": range(4),
        "conversions": [1, 1, 1, 1],
        "spend": [100.0, 100.0, 100.0, 100.0],
    })
    
    transformer = AdstockTransformer(ctx, adstock_params=adstock_params)
    result = transformer.apply_transforms(df, ["spend"])
    
    expected = [100.0, 150.0, 175.0, 175.0]
    np.testing.assert_array_almost_equal(result["spend"].values, expected)


def test_adstock_zero_decay(ctx):
    adstock_params = {"spend": {"decay": 0.0, "max_lag": 6}}
    """Decay of 0 means only current period matters."""
    df = pd.DataFrame({
        "week": range(3),
        "conversions": [1, 1, 1],
        "spend": [10.0, 20.0, 30.0],
    })
    
    transformer = AdstockTransformer(ctx, adstock_params=adstock_params)
    result = transformer.apply_transforms(df, ["spend"])
    
    # Should be unchanged
    print(result.head())
    pd.testing.assert_series_equal(result["spend"], df["spend"], check_names=True)


def test_adstock_full_decay(ctx):
    adstock_params = {"spend": {"decay": 1.0, "max_lag": 3}}
    """Decay of 1.0 means all past periods count equally."""
    df = pd.DataFrame({
        "week": range(3),
        "conversions": [1, 1, 1],
        "spend": [10.0, 10.0, 10.0],
    })
    
    # With decay=1.0, max_lag=2:
    # t=0: 10
    # t=1: 10 + 10 * 1.0 = 20
    # t=2: 10 + 10 * 1.0 + 10 * 1.0 = 30
    
    transformer = AdstockTransformer(ctx, adstock_params=adstock_params)
    result = transformer.apply_transforms(df, ["spend"])
    
    expected = [10.0, 20.0, 30.0]
    np.testing.assert_array_almost_equal(result["spend"].values, expected)