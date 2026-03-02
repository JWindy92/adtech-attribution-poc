import pandas as pd
import numpy as np
from src.core.interfaces import SchemaMapper
from src.core.context import AppContext

class KaggleMTADataMapper(SchemaMapper):

    def __init__(self, ctx: AppContext, file_path: str = None):
        self.ctx = ctx
        self.file_path = file_path
        self.weekly_budget = 100000

    def map_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        # Example mapping logic - adjust based on actual schema differences
        channels = df['Channel'].unique()
        print(f"{len(channels)} channels")
        print(channels)
        spend_pcts = np.random.dirichlet([1, 1, 1, 1])

        conversion_enc = {"Yes": 1, "No": 0}

        df['Conversion'] = df['Conversion'].map(conversion_enc)
        for chan in channels:
            num_conv = df.loc[df['Channel'] == chan, 'Conversion'].sum()
            print(f"{chan}: {num_conv} conversions")

            # Pivot the data to have one row per week and separate columns for each channel's spend
        df_pivot = df.pivot_table(index='Timestamp', columns='Channel', values='Spend', aggfunc='sum').reset_index()
        df_pivot.columns.name = None  # Remove the aggregation name
        df_pivot.rename(columns={'Week': 'week'}, inplace=True)     
        return df