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


def main():
    csv_dir = Path(__file__).parent.parent.parent / "data"
    dataSource = CSVDataSource(str(csv_dir))
    raw_data = dataSource.load_data("synthetic_mmm_data.csv")
    media_columns = dataSource.get_media_columns(raw_data)
    print(raw_data.head())

    passthrough = PassthroughTransformer()
    adstock = AdstockTransformer(adstock_params=config.DEFAULT_ADSTOCK_PARAMS)
    saturation = SaturationTransformer(
        saturation_params=config.DEFAULT_SATURATION_PARAMS
    )

    transformer = passthrough.then(adstock).then(saturation)
    transformed_data = transformer.apply_transforms(raw_data, media_columns)
    print(transformed_data.head())

    model = BayesianMMMModel(samples=2000, tune=1000, target_accept=0.95)
    metrics = model.fit(transformed_data, media_columns, raw_df=raw_data)

    optimizer = ScipyOptimizer()
    total_budget = raw_data[media_columns].sum().sum()
    optimization_results = optimizer.optimize(metrics, total_budget)

    print(optimization_results.head())


def run_pipeline():
    csv_dir = Path(__file__).parent.parent.parent / "data"
    dataSource = CSVDataSource(str(csv_dir))

    adstock = AdstockTransformer(adstock_params=config.DEFAULT_ADSTOCK_PARAMS)
    saturation = SaturationTransformer()

    transformer = adstock.then(saturation)
    # transformer = adstock

    model = BayesianMMMModel(samples=2000, tune=2000, target_accept=0.95)
    optimizer = ScipyOptimizer(method="saturation")

    pipeline = Pipeline(
        data_source=dataSource,
        transformer=transformer,
        attribution_model=model,
        optimizer=optimizer,
    )

    results = pipeline.run("synthetic_mmm_data.csv")
    metrics = results["metrics"]
    # print(metrics.head())
    optimization = results["optimization"]
    # print(optimization.head())
    metrics.to_csv("bayesian_mmm_metrics.csv", index=False)
    optimization.to_csv("bayesian_mmm_optimization.csv", index=False)


if __name__ == "__main__":
    run_pipeline()
