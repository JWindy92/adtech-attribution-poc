import pandas as pd
import numpy as np
from .base import Optimizer

try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class ScipyOptimizer(Optimizer):
    def __init__(self, min_channel_budget=1000, epsilon=1e-8):
        self.min_channel_budget = min_channel_budget
        self.epsilon = epsilon
    
    def optimize(self, metrics: pd.DataFrame, total_budget: float) -> pd.DataFrame:
        if not SCIPY_AVAILABLE:
            raise ImportError("SciPy is required. Install with: pip install scipy")
        
        n_channels = len(metrics)
        current_spend = metrics['total_spend'].values
        cpc = metrics['cost_per_conversion'].values
        cpc = np.where(np.isfinite(cpc), cpc, current_spend.max())
        
        def objective(allocation):
            conversions = allocation / (cpc + self.epsilon)
            return -conversions.sum()
        
        constraints = [
            {'type': 'eq', 'fun': lambda x: x.sum() - total_budget}
        ]
        
        bounds = [(self.min_channel_budget, total_budget * 0.8) for _ in range(n_channels)]
        
        x0 = np.full(n_channels, total_budget / n_channels)
        
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            optimized_allocation = current_spend
        else:
            optimized_allocation = result.x
        
        optimization_results = metrics.copy()
        optimization_results['current_allocation'] = current_spend
        optimization_results['optimized_allocation'] = optimized_allocation
        optimization_results['change'] = optimized_allocation - current_spend
        optimization_results['change_pct'] = (optimization_results['change'] / current_spend) * 100
        
        return optimization_results
