import pandas as pd
import numpy as np
from typing import List, Dict
from src.core.interfaces import Transformer


class AdstockTransformer(Transformer):
    def __init__(self, adstock_params=None):
        self.adstock_params = adstock_params or {}
    
    def apply_adstock(self, x: np.ndarray, decay: float, max_lag: int) -> np.ndarray:
        adstocked = np.zeros_like(x, dtype=float)
        for t in range(len(x)):
            for lag in range(min(t + 1, max_lag)):
                adstocked[t] += x[t - lag] * (decay ** lag)
        return adstocked

    def apply_transforms(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        df_transformed = df.copy()
        
        for col in media_columns:
            original = df[col].values
            transformed = original.copy()
            
            if col in self.adstock_params:
                params = self.adstock_params[col]
                transformed = self.apply_adstock(
                    transformed,
                    decay=params.get('decay', 0.5),
                    max_lag=params.get('max_lag', 4)
                )
            
            df_transformed[col] = transformed
        
        return df_transformed
