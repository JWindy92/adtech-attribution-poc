from abc import ABC, abstractmethod
import pandas as pd
from typing import List

class DataSource(ABC):
    @abstractmethod
    def load_data(self, identifier: str) -> pd.DataFrame: ...

    @abstractmethod
    def get_media_columns(self, df: pd.DataFrame) -> List[str]: ...

class Transformer(ABC):
    @abstractmethod
    def apply_transforms(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame: ...

    def then(self, other: 'Transformer') -> 'Transformer':
        """Fluent chaining: AdstockTransformer(...).then(SaturationTransformer(...))"""
        from src.transformers.chain import TransformerChain
        return TransformerChain([self, other])
    
class AttributionModel(ABC):
    @abstractmethod
    def fit(self, df: pd.DataFrame, media_columns: List[str], raw_df: pd.DataFrame = None) -> pd.DataFrame: ...

    @abstractmethod
    def get_contributions(self) -> pd.DataFrame: ...

class Optimizer(ABC):
    @abstractmethod
    def optimize(self, metrics: pd.DataFrame, total_budget: float) -> pd.DataFrame: ...