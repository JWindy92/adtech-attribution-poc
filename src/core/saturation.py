"""
Hill Saturation Function - Core mathematical operation for MMM.

The Hill equation models diminishing returns to marketing spend:
  saturation(spend, alpha, gamma) = spend^alpha / (gamma^alpha + spend^alpha)

Where:
  - alpha: Curve steepness. alpha=1 (linear), alpha>1 (curved/S-shape)
  - gamma: Half-saturation point (spend level where saturation = 0.5)
  - Both parameters learned in Bayesian model, not pre-fit

No dependencies outside numpy. Pure function - fully testable.
"""
#! Deprecated
import numpy as np
from typing import Union


def hill_saturation(
    spend: Union[float, np.ndarray],
    alpha: Union[float, np.ndarray],
    gamma: Union[float, np.ndarray],
) -> Union[float, np.ndarray]:
    """
    Apply Hill saturation transformation to marketing spend.
    
    Formula:
        saturation = spend^alpha / (gamma^alpha + spend^alpha)
    
    Properties:
        - saturation(0) = 0 (no spend, no output)
        - saturation(∞) → 1 (asymptotic ceiling)
        - 0 ≤ saturation ≤ 1 for all spend ≥ 0
        - saturation(gamma) = 0.5 (gamma is half-saturation point)
    
    Args:
        spend: Marketing spend. Can be scalar, 1D array, or 2D array.
            Shape: (), (n,), or (n_periods, n_channels)
            Values: Must be ≥ 0. Negative spend raises ValueError.
        
        alpha: Curve steepness parameter.
            Shape: scalar or (n_channels,)
            Range: (0, ∞). Typical: 0.1 to 3.0
            - alpha=1: Linear saturation (no ceiling)
            - alpha>1: S-curve (strong saturation effect)
        
        gamma: Half-saturation point (spend at 50% output).
            Shape: scalar or (n_channels,)
            Range: > 0. Typical: 0.1x to 10x of mean spend
            Raises ValueError if gamma ≤ 0.
    
    Returns:
        Saturation values, same shape as spend.
        Type: float64 ndarray or float, depending on input.
        When called with PyMC variables, returns PyMC tensor.
    
    Raises:
        ValueError: If spend has negative values (numpy context only).
        ValueError: If gamma ≤ 0 (numpy context only).
        RuntimeWarning: If numerical overflow occurs (handled by numpy).
    
    Examples:
        >>> hill_saturation(100, alpha=1.0, gamma=150)
        # Linear: 100 / (150 + 100) = 0.4
        
        >>> hill_saturation([0, 50, 100, 200], alpha=1.0, gamma=100)
        # array([0.  , 0.33, 0.5 , 0.67])
        
        >>> spend = np.array([[100, 200], [300, 50]])  # (2 weeks, 2 channels)
        >>> alpha = np.array([0.8, 1.2])
        >>> gamma = np.array([150, 100])
        >>> hill_saturation(spend, alpha, gamma)  # Broadcasting works
    """
    # Check if inputs are PyMC/PyTensor variables (works in PyMC model context)
    # If so, use basic arithmetic which PyMC's tensor backend supports
    try:
        import pytensor
        is_pymc_context = False
        
        # Check if any input is a PyTensor Variable (includes PyMC random variables)
        if isinstance(alpha, pytensor.graph.basic.Variable) or \
           isinstance(gamma, pytensor.graph.basic.Variable):
            is_pymc_context = True
        
        if is_pymc_context:
            # PyMC context: Use numerically stable form that PyMC tensor ops support
            # saturation = spend^alpha / (gamma^alpha + spend^alpha)
            return (spend ** alpha) / (gamma ** alpha + spend ** alpha)
    except (ImportError, AttributeError, TypeError):
        # PyTensor not available or inputs don't match - continue to numpy path
        pass
    
    # Numpy context: Validate inputs and use numerically stable computation
    spend_arr = np.asarray(spend, dtype=np.float64)
    alpha_arr = np.asarray(alpha, dtype=np.float64)
    gamma_arr = np.asarray(gamma, dtype=np.float64)
    
    # Check for invalid values
    if np.any(spend_arr < 0):
        raise ValueError(f"spend must be non-negative. Got min value: {spend_arr.min()}")
    
    if np.any(gamma_arr <= 0):
        raise ValueError(f"gamma must be positive. Got min value: {gamma_arr.min()}")
    
    # Compute Hill saturation
    # Use log-space arithmetic to avoid numerical overflow at high spend
    # saturation = spend^alpha / (gamma^alpha + spend^alpha)
    #            = 1 / (1 + (gamma/spend)^alpha)  when spend > 0
    #            = 0 when spend == 0
    
    # Handle zero spend case explicitly
    saturation = np.zeros_like(spend_arr)
    
    nonzero_mask = spend_arr > 0
    if np.any(nonzero_mask):
        # For non-zero spend, use numerically stable computation
        # This avoids overflow when spend^alpha is very large
        ratio = gamma_arr / np.where(nonzero_mask, spend_arr, 1.0)
        ratio_power = np.power(ratio, alpha_arr, where=nonzero_mask, out=np.ones_like(ratio))
        saturation = np.where(nonzero_mask, 1.0 / (1.0 + ratio_power), 0.0)
    
    # Return scalar if input was scalar
    if saturation.shape == ():
        return float(saturation)
    
    return saturation