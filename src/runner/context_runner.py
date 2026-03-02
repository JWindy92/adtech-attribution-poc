import sys
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.transformers import (
    NormalizeTransformer,
    AdstockTransformer,
    SqrtSaturationTransformer,
)
from src.models import SpendProportionalModel
from src.models.bayesian_mmm import BayesianMMMModel
from src.datasources.csv import CSVDataSource
from src.optimizers import ScipyOptimizer
import src.config as config
from src.pipeline import Pipeline
from src.core.context import AppContext, RunConfig
from pprint import pprint
from src.helpers.visualization.raw_data import *
from src.helpers.visualization.analysis import *

# TODO: load config from file
ctx = AppContext(config=RunConfig(
    channels=["ctv_spend", "social_spend", "search_spend", "linear_tv_spend"],
    model_type="bayesian_mmm",
    # budget=500_000.0,
))

def main():
    csv_dir = Path(__file__).parent.parent.parent / "data"
    datasource = CSVDataSource(ctx, data_dir=csv_dir)
    df = datasource.load_data("synthetic_mmm_data.csv")

    
    normalizer = NormalizeTransformer(ctx=ctx)
    adstock = AdstockTransformer(ctx=ctx, adstock_params=config.DEFAULT_ADSTOCK_PARAMS)
    saturation = SqrtSaturationTransformer(ctx=ctx)

    transformer = normalizer.then(adstock).then(saturation)
    # transformer = adstock
    transformed_data = transformer.apply_transforms(ctx.state.get("raw_df"), ctx.config.channels) # TODO: remove media_columns param, alread has context

    transformed_data.to_csv("transformed_data.csv")

    X = transformed_data[[f"{col}_saturated" for col in ctx.config.channels]]
    X = sm.add_constant(X) 
    y = transformed_data['conversions']

    model = sm.OLS(y, X).fit()

    print(model.summary())
    pprint(model.params)
    describe_results_saturated(model, transformed_data)

    plot_residuals(transformed_data, model)

def describe_results_saturated(model, df):
    for col in ctx.config.channels:
        avg_spend = df[col].mean()
        coef = model.params[f'{col}_saturated']
        marginal_return = coef / (2 * np.sqrt(avg_spend))

        marginal_cpa = 1 / marginal_return
        print(f"At an average weekly spend of ${avg_spend:,.2f}:")
        print(f"Each additional $1 is expected to bring {marginal_return:.6f} conversions.")
        print(f"Your Marginal CPA is: ${marginal_cpa:.2f}")

def describe_linear_results(model):
    for col in ctx.config.channels:
        coef = model.params[f'{col}_adstock']
        cpa = 1000 / coef

        coef_1k = coef * 1000
        print(f"For every $1000 spent, we get {coef_1k:.4f} conversions.")
        print(f"Estimated CPA: ${cpa:.2e}")

def get_alphas(alpha_store="data/alpha_params.csv", force=False):
    alpha_path = Path(alpha_store)
    if not force and (alpha_path.exists() and alpha_path.is_file()):
        return pd.read_csv(alpha_path)
    else:
        print("Alpha param file not found at {alpha_path}. Performing grid search...")
        csv_dir = Path(__file__).parent.parent.parent / "data"
        datasource = CSVDataSource(ctx, data_dir=csv_dir)
        adstock = AdstockTransformer(ctx=ctx, adstock_params=config.DEFAULT_ADSTOCK_PARAMS)
        df = datasource.load_data("synthetic_mmm_data.csv")
        optimal_alphas = adstock.alpha_grid_search(df)
        out_rows = []
        for key in optimal_alphas.keys():
            best_run = optimal_alphas[key].copy()
            best_run['channel'] = key
            print(f"Best Alpha for {key}: {best_run['alpha']:.1f}")
            print(f"R-Squared at this Alpha: {best_run['r_squared']:.4f}")
            print(f"Conversions per $1: {best_run['coef']:.6f}")
            out_rows.append(best_run)
        out_df = pd.DataFrame(out_rows).set_index("channel")
        out_df.to_csv(alpha_path, index=True)

if __name__ == "__main__":
    get_alphas()
    main()
