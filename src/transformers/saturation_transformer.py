import pandas as pd
import numpy as np
import src.config
from typing import List, Dict
from src.core.interfaces import Transformer
from scipy.optimize import curve_fit
from pprint import pprint
from src.config import APP_CONFIG


class SaturationTransformer(Transformer):
    def __init__(self, saturation_params=None):
        self.saturation_params = saturation_params or {}

    def calculate_saturation_params(
        self, df: pd.DataFrame, media_columns: List[str]
    ) -> None:
        total_spend = df[media_columns].sum(axis=1)
        y_norm = df["conversions"] / df["conversions"].max()

        for ch in media_columns:
            x = df[ch].values
            spend_share = x / total_spend.values
            y = y_norm.values * spend_share

            popt, _ = curve_fit(
                self.apply_saturation,
                xdata=x,
                ydata=y,
                p0=[2.0, x.mean()],
                bounds=([0.1, 1], [10.0, x.max() * 10]),
                maxfev=5000,
            )
            self.saturation_params[ch] = {"alpha": popt[0], "gamma": popt[1]}
            APP_CONFIG.saturation_params = self.saturation_params

    def apply_saturation(self, x: np.ndarray, alpha: float, gamma: float) -> np.ndarray:
        return (x**alpha) / (gamma**alpha + x**alpha)

    def apply_transforms(
        self, df: pd.DataFrame, media_columns: List[str]
    ) -> pd.DataFrame:
        df_transformed = df.copy()
        if not self.saturation_params:
            print("calculating saturation parameters")
            self.calculate_saturation_params(
                df_transformed, media_columns=media_columns
            )

        for col in media_columns:
            original = df[col].values
            transformed = original.copy()

            if col in self.saturation_params:
                params = self.saturation_params[col]
                transformed = self.apply_saturation(
                    transformed,
                    alpha=params.get("alpha", 1.0),
                    gamma=params.get("gamma", np.mean(original)),
                )

            df_transformed[col] = transformed

        return df_transformed
