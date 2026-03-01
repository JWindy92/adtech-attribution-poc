import pandas as pd
import numpy as np
from typing import List
from src.core.interfaces import Optimizer
from src.core.context import AppContext 
from pprint import pprint

try:
    from scipy.optimize import minimize, curve_fit

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class ScipyOptimizer(Optimizer):
    def __init__(self, ctx: AppContext, min_channel_budget=1000, method="naive", epsilon=1e-8):
        self.ctx = ctx
        self.min_channel_budget = min_channel_budget
        self.epsilon = epsilon
        self.method = method

    def optimize(self, metrics, total_budget) -> pd.DataFrame:
        if not SCIPY_AVAILABLE:
            raise ImportError("SciPy is required. Install with: pip install scipy")

        # optimized_allocation = self._optimize_naive(metrics, total_budget)
        optimized_allocation = self._optimize_saturation_aware(metrics, total_budget)

        current_spend = metrics["total_spend"].values
        results = metrics.copy()
        results["current_allocation"] = current_spend
        results["optimized_allocation"] = optimized_allocation
        results["change"] = optimized_allocation - current_spend
        results["change_pct"] = (results["change"] / current_spend) * 100
        return results

    def hill_saturation(self, x, alpha, gamma):
        """
        Hill function: flattens spend effect as x grows.
        alpha = slope steepness
        gamma = half-saturation point (spend level at 50% of max effect)
        """
        return x**alpha / (x**alpha + gamma**alpha)

    def unpack_saturation_params(
        self,
        saturation_params: dict,
    ) -> tuple[np.ndarray, np.ndarray]:
        media_columns = self.ctx.config.channels
        alphas = np.array([saturation_params[ch]["alpha"] for ch in media_columns])
        gammas = np.array([saturation_params[ch]["gamma"] for ch in media_columns])
        return alphas, gammas

    def initial_guess(self, total_budget: float, n_channels: int) -> np.ndarray:
        return np.full(n_channels, total_budget / n_channels)

    def build_bounds(
        self, n_channels: int, min_budget: float, total_budget: float
    ) -> list:
        return [(min_budget, total_budget * 0.8)] * n_channels

    def build_constraints(self, total_budget: float) -> list:
        return [{"type": "eq", "fun": lambda x: x.sum() - total_budget}]

    def saturation_objective(
        self,
        allocation: np.ndarray,
        alphas: np.ndarray,
        gammas: np.ndarray,
        beta_coefficients: np.ndarray,  # <-- Use betas instead
    ) -> float:
        saturation = self.hill_saturation(allocation, alphas, gammas)
        return -(beta_coefficients * saturation).sum()

    def run_optimizer(self, objective, x0, bounds, constraints) -> np.ndarray:
        result = minimize(
            objective, x0=x0, method="SLSQP", bounds=bounds, constraints=constraints
        )
        print(f"DEBUG: Optimization success: {result.success}, message: {result.message}")
        print(f"DEBUG: Optimization result.x = {result.x}")
        return result.x if result.success else None

    def _optimize_saturation_aware(
        self, metrics: pd.DataFrame, total_budget: float
    ) -> np.ndarray:
        # extract spend: np.ndarray
        current_spend = metrics["total_spend"].values
        # extract attributed conversions: np.ndarray
        beta_coefficients = metrics["beta_coefficient"].values 
        # get alphas & gammas
        saturation_params = self.ctx.state.get("saturation_params")
        print(f"DEBUG: saturation_params = {saturation_params}")
        alphas, gammas = self.unpack_saturation_params(saturation_params)
        print(f"DEBUG: alphas = {alphas}, gammas = {gammas}")
        
        n_channels = len(self.ctx.config.channels)
        x0 = self.initial_guess(total_budget, n_channels)
        bounds = self.build_bounds(n_channels, self.min_channel_budget, total_budget)
        constraints = self.build_constraints(total_budget)
        
        print(f"DEBUG: x0 = {x0}")
        print(f"DEBUG: bounds = {bounds}")
        print(f"DEBUG: total_budget = {total_budget}")

        # Diagnostic: compare objective values at different allocations
        test_equal = np.array([total_budget / n_channels] * n_channels)
        test_favoring_search = np.array([
            total_budget * 0.5,      # 50% to search (highest beta)
            total_budget * 0.15,     # 15% to social
            total_budget * 0.25,     # 25% to ctv
            total_budget * 0.1       # 10% to linear_tv (lowest beta)
        ])
        
        def objective(alloc):
            return self.saturation_objective(alloc, alphas, gammas, beta_coefficients)

        obj_equal = objective(test_equal)
        obj_search = objective(test_favoring_search)
        
        print(f"DEBUG: Objective at equal allocation: {obj_equal}")
        print(f"DEBUG: Objective favoring search: {obj_search}")
        print(f"DEBUG: Difference (search - equal): {obj_search - obj_equal}")
        print(f"DEBUG: Beta coefficients: {beta_coefficients}")

        result = self.run_optimizer(objective, x0, bounds, constraints)
        print(f"DEBUG: Optimizer result = {result}")
        return result if result is not None else current_spend

    def _optimize_naive(self, metrics: pd.DataFrame, total_budget: float) -> np.ndarray:
        """
        Fixed-CPC linear objective.
        Assumes cost-per-conversion is constant at any spend level.
        Always produces corner solutions — dumps budget into the single
        cheapest channel. Use only for comparison against saturation-aware.
        """
        n_channels = len(metrics)
        current_spend = metrics["total_spend"].values
        cpc = metrics["cost_per_conversion"].values
        cpc = np.where(np.isfinite(cpc), cpc, current_spend.max())

        def objective(allocation):
            return -(allocation / (cpc + self.epsilon)).sum()

        result = minimize(
            objective,
            x0=np.full(n_channels, total_budget / n_channels),
            method="SLSQP",
            bounds=[(self.min_channel_budget, total_budget * 0.8)] * n_channels,
            constraints=[{"type": "eq", "fun": lambda x: x.sum() - total_budget}],
        )
        return result.x if result.success else current_spend
