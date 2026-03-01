import pandas as pd
import numpy as np
import src.config
from typing import List, Dict
from src.core.interfaces import Transformer
from scipy.optimize import curve_fit
from pprint import pprint
from src.core.context import AppContext


class SaturationTransformer(Transformer):
    def __init__(self, ctx: AppContext, saturation_params=None):
        self.ctx = ctx
        self.saturation_params = saturation_params or {}

    def calculate_saturation_params(
        self, df: pd.DataFrame, media_columns: List[str], expected_total_budget: float = None
    ) -> None:
        """
        Fit saturation parameters (alpha, gamma) for each channel.
        
        Key principle: 
        - Alpha (shape) is fit from historical data to understand channel curvature
        - Gamma (half-saturation point) is NOT fit—it's calculated based on the principle:
          "At typical optimization budget, saturation should be ~60% so optimization can 
          move budgets and see meaningful differences."
        
        This avoids the problem of fitting gamma to historical data (0-300K) and then
        extrapolating it to optimization budgets (6.4M+), which produces gammas that are
        too small and cause premature saturation at optimization scales.
        
        Args:
            df: DataFrame with conversion and spend data
            media_columns: List of channel spend columns
            expected_total_budget: Expected total optimization budget. If provided, gamma
                                values are calculated to produce ~60% saturation at typical
                                per-channel budget. If None, falls back to fitting gamma
                                from historical data patterns.
        """
        channels = self.ctx.config.channels
        total_spend = df[channels].sum(axis=1)
        y_norm = df["conversions"] / df["conversions"].max()

        # Auto-calculate budget from context if not provided
        if expected_total_budget is None:
            raw_df = self.ctx.state.get("raw_df")
            if raw_df is not None:
                expected_total_budget = raw_df[channels].sum().sum()

        for ch in channels:
            x = df[ch].values
            spend_share = x / total_spend.values
            y = y_norm.values * spend_share

            # Always fit both alpha and gamma from historical data first
            # Historical data is ground truth for curve shape
            popt, _ = curve_fit(
                self.apply_saturation,
                xdata=x,
                ydata=y,
                p0=[1.0, x.mean()],
                bounds=([0.1, 1], [10.0, x.max() * 10]),
                maxfev=5000,
            )
            fitted_alpha = popt[0]
            fitted_gamma = popt[1]
            
            # If we have expected_total_budget, calculate gamma for optimization scale
            if expected_total_budget is not None:
                n_channels = len(channels)
                typical_spend_per_channel = expected_total_budget / n_channels
                
                # Principle: At typical optimization budget, saturation should be ~60%
                # This ensures:
                # 1. Channels are not fully saturated (still responsive to budget changes)
                # 2. Optimal allocation can differentiate channels based on their betas
                # 3. Avoids extrapolating fitted gamma far beyond historical data range
                #
                # For Hill saturation: sat(spend, alpha, gamma) = spend^alpha / (gamma^alpha + spend^alpha)
                # Solving for gamma when sat = 0.6:
                # gamma = spend * ((1-0.6)/0.6)^(1/alpha) = spend * (2/3)^(1/alpha)
                
                target_saturation = 0.6
                ratio = (1 - target_saturation) / target_saturation  # 2/3
                gamma_calculated = typical_spend_per_channel * (ratio ** (1.0 / fitted_alpha))
                
                self.saturation_params[ch] = {
                    "alpha": fitted_alpha,
                    "gamma": gamma_calculated
                }
            else:
                self.saturation_params[ch] = {
                    "alpha": fitted_alpha,
                    "gamma": fitted_gamma
                }

        self.ctx.state.set("saturation_params", self.saturation_params)

    def apply_saturation(self, x: np.ndarray, alpha: float, gamma: float) -> np.ndarray:
        return (x**alpha) / (gamma**alpha + x**alpha)

    def apply_transforms(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        df_transformed = df.copy()
        if not self.saturation_params:
            self.calculate_saturation_params(df_transformed, media_columns=media_columns)

        for col in media_columns:
            if col in self.saturation_params:
                params = self.saturation_params[col]
                saturated = self.apply_saturation(
                    df[col].values,
                    alpha=params['alpha'],
                    gamma=params['gamma']
                )
                # Use a new column name
                df_transformed[f"{col}_saturated"] = saturated
            else:
                df_transformed[f"{col}_saturated"] = df[col]

        return df_transformed