import pandas as pd
import numpy as np
from src.core.interfaces import Optimizer
from src.config import DEFAULT_SATURATION_PARAMS

try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class ScipyOptimizer(Optimizer):
    def __init__(self, min_channel_budget=1000, method="naive", epsilon=1e-8):
        self.min_channel_budget = min_channel_budget
        self.epsilon = epsilon
        self.method = method
    
    def optimize(self, metrics, total_budget) -> pd.DataFrame:
        if not SCIPY_AVAILABLE:
            raise ImportError("SciPy is required. Install with: pip install scipy")
        
        optimized_allocation = self._optimize_naive(metrics, total_budget)

        current_spend = metrics['total_spend'].values
        results = metrics.copy()
        results['current_allocation'] = current_spend
        results['optimized_allocation'] = optimized_allocation
        results['change'] = optimized_allocation - current_spend
        results['change_pct'] = (results['change'] / current_spend) * 100
        return results
    
    def _optimize_naive(self, metrics: pd.DataFrame, total_budget: float) -> np.ndarray:
        """
        Fixed-CPC linear objective.
        Assumes cost-per-conversion is constant at any spend level.
        Always produces corner solutions — dumps budget into the single
        cheapest channel. Use only for comparison against saturation-aware.
        """
        n_channels = len(metrics)
        current_spend = metrics['total_spend'].values
        cpc = metrics['cost_per_conversion'].values
        cpc = np.where(np.isfinite(cpc), cpc, current_spend.max())

        def objective(allocation):
            return -(allocation / (cpc + self.epsilon)).sum()

        result = minimize(
            objective,
            x0=np.full(n_channels, total_budget / n_channels),
            method='SLSQP',
            bounds=[(self.min_channel_budget, total_budget * 0.8)] * n_channels,
            constraints=[{'type': 'eq', 'fun': lambda x: x.sum() - total_budget}],
        )
        return result.x if result.success else current_spend