import pandas as pd
from pathlib import Path
from typing import List
from src.core.interfaces import DataSource


class CSVDataSource(DataSource):
    REQUIRED_COLUMNS = ['week', 'conversions']
    MEDIA_COLUMNS = ['ctv_spend', 'social_spend', 'search_spend', 'linear_tv_spend'] #TODO: dont hardcode this
    
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        
    def load_data(self, filename: str) -> pd.DataFrame:
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        df = pd.read_csv(filepath)
        
        if not self._validate_schema(df):
            raise ValueError("Data failed schema validation")
        
        df['week'] = pd.to_datetime(df['week'])
        return df
    
    def get_media_columns(self, df: pd.DataFrame) -> List[str]:
        return [col for col in self.MEDIA_COLUMNS if col in df.columns]
    
    def _validate_schema(self, df: pd.DataFrame) -> bool:
        missing_required = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_required:
            return False
        
        media_cols = self.get_media_columns(df)
        if not media_cols:
            return False
        
        critical_cols = self.REQUIRED_COLUMNS + media_cols
        if df[critical_cols].isnull().any().any():
            return False
        
        numeric_cols = ['conversions'] + media_cols
        for col in numeric_cols:
            if not pd.api.types.is_numeric_dtype(df[col]):
                return False
        
        return True
