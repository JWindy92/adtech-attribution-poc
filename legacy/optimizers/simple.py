import pandas as pd
from .base import Optimizer


class SimpleOptimizer(Optimizer):
    def optimize(self, metrics: pd.DataFrame, total_budget: float) -> pd.DataFrame:
        channels = metrics['channel'].tolist()
        current_spend = metrics.set_index('channel')['total_spend'].to_dict()
        cpc = metrics.set_index('channel')['cost_per_conversion'].to_dict()
        
        avg_cpc = metrics['cost_per_conversion'].mean()
        efficiency = {ch: avg_cpc / cpc[ch] for ch in channels}
        
        total_efficiency = sum(efficiency.values())
        optimal_allocation = {ch: (efficiency[ch] / total_efficiency) * total_budget for ch in channels}
        
        results = []
        for ch in channels:
            results.append({
                'channel': ch,
                'current_spend': current_spend[ch],
                'optimal_spend': optimal_allocation[ch],
                'change_pct': (optimal_allocation[ch] - current_spend[ch]) / current_spend[ch] * 100
            })
        
        return pd.DataFrame(results)
