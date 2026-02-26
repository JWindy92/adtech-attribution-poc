import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class SyntheticMMMDataGenerator:
    def __init__(self, n_weeks=52, seed=42):
        self.n_weeks = n_weeks
        self.seed = seed
        np.random.seed(seed)
        
        self.channel_params = {
            'ctv_spend': {
                'base_spend': 80000,
                'variance': 0.15,
                'adstock_decay': 0.7,
                'adstock_lag': 8,
                'saturation_alpha': 1.2,
                'saturation_gamma': 100000,
                'roi': 0.025
            },
            'linear_tv_spend': {
                'base_spend': 110000,
                'variance': 0.12,
                'adstock_decay': 0.6,
                'adstock_lag': 6,
                'saturation_alpha': 1.0,
                'saturation_gamma': 150000,
                'roi': 0.018
            },
            'search_spend': {
                'base_spend': 35000,
                'variance': 0.20,
                'adstock_decay': 0.3,
                'adstock_lag': 2,
                'saturation_alpha': 1.5,
                'saturation_gamma': 40000,
                'roi': 0.045
            },
            'social_spend': {
                'base_spend': 20000,
                'variance': 0.25,
                'adstock_decay': 0.5,
                'adstock_lag': 4,
                'saturation_alpha': 1.3,
                'saturation_gamma': 25000,
                'roi': 0.035
            }
        }
    
    def generate_spend(self, channel, trend=0.02):
        params = self.channel_params[channel]
        base = params['base_spend']
        variance = params['variance']
        
        weeks = np.arange(self.n_weeks)
        trend_component = base * trend * (weeks / self.n_weeks)
        seasonal_component = base * 0.1 * np.sin(2 * np.pi * weeks / 52)
        random_component = np.random.normal(0, base * variance, self.n_weeks)
        
        spend = base + trend_component + seasonal_component + random_component
        return np.maximum(spend, 0)
    
    def apply_adstock(self, x, decay, max_lag):
        adstocked = np.zeros_like(x)
        for t in range(len(x)):
            for lag in range(min(t + 1, max_lag)):
                adstocked[t] += x[t - lag] * (decay ** lag)
        return adstocked
    
    def apply_saturation(self, x, alpha, gamma):
        return (x ** alpha) / (gamma ** alpha + x ** alpha)
    
    def generate_conversions(self, spend_data, baseline=500, noise_std=50):
        conversions = np.full(self.n_weeks, baseline, dtype=float)
        
        for channel, spend in spend_data.items():
            params = self.channel_params[channel]
            
            adstocked = self.apply_adstock(
                spend, 
                params['adstock_decay'], 
                params['adstock_lag']
            )
            
            saturated = self.apply_saturation(
                adstocked,
                params['saturation_alpha'],
                params['saturation_gamma']
            )
            
            channel_contribution = saturated * params['roi'] * params['saturation_gamma']
            conversions += channel_contribution
        
        weeks = np.arange(self.n_weeks)
        seasonal_boost = 200 * np.sin(2 * np.pi * weeks / 52 - np.pi/2)
        conversions += seasonal_boost
        
        noise = np.random.normal(0, noise_std, self.n_weeks)
        conversions += noise
        
        return np.maximum(conversions, 0)
    
    def generate(self, start_date='2024-01-01'):
        dates = pd.date_range(start=start_date, periods=self.n_weeks, freq='W')
        
        spend_data = {}
        for channel in self.channel_params.keys():
            spend_data[channel] = self.generate_spend(channel)
        
        conversions = self.generate_conversions(spend_data)
        
        df = pd.DataFrame({
            'week': dates,
            **spend_data,
            'conversions': conversions
        })
        
        return df


def main():
    print("Generating realistic MMM synthetic data...")
    print("=" * 60)
    
    generator = SyntheticMMMDataGenerator(n_weeks=104, seed=42)
    df = generator.generate(start_date='2024-01-01')
    
    df.to_csv('synthetic_mmm_data.csv', index=False)
    
    print(f"\n✓ Generated {len(df)} weeks of data")
    print(f"  Date range: {df['week'].min()} to {df['week'].max()}")
    print(f"\n  Total spend by channel:")
    for col in ['ctv_spend', 'linear_tv_spend', 'search_spend', 'social_spend']:
        print(f"    {col}: ${df[col].sum():,.0f}")
    print(f"\n  Total conversions: {df['conversions'].sum():,.0f}")
    print(f"  Average conversions/week: {df['conversions'].mean():,.0f}")
    
    print(f"\n✓ Saved to synthetic_mmm_data.csv")
    print("\nData characteristics:")
    print("  • Adstock effects (carryover varies by channel)")
    print("  • Saturation (diminishing returns)")
    print("  • Seasonality (annual patterns)")
    print("  • Baseline conversions")
    print("  • Realistic noise")
    print("=" * 60)


if __name__ == "__main__":
    main()
