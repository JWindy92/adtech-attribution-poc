import pandas as pd
import numpy as np
from scipy.signal import lfilter
from typing import List, Dict
from src.core.interfaces import Transformer
from src.core.context import AppContext
import statsmodels.api as sm
from pprint import pprint
class AdstockTransformer(Transformer):
    def __init__(self, ctx: AppContext, adstock_params=None):
        self.ctx = ctx
        self.adstock_params = adstock_params or {}
    
    def apply_adstock(self, x: np.ndarray, decay: float, max_lag: int) -> np.ndarray:
        adstocked = np.zeros_like(x, dtype=float)
        for t in range(len(x)):
            for lag in range(min(t + 1, max_lag)):
                adstocked[t] += x[t - lag] * (decay ** lag)
        return adstocked

    def apply_transforms(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        df_adstocked = self.adstock_new(df, media_columns)
        return pd.concat([df, df_adstocked], axis=1)
    
    def adstock_new(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        adstocked_df = pd.DataFrame(index=df.index)
        params = self.adstock_params

        for channel, alpha in params.items():
            if channel in df.columns:
                alpha = params.get('decay', 0.5)
                # Apply recursive filter: y[t] = x[t] + alpha * y[t-1]
                # adstocked_df[f'{channel}_adstock'] = self.get_adstock(df[channel], alpha=alpha)
                adstocked_df[f'{channel}_adstock'] = self.get_adstock_normalized(df[channel], alpha=alpha)
                
        return adstocked_df
    
    def get_adstock(self, raw_spend_series, alpha):
        return lfilter([1], [1, -alpha], raw_spend_series)
    
    def get_adstock_normalized(self, raw_spend_series, alpha):
        # Calculate recursive adstock
        adstock = lfilter([1], [1, -alpha], raw_spend_series)
        # Normalize: Sum of Adstock == Sum of Raw Spend
        scaling_factor = raw_spend_series.sum() / adstock.sum()
        return adstock * scaling_factor
    
    def alpha_grid_search(self, df: pd.DataFrame):
        alpha_choices = np.linspace(0.0, 0.9, 10) 
        optimal_results = {}
        for col in self.ctx.config.channels:
            print(f"optimizing {col}")
            results = []
            for a in alpha_choices:
                print(f"[{col}] alpha={a}")
                norm_adstock = self.get_adstock_normalized(df[col], a)
                X = sm.add_constant(norm_adstock)
                model = sm.OLS(df['conversions'], X).fit()
    
                # Store the Alpha and its corresponding R-Squared
                results.append({
                    'alpha': a,
                    'r_squared': model.rsquared,
                    'coef': model.params.iloc[1], # Conversions per $1 (second param after const)
                    'intercept': model.params['const'] # Base Conversions
                })
            results_df = pd.DataFrame(results)
            best_run = results_df.loc[results_df['r_squared'].idxmax()]
            optimal_results[col] = best_run
        return optimal_results
            

    def adstock_old(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        df_transformed = df.copy()
        
        for col in media_columns:
            normalized_col = f"{col}_normalized"
            original = df[normalized_col].values
            transformed = original.copy()
            
            if col in self.adstock_params:
                params = self.adstock_params[col]
                pprint(params)
                transformed = self.apply_adstock(
                    transformed,
                    decay=params.get('decay', 0.5),
                    max_lag=params.get('max_lag', 4)
                )
            
            df_transformed[f"{col}_adstock"] = transformed
        
        return df_transformed