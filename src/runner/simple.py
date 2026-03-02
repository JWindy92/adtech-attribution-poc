import pandas as pd
import numpy as np
from scipy.signal import lfilter

# 1. Setup your input data
data = {
    'TV': [1000, 0, 0, 500, 0, 0],
    'Social': [200, 200, 200, 200, 0, 0],
    'Search': [50, 300, 50, 300, 50, 0]
}
df = pd.DataFrame(data, index=pd.date_range("2024-01-01", periods=6, freq="W"))

# 2. Define decay rates for each channel (0.0 to 1.0)
# Higher alpha = longer lasting effect
alphas = {
    'TV': 0.8,      # Long memory
    'Social': 0.4,  # Medium memory
    'Search': 0.1   # Short memory (immediate intent)
}

# 3. Apply the transformation
def adstock_transform(df, alpha_dict):
    adstocked_df = pd.DataFrame(index=df.index)
    
    for channel, alpha in alpha_dict.items():
        if channel in df.columns:
            # Apply recursive filter: y[t] = x[t] + alpha * y[t-1]
            adstocked_df[f'{channel}_adstock'] = lfilter([1], [1, -alpha], df[channel])
            
    return adstocked_df

# Run and combine
df_adstocked = adstock_transform(df, alphas)
result = pd.concat([df, df_adstocked], axis=1)
print(result.head())