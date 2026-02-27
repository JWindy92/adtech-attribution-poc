import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib


class EventStreamGenerator:
    def __init__(self, n_weeks=4, impressions_per_week=10000, conversion_rate=0.02, seed=42):
        self.n_weeks = n_weeks
        self.impressions_per_week = impressions_per_week
        self.conversion_rate = conversion_rate
        np.random.seed(seed)
        
        self.channels = ['ctv', 'linear_tv', 'search', 'social']
        self.channel_weights = [0.35, 0.40, 0.15, 0.10]
        self.channel_cpc = {'ctv': 0.025, 'linear_tv': 0.020, 'search': 1.50, 'social': 0.85}
    
    def generate_user_id(self, index):
        return f"user_{hashlib.md5(str(index).encode()).hexdigest()[:8]}"
    
    def generate_impressions(self, start_date='2024-01-01'):
        impressions = []
        start = datetime.strptime(start_date, '%Y-%m-%d')
        
        for week in range(self.n_weeks):
            week_start = start + timedelta(weeks=week)
            
            for i in range(self.impressions_per_week):
                channel = np.random.choice(self.channels, p=self.channel_weights)
                user_id = self.generate_user_id(np.random.randint(0, self.impressions_per_week // 2))
                
                timestamp = week_start + timedelta(
                    days=np.random.randint(0, 7),
                    hours=np.random.randint(0, 24),
                    minutes=np.random.randint(0, 60)
                )
                
                impressions.append({
                    'event_id': f"imp_{week}_{i}",
                    'user_id': user_id,
                    'timestamp': timestamp,
                    'channel': channel,
                    'spend': self.channel_cpc[channel]
                })
        
        return pd.DataFrame(impressions)
    
    def generate_conversions(self, impressions_df):
        conversions = []
        users = impressions_df['user_id'].unique()
        n_converters = int(len(users) * self.conversion_rate)
        converters = np.random.choice(users, n_converters, replace=False)
        
        for idx, user in enumerate(converters):
            user_imps = impressions_df[impressions_df['user_id'] == user]
            last_imp = user_imps['timestamp'].max()
            
            conversion_time = last_imp + timedelta(
                hours=np.random.randint(1, 48)
            )
            
            conversions.append({
                'conversion_id': f"conv_{idx}",
                'user_id': user,
                'timestamp': conversion_time,
                'value': np.random.uniform(50, 500)
            })
        
        return pd.DataFrame(conversions)
    
    def aggregate_to_weekly(self, impressions_df, conversions_df):
        impressions_df['week'] = pd.to_datetime(impressions_df['timestamp']).dt.to_period('W').dt.start_time
        conversions_df['week'] = pd.to_datetime(conversions_df['timestamp']).dt.to_period('W').dt.start_time
        
        spend_by_channel = impressions_df.pivot_table(
            index='week',
            columns='channel',
            values='spend',
            aggfunc='sum',
            fill_value=0
        )
        
        spend_by_channel.columns = [f"{col}_spend" for col in spend_by_channel.columns]
        
        conversions_agg = conversions_df.groupby('week').size().reset_index(name='conversions')
        
        weekly = spend_by_channel.reset_index().merge(conversions_agg, on='week', how='left')
        weekly['conversions'] = weekly['conversions'].fillna(0).astype(int)
        
        return weekly


def main():
    print("=" * 60)
    print("EVENT STREAM EXAMPLE - Shows Full Data Landscape")
    print("=" * 60)
    
    generator = EventStreamGenerator(n_weeks=4, impressions_per_week=5000, seed=42)
    
    print("\n[1/3] Generating impression events...")
    impressions = generator.generate_impressions()
    impressions.to_csv('event_impressions_sample.csv', index=False)
    print(f"  ✓ Generated {len(impressions):,} impression events")
    print(f"\n  Sample impressions:")
    print(impressions.head(3).to_string(index=False))
    
    print("\n[2/3] Generating conversion events...")
    conversions = generator.generate_conversions(impressions)
    conversions.to_csv('event_conversions_sample.csv', index=False)
    print(f"  ✓ Generated {len(conversions):,} conversion events")
    print(f"\n  Sample conversions:")
    print(conversions.head(3).to_string(index=False))
    
    print("\n[3/3] Aggregating to weekly summaries (for MMM)...")
    weekly = generator.aggregate_to_weekly(impressions, conversions)
    weekly.to_csv('weekly_aggregated_sample.csv', index=False)
    print(f"  ✓ Aggregated to {len(weekly)} weeks")
    print(f"\n  Weekly summary:")
    print(weekly.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("Data Landscape Generated:")
    print("  • event_impressions_sample.csv (MTA uses this)")
    print("  • event_conversions_sample.csv (MTA uses this)")
    print("  • weekly_aggregated_sample.csv (MMM uses this)")
    print("=" * 60)


if __name__ == "__main__":
    main()
