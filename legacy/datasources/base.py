from abc import ABC, abstractmethod
import pandas as pd
from typing import List


class DataSource(ABC):
    @abstractmethod
    def load_data(self, identifier: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_media_columns(self, df: pd.DataFrame) -> List[str]:
        pass
