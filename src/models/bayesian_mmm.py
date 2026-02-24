import pandas as pd
from typing import List
from .base import AttributionModel


class BayesianMMMModel(AttributionModel):
    def __init__(self):
        self.metrics = None
        self.trace = None
    
    def fit(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        raise NotImplementedError("Bayesian MMM - Stage 3 (Days 6-9)")
    
    def get_contributions(self) -> pd.DataFrame:
        return self.metrics
