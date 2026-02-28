import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.transformers import (
    PassthroughTransformer,
    AdstockTransformer,
    SaturationTransformer,
)
from src.models import SpendProportionalModel
from src.models.bayesian_mmm import BayesianMMMModel
from src.datasources.csv import CSVDataSource
from src.optimizers import ScipyOptimizer
import src.config as config
from src.pipeline import Pipeline
from src.core.context import AppContext, RunConfig

# TODO: load config from file
ctx = AppContext(config=RunConfig(
    channels=["ctv_spend", "social_spend", "search_spend", "linear_tv_spend"],
    model_type="bayesian_mmm",
    # budget=500_000.0,
))

def main():
    csv_dir = Path(__file__).parent.parent.parent / "data"
    datasource = CSVDataSource(ctx, data_dir="data")
    datasource.load_data("synthetic_mmm_data.csv")


if __name__ == "__main__":
    main()
