import pandas as pd
from .base import Optimizer


class ScipyOptimizer(Optimizer):
    def optimize(self, metrics: pd.DataFrame, total_budget: float) -> pd.DataFrame:
        raise NotImplementedError("SciPy optimizer - Stage 3 (Day 9)")
