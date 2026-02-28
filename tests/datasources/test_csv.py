import pandas as pd
from pathlib import Path
from typing import List
from src.core.interfaces import DataSource
from src.core.context import AppContext,RunConfig
from src.datasources import CSVDataSource

ctx = AppContext(config=RunConfig(
    model_type="test",
    channels=["ctv_spend", "social_spend", "search_spend", "linear_tv_spend"],
))

def test_csv_datasource():
    csv_dir = Path(__file__).parent.parent.parent / "data"
    datasource = CSVDataSource(ctx, data_dir=csv_dir)
    data = datasource.load_data("synthetic_mmm_data.csv")
    print(data.head())
    assert set(ctx.config.channels).issubset(data.columns)
