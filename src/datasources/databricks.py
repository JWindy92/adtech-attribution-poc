import pandas as pd
from typing import List
from src.core.interfaces import DataSource


class DatabricksDataSource(DataSource):
    def __init__(self, connection_params):
        self.connection_params = connection_params
    
    def load_data(self, table_name: str) -> pd.DataFrame:
        raise NotImplementedError("Databricks integration - add pyspark logic here")
    
    def get_media_columns(self, df: pd.DataFrame) -> List[str]:
        return ['ctv_spend', 'social_spend', 'search_spend', 'linear_tv_spend']
