import pandas as pd
from pathlib import Path
from typing import List
from src.core.interfaces import DataSource
from src.core.context import AppContext



class CSVDataSource(DataSource):
    #TODO: this is hard coded and specific to the synthetic data - need to make more flexible for real world use
    REQUIRED_COLUMNS = ['week', 'conversions']
    MEDIA_COLUMNS = ['ctv_spend', 'social_spend', 'search_spend', 'linear_tv_spend'] #TODO: dont hardcode this
    
    def __init__(self, ctx: AppContext, data_dir="data"):
        self.ctx = ctx
        self.data_dir = Path(data_dir)
        self._media_columns = ctx.config.channels
        
    def load_data(self, filename: str) -> pd.DataFrame:
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        df = pd.read_csv(filepath)
        
        if not self._validate_schema(df):
            raise ValueError("Data failed schema validation")
        
        df['week'] = pd.to_datetime(df['week'])

        self.ctx.state.set("raw_df", df)
        self.ctx.update_state(current_step="data_loaded")

        return df
    
    def get_media_columns(self, df: pd.DataFrame) -> List[str]:
        return [col for col in self.MEDIA_COLUMNS if col in df.columns]
    
    def _validate_schema(self, df: pd.DataFrame) -> bool:
        missing_required = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_required:
            self.ctx.state.errors.append(f"Missing required columns: {missing_required}")
            return False

        media_cols = self.get_media_columns(df)
        if not media_cols:
            self.ctx.state.errors.append("No configured media columns found in file")
            return False

        critical_cols = self.REQUIRED_COLUMNS + media_cols
        if df[critical_cols].isnull().any().any():
            self.ctx.state.errors.append("Null values found in critical columns")
            return False

        numeric_cols = ['conversions'] + media_cols
        for col in numeric_cols:
            if not pd.api.types.is_numeric_dtype(df[col]):
                self.ctx.state.errors.append(f"Non-numeric data in column: {col}")
                return False

        return True
