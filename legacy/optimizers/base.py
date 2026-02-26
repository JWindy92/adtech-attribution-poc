from abc import ABC, abstractmethod
import pandas as pd


class Optimizer(ABC):
    @abstractmethod
    def optimize(self, metrics: pd.DataFrame, total_budget: float) -> pd.DataFrame:
        pass
