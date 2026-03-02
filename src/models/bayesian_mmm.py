import pandas as pd
import numpy as np
import statsmodels.api as sm
from typing import List
from src.core.interfaces import AttributionModel
from src.core.context import AppContext


class BayesianAttributionModel(AttributionModel):
    """
    Attribution model using OLS regression on saturation-transformed media spend.
    
    Fits a linear model of the form:
        conversions = intercept + sum(beta_i * saturated_spend_i) + noise
    
    Where saturated_spend is pre-computed via sqrt saturation transformation.
    """
    
    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.ols_model = None
        self.ols_results = None
        self.contributions = None
        self.media_columns = None

    def fit(self, df: pd.DataFrame, media_columns: List[str], raw_df: pd.DataFrame = None) -> pd.DataFrame:
        pass

    def get_contributions(self) -> pd.DataFrame:
        pass

    def get_model_summary(self) -> sm.regression.RegressionResults:
        pass