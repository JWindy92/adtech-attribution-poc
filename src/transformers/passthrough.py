import pandas as pd
from typing import List
from src.core.interfaces import Transformer


class PassthroughTransformer(Transformer):
    def apply_transforms(self, df: pd.DataFrame, media_columns: List[str]) -> pd.DataFrame:
        return df
