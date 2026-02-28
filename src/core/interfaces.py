from abc import ABC, abstractmethod
import pandas as pd
from typing import List
from src.core.context import AppContext

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
    # TODO: consider a different solution than having to pass raw_df to fit() for models that need it - maybe a separate method or something else
    @abstractmethod
    def fit(self, df: pd.DataFrame, media_columns: List[str], raw_df: pd.DataFrame = None) -> pd.DataFrame: ...

    @abstractmethod
    def get_contributions(self) -> pd.DataFrame: ...

class Optimizer(ABC):
    @abstractmethod
    def optimize(self, metrics: pd.DataFrame, total_budget: float) -> pd.DataFrame: ...


class ContextualProcess(ABC):
    """Any process that needs shared application state."""

    def __init__(self, ctx: AppContext):
        self.ctx = ctx

    @abstractmethod
    def run(self) -> None: ...