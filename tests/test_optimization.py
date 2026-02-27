import pandas as pd
import numpy as np
from src.config import APP_CONFIG

metrics = pd.DataFrame(
    {
        "channel": ["ctv_spend", "linear_tv_spend", "search_spend", "social_spend"],
        "total_spend": [8242012.0, 11645438.0, 3722935.0, 2125986.0],
        "attributed_conversions": [114132.0, 33199.0, 45261.0, 22493.0],
    }
)

# Params where gamma is in the same order of magnitude as total_spend
APP_CONFIG.saturation_params = {
    "ctv_spend": {"alpha": 2.0, "gamma": 8000000.0},
    "linear_tv_spend": {"alpha": 2.0, "gamma": 12000000.0},
    "search_spend": {"alpha": 2.0, "gamma": 3500000.0},
    "social_spend": {"alpha": 2.0, "gamma": 2000000.0},
}

total_budget = sum(metrics["total_spend"])
