import pandas as pd
import numpy as np
import pytest
from src.core.context import AppContext, RunConfig
from src.transformers import SaturationTransformer

@pytest.fixture
def ctx():
    return AppContext(config=RunConfig(
        model_type="test",
        channels=["spend"],
    ))

def show_results(result: pd.DataFrame):
    print()
    print(f"Result columns: {result.head()}")
    print()
    print("calculating 'spend_effective'...")
    result["spend_effective"] = result["spend_saturated"] * result["spend"]
    print()
    print(result.head())

def test_saturation_zero_spend():
    """Spending zero should result in zero output."""
    df = pd.DataFrame({
        "week": range(1),
        "conversions": [100],
        "spend": [0.0],
    })
    
    saturation_params = {"spend": {"alpha": 1.5, "gamma": 100}}
    transformer = SaturationTransformer(saturation_params=saturation_params)
    result = transformer.apply_transforms(df, ["spend"])
    
    show_results(result=result)
    assert result["spend"].iloc[0] == 0.0

def test_saturation_monotonic_increase():
    """Higher spend = higher output."""
    df = pd.DataFrame({
        "week": range(4),
        "conversions": [100, 100, 100, 100],
        "spend": [10.0, 50.0, 100.0, 200.0],
    })
    
    saturation_params = {"spend": {"alpha": 1.5, "gamma": 50}}
    transformer = SaturationTransformer(saturation_params=saturation_params)
    result = transformer.apply_transforms(df, ["spend"])
    
    show_results(result=result)
    # Verify monotonic increase
    assert (result["spend"].diff().dropna() > 0).all()

def test_saturation_bounded():
    """Output should be bounded [0, 1]."""
    df = pd.DataFrame({
        "week": range(5),
        "conversions": [100, 100, 100, 100, 100],
        "spend": [0.0, 10.0, 50.0, 200.0, 1000.0],
    })
    
    saturation_params = {"spend": {"alpha": 2.0, "gamma": 100}}
    transformer = SaturationTransformer(saturation_params=saturation_params)
    result = transformer.apply_transforms(df, ["spend"])
    
    show_results(result=result)
    assert (result["spend_saturated"] >= 0).all()
    assert (result["spend_saturated"] <= 1).all()