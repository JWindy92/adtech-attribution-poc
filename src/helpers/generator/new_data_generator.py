import warnings

import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc as pm
import seaborn as sns
from pymc_extras.prior import Prior

from pymc_marketing.mmm import GeometricAdstock, LogisticSaturation
from pymc_marketing.mmm.multidimensional import MMM
from pymc_marketing.mmm.transformers import geometric_adstock, logistic_saturation

warnings.filterwarnings("ignore", category=FutureWarning)

az.style.use("arviz-darkgrid")
plt.rcParams["figure.figsize"] = [12, 7]
plt.rcParams["figure.dpi"] = 100

class DataGenerator:
    def __init__(self, seed=42):
        self.seed = sum(map(ord, "mmm"))
        self.rng = np.random.default_rng(seed=seed)
        # np.random.seed(seed)
        
        
    def generate_data(self):
        # TODO: parameterize date range
        min_date = pd.to_datetime("2018-04-01")
        max_date = pd.to_datetime("2021-09-01")

        df = pd.DataFrame(
            data={"date_week": pd.date_range(start=min_date, end=max_date, freq="W-MON")}
        ).assign(
            year=lambda x: x["date_week"].dt.year,
            month=lambda x: x["date_week"].dt.month,
            dayofyear=lambda x: x["date_week"].dt.dayofyear,
        )

        n = df.shape[0]
        print(f"Number of observations: {n}")
        print(df.head())
        df = self.add_media_costs(df)
        df = self.apply_adstock(df)
        df = self.apply_saturation(df)
        

    def add_media_costs(self, df):
        result = df.copy()
        n = df.shape[0] #TODO: dup
        x1 = self.rng.uniform(low=0.0, high=1.0, size=n)
        result["x1"] = np.where(x1 > 0.9, x1, x1 / 2)

        x2 = self.rng.uniform(low=0.0, high=1.0, size=n)
        result["x2"] = np.where(x2 > 0.8, x2, 0)

        print(result.head())
        return result

    def apply_adstock(self, df):
        result = df.copy()
        alpha1: float = 0.4
        alpha2: float = 0.2

        result["x1_adstock"] = (
            geometric_adstock(x=result["x1"].to_numpy(), alpha=alpha1, l_max=8, normalize=True)
            .eval()
            .flatten()
        )

        result["x2_adstock"] = (
            geometric_adstock(x=result["x2"].to_numpy(), alpha=alpha2, l_max=8, normalize=True)
            .eval()
            .flatten()
        )
        print(result.head())
        return result
    
    def apply_saturation(self, df):
        result = df.copy()

        # apply saturation transformation
        lam1: float = 4.0
        lam2: float = 3.0

        df["x1_adstock_saturated"] = logistic_saturation(
            x=df["x1_adstock"].to_numpy(), lam=lam1
        ).eval()

        df["x2_adstock_saturated"] = logistic_saturation(
            x=df["x2_adstock"].to_numpy(), lam=lam2
        ).eval()

        print(result.head())
        return result
    
if __name__ == "__main__":
    gen = DataGenerator()
    gen.generate_data()