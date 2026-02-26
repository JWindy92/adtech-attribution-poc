import pandas as pd
import numpy as np
from typing import List, Dict
from src.core.interfaces import Transformer


class SaturationTransformer(Transformer):
    def __init__(self, saturation_params=None):
        self.saturation_params = saturation_params or {}
    
    def apply_saturation(self, x: np.ndarray, alpha: float, gamma: float) -> np.ndarray:
        return (x ** alpha) / (gamma ** alpha + x ** alpha)
    
    def apply_transforms(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        df_transformed = df.copy()
        
        for col in media_columns:
            original = df[col].values
            transformed = original.copy()
            
            if col in self.saturation_params:
                params = self.saturation_params[col]
                transformed = self.apply_saturation(
                    transformed,
                    alpha=params.get('alpha', 1.0),
                    gamma=params.get('gamma', np.mean(original))
                )
            
            df_transformed[col] = transformed
        
        return df_transformed
