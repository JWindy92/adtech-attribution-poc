import pandas as pd
from typing import List
from .base import Transformer


class AdstockSaturationTransformer(Transformer):
    def __init__(self, adstock_params=None, saturation_params=None):
        self.adstock_params = adstock_params or {}
        self.saturation_params = saturation_params or {}
    
    def apply_transforms(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        raise NotImplementedError("Adstock/saturation transforms - Stage 3")
