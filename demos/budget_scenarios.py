#!/usr/bin/env python3
"""
Budget Scenario Demo - Identify advertiser upsell opportunities and saturation points

Use Case: Analyze how much additional spend our inventory can absorb before 
diminishing returns kick in. Helps sales identify upsell headroom.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.datasources.csv import CSVDataSource
from src.transformers.adstock_saturation import AdstockSaturationTransformer
from src.models.bayesian_mmm import BayesianMMMModel
from src.optimizers.scipy import ScipyOptimizer
from src.pipeline import Pipeline
import pandas as pd


def run_scenario(budget_level, budget_amount):
    """Run optimization for a specific budget level"""
    
    adstock_params = {
        'ctv_spend': {'decay': 0.7, 'max_lag': 8},
        'linear_tv_spend': {'decay': 0.6, 'max_lag': 6},
        'search_spend': {'decay': 0.3, 'max_lag': 2},
        'social_spend': {'decay': 0.5, 'max_lag': 4}
    }
    
    saturation_params = {
        'ctv_spend': {'alpha': 1.2, 'gamma': 100000},
        'linear_tv_spend': {'alpha': 1.0, 'gamma': 150000},
        'search_spend': {'alpha': 1.5, 'gamma': 40000},
        'social_spend': {'alpha': 1.3, 'gamma': 25000}
    }
    
    pipeline = Pipeline(
        data_source=CSVDataSource('data'),
        transformer=AdstockSaturationTransformer(adstock_params, saturation_params),
        attribution_model=BayesianMMMModel(samples=1000, tune=500),
        optimizer=ScipyOptimizer()
    )
    
    results = pipeline.run('synthetic_mmm_data.csv')
    optimization = pipeline.optimizer.optimize(results['metrics'], budget_amount)
    
    return {
        'level': budget_level,
        'budget': budget_amount,
        'allocation': optimization[['channel', 'optimized_allocation']],
        'metrics': results['metrics']
    }


def main():
    print("\n" + "=" * 80)
    print("ADVERTISER SPEND SCENARIO ANALYSIS - Upsell Headroom & Saturation Detection")
    print("=" * 80)
    
    current_budget = 24_500_000  # Current advertiser spend on our inventory
    
    scenarios = [
        ("Current Spend", current_budget),
        ("Upsell +20% ($5M)", current_budget * 1.20),
        ("Upsell +50% ($12M)", current_budget * 1.50),
    ]
    
    print("\n📊 Running scenarios (this will take ~2 minutes)...")
    print("    Simulating advertiser spend levels on our inventory...\n")
    
    results = []
    for level, budget in scenarios:
        print(f"  Running {level} scenario (${budget:,.0f})...")
        result = run_scenario(level, budget)
        results.append(result)
    
    print("\n" + "=" * 80)
    print("SCENARIO COMPARISON")
    print("=" * 80)
    
    for i, result in enumerate(results):
        print(f"\n### Scenario {i+1}: {result['level']} - ${result['budget']:,.0f}")
        print("\nOptimal Allocation:")
        
        allocation = result['allocation'].copy()
        allocation['optimized_allocation'] = allocation['optimized_allocation'].apply(lambda x: f"${x:,.0f}")
        print(allocation.to_string(index=False))
        
        if i > 0:
            prev = results[i-1]['allocation']
            curr = result['allocation']
            
            print("\nIncremental Changes from Previous:")
            for j, row in curr.iterrows():
                channel = row['channel']
                prev_val = prev[prev['channel'] == channel]['optimized_allocation'].values[0]
                curr_val = row['optimized_allocation']
                diff = curr_val - prev_val
                pct = (diff / prev_val) * 100 if prev_val > 0 else 0
                print(f"  {channel}: ${diff:+,.0f} ({pct:+.1f}%)")
    
    print("\n" + "=" * 80 + " - Sales & Pricing Strategy")
    print("=" * 80)
    
    base_alloc = results[0]['allocation'].set_index('channel')['optimized_allocation']
    high_alloc = results[-1]['allocation'].set_index('channel')['optimized_allocation']
    
    increases = high_alloc - base_alloc
    top_channel = increases.idxmax()
    top_increase = increases.max()
    
    print(f"\n✓ Upsell Priority: {top_channel}")
    print(f"  → Can absorb ${top_increase:,.0f} incremental spend before saturation")
    print(f"  → Sales talking point: 'You have headroom for {(top_increase/base_alloc[top_channel]*100):.0f}% more spend on {top_channel}'")
    
    print(f"\n✓ Diminishing Returns Threshold:")
    margin_1 = (results[1]['budget'] - results[0]['budget'])
    margin_2 = (results[2]['budget'] - results[1]['budget'])
    
    print(f"  → First ${margin_1/1e6:.1f}M: High efficiency (strong upsell case)")
    print(f"  → Next ${margin_2/1e6:.1f}M: Declining efficiency (saturation setting in)")
    print(f"  → Insight: Don't push advertisers past +20-30% without creative refresh")
    
    print(f"\n✓ Pricing Strategy:")
    print(f"  → Charge premium for {top_channel} - it has most headroom")
    print(f"  → Consider volume discounts beyond optimal point to prevent churn")
    
    print("\n" + "=" * 80)
    print("💡 Internal Use Case: Sales Enablement")
    print("=" * 80)
    print("""
This analysis helps answer (INTERNAL ONLY - not shared with advertisers):
  • "Can we upsell Advertiser X without hitting diminishing returns?"
  • "Which inventory (CTV vs Linear) has the most headroom?"
  • "At what spend level should we warn about saturation?"
  • "How do we price inventory based on marginal ROI?"
  
Example Sales Use:
  Advertiser currently spends $10M on Linear TV.
  → Model shows Linear can absorb $12M before saturation.
  → Sales pitch: "Data shows you have 20% headroom on Linear before diminishing returns."
  → Upsell $2M with confidence.
  
Next steps:
  • Run per-advertiser to personalize recommendations
  • Add seasonal adjustments (Q4 holiday capacity)
  • Include creative fatigue (diminishing returns from same ad)
  • Integrate with yield management pricing
  • Include constraints (e.g., min spend per channel for brand presence)
    """)


if __name__ == "__main__":
    main()