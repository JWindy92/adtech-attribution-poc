from abc import ABC, abstractmethod
import pandas as pd
from typing import List


class Transformer(ABC):
    @abstractmethod
    def apply_transforms(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        pass
