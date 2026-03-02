"""
Scale-adaptive prior calculation for Bayesian MMM.

The key principle: Priors for saturation parameters (gamma) should be centered
on the observed data scale, enabling the model to work with any spend magnitude
without hardcoding.

This is industry-standard practice from Google's Lightweight MMM research.
"""

import numpy as np
from typing import Tuple

#! Deprecated
def calculate_gamma_prior(raw_spend_data: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Calculate data-driven priors for gamma (half-saturation point parameter).
    
    Gamma represents the spend level at which saturation reaches 50%.
    Different channels have different typical spend levels in the data.
    This function centers the prior around those observed levels.
    
    Theory:
        - Gamma is always positive and log-distributed in practice
        - LogNormal distribution is appropriate for positive parameters
        - Prior mean (in log space) = log(typical spend per channel)
        - Prior std (in log space) = 1.0 allows ~1-2 orders of magnitude variation
    
    Args:
        raw_spend_data: Shape (n_weeks, n_channels)
            Raw (not transformed) weekly spend per channel.
            Must have ≥ 2 observations per channel.
            All values must be ≥ 0.
    
    Returns:
        gamma_mu: Shape (n_channels,) dtype float64
            Log-scale mean for LogNormal prior.
            gamma_mu[ch] = log(mean_spend[ch])
        
        gamma_sigma: float, value 1.0
            Log-scale standard deviation for LogNormal prior.
            Fixed at 1.0 (industry standard, allows moderate uncertainty).
    
    Raises:
        ValueError: If spend_data has < 2 observations per channel
        ValueError: If spend_data has negative values
        ValueError: If any channel is all zeros (mean=0, can't take log)
    
    Example:
        >>> spend_data = np.array([
        ...     [100000, 200000],
        ...     [150000, 250000],
        ...     [120000, 180000],
        ... ])  # 3 weeks, 2 channels
        >>> gamma_mu, gamma_sigma = calculate_gamma_prior(spend_data)
        >>> gamma_mu  # log of mean spend per channel
        array([11.71, 12.27])
        >>> gamma_sigma
        1.0
    
    Notes:
        - Total budget scale doesn't matter; the function adapts automatically
        - Works with any spend distribution (uniform, exponential, etc.)
        - No hardcoded constants except gamma_sigma=1.0 (industry standard)
    """
    # Validate input
    spend_data = np.asarray(raw_spend_data, dtype=np.float64)
    
    if spend_data.ndim != 2:
        raise ValueError(
            f"raw_spend_data must be 2D (n_weeks, n_channels). "
            f"Got shape: {spend_data.shape}"
        )
    
    n_weeks, n_channels = spend_data.shape
    
    if n_weeks < 2:
        raise ValueError(
            f"raw_spend_data must have ≥ 2 weeks of data. Got {n_weeks} weeks."
        )
    
    if np.any(spend_data < 0):
        raise ValueError(
            f"raw_spend_data must be non-negative. "
            f"Got min value: {spend_data.min()}"
        )
    
    # Calculate per-channel mean spend
    mean_spend = spend_data.mean(axis=0)  # Shape: (n_channels,)
    
    # Check for all-zero channels (can't take log of zero)
    if np.any(mean_spend == 0):
        zero_channels = np.where(mean_spend == 0)[0]
        raise ValueError(
            f"Channels {zero_channels} have zero total spend. "
            f"Cannot compute prior for zero-spend channels."
        )
    
    # Calculate gamma prior in log space
    gamma_mu = np.log(mean_spend)  # Shape: (n_channels,)
    
    # Industry standard: sigma=1.0 in log space
    # This allows approximately 1-2 orders of magnitude variation
    # e.g., if mean is 100K, prior covers roughly 10K to 1M
    gamma_sigma = 1.0
    
    return gamma_mu, gamma_sigma