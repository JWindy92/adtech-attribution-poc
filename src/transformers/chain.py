import pandas as pd
from typing import List
from src.core.interfaces import Transformer


class TransformerChain(Transformer):
    def __init__(self, transformers: List[Transformer]):
        self.transformers = transformers

    def apply_transforms(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        for t in self.transformers:
            df = t.apply_transforms(df, media_columns)
        return df