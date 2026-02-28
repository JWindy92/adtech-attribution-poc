import pandas as pd
import pytest
from pathlib import Path
from typing import List
from src.core.interfaces import Transformer, DataSource
from src.core.context import AppContext,RunConfig
from src.transformers import PassthroughTransformer
from src.datasources import CSVDataSource

ctx = AppContext(config=RunConfig(
    model_type="test",
    channels=["ctv_spend", "social_spend", "search_spend", "linear_tv_spend"],
))

@pytest.fixture
def sample_data():
    csv_dir = Path(__file__).parent.parent.parent / "data"
    datasource = CSVDataSource(ctx, data_dir=csv_dir)
    data = datasource.load_data("synthetic_mmm_data.csv")
    return data

def test_passthrough_transformer(sample_data):
    # TODO: create test data not dependent on datasource class(es)
    passthrough_transformer = PassthroughTransformer()
    out_data = passthrough_transformer.apply_transforms(sample_data, ctx.config.channels)
    
    pd.testing.assert_frame_equal(out_data, sample_data)
