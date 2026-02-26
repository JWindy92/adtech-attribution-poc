import pandas as pd
from typing import List
from src.core.interfaces import AttributionModel


class SpendProportionalModel(AttributionModel):
    def __init__(self):
        self.metrics = None
        
    def fit(self, df: pd.DataFrame, media_columns: List[str], raw_df: pd.DataFrame = None) -> pd.DataFrame:
        if raw_df is None:
            raw_df = df
        
        total_spend = raw_df[media_columns].sum()
        total_spend_sum = total_spend.sum()
        
        attribution = {}
        for channel in media_columns:
            attribution[channel] = total_spend[channel] / total_spend_sum
        
        total_conversions = df['conversions'].sum()
        
        metrics = []
        for channel in media_columns:
            attr_pct = attribution[channel]
            metrics.append({
                'channel': channel,
                'total_spend': total_spend[channel],
                'attribution_pct': attr_pct,
                'attributed_conversions': total_conversions * attr_pct,
                'cost_per_conversion': total_spend[channel] / (total_conversions * attr_pct) if attr_pct > 0 else 0
            })
        
        self.metrics = pd.DataFrame(metrics)
        return self.metrics
    
    def get_contributions(self) -> pd.DataFrame:
        return self.metrics
