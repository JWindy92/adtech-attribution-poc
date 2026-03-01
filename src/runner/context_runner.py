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
    datasource = CSVDataSource(ctx, data_dir=csv_dir)
    datasource.load_data("synthetic_mmm_data.csv")

    adstock = AdstockTransformer(ctx=ctx, adstock_params=config.DEFAULT_ADSTOCK_PARAMS)
    saturation = SaturationTransformer(ctx=ctx)

    transformer = adstock.then(saturation)
    transformed_data = transformer.apply_transforms(ctx.state.get("raw_df"), ctx.config.channels) # TODO: remove media_columns param, alread has context
    # print(transformed_data.head())
    # print(transformed_data.info())
    transformed_data.to_csv("transformed_data.csv")

    model = BayesianMMMModel(ctx=ctx, samples=2000, tune=1000, target_accept=0.95)
    raw_df = ctx.state.get("raw_df").copy()
    _metrics = model.fit(transformed_data)

    _metrics.to_csv("model_return_output.csv")
    ctx.state.metrics.to_csv("context_state_output.csv")

    # print(ctx.state.metrics.head())
    optimizer = ScipyOptimizer(ctx=ctx)
    total_budget = ctx.state.get("raw_df")[ctx.config.channels].sum().sum()
    optimization_results = optimizer.optimize(ctx.state.metrics, total_budget)

    print(optimization_results.head())
    optimization_results.to_csv("optimization_output.csv")



if __name__ == "__main__":
    main()
