import pandas as pd
import numpy as np
import statsmodels.api as sm

import src.config
from typing import List, Dict
from src.core.interfaces import Transformer
from scipy.optimize import curve_fit
from pprint import pprint
from src.core.context import AppContext


class SqrtSaturationTransformer(Transformer):
    def __init__(self, ctx: AppContext, saturation_params=None):
        self.ctx = ctx
        self.saturation_params = saturation_params or {}
    
    def apply_transforms(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        transformed_df = df.copy()
        channels = self.ctx.config.channels
        for chan in channels:
            transformed_df[f"{chan}_saturated"] = np.sqrt(transformed_df[f"{chan}_adstock"])

            # 2. Run the regression
            X = sm.add_constant(transformed_df[f"{chan}_saturated"])
            y = transformed_df['conversions']
            model = sm.OLS(y, X).fit()

            # 3. Extract the coefficient
            # This is no longer "Conversions per $1" directly!
            saturated_coef = model.params[f"{chan}_saturated"]
        return transformed_df