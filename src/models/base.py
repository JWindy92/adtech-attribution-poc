from abc import ABC, abstractmethod
import pandas as pd
from typing import List


class AttributionModel(ABC):
    @abstractmethod
    def fit(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_contributions(self) -> pd.DataFrame:
        pass
