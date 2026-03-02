from src.runner.context_runner import AppContext, RunConfig
from src.datasources import CSVDataSource
from src.mapper.kaggle_mta_mapper import KaggleMTADataMapper
from pathlib import Path
import pandas as pd

def test_kaggle_mta_mapper():
    ctx = AppContext(config=RunConfig(
        channels=["ctv_spend", "social_spend", "search_spend", "linear_tv_spend"],
        data_dir=Path(__file__).parent.parent.parent / "data" / "kaggle",
        data_file="multi_touch_attribution_data.csv"
    ))
    df = pd.read_csv(ctx.config.data_dir / ctx.config.data_file)
    # Create a minimal context with the expected configuration
    mapper = KaggleMTADataMapper(ctx=ctx)
    mapped_df = mapper.map_schema(df)
    print(mapped_df.head())