import pandas as pd
import numpy as np
from typing import List, Dict
from src.core.interfaces import Transformer
from src.core.context import AppContext

class NormalizeTransformer(Transformer):
    def __init__(self, ctx: AppContext, adstock_params=None):
        self.ctx = ctx
        self.adstock_params = adstock_params or {}
    
    def normalize(self, df: pd.DataFrame) -> np.ndarray:
        for col in self.ctx.config.channels:
            new_col = f"{col}_normalized"
            df[new_col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
        return df
        
    def apply_transforms(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        df_transformed = df.copy()
        return self.normalize(df_transformed)
