#!/usr/bin/env python3

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from src.datasources.csv import CSVDataSource
from src.transformers.adstock_saturation import AdstockSaturationTransformer
from src.models.bayesian_mmm import BayesianMMMModel
from src.optimizers.scipy import ScipyOptimizer
from src.pipeline import Pipeline


def main():
    print("\n" + "=" * 70)
    print("BAYESIAN MMM - FULL PIPELINE")
    print("=" * 70)
    
    print("\n📋 Configuration:")
    print("  • Data: synthetic_mmm_data.csv (104 weeks)")
    print("  • Transformer: Adstock + Saturation")
    print("  • Model: Bayesian Hierarchical Regression (PyMC)")
    print("  • Optimizer: SciPy SLSQP")
    
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
    
    print("\n🔧 Initializing pipeline...")
    pipeline = Pipeline(
        data_source=CSVDataSource('data'),
        transformer=AdstockSaturationTransformer(adstock_params, saturation_params),
        attribution_model=BayesianMMMModel(samples=2000, tune=1000),
        optimizer=ScipyOptimizer()
    )
    
    print("\n🚀 Running pipeline (this will take 1-2 minutes)...")
    print("  [1/4] Loading data...")
    results = pipeline.run('synthetic_mmm_data.csv')
    print(f"        ✓ Loaded {len(pipeline.raw_data)} weeks of data")
    
    print("  [2/4] Applying transformations...")
    print("        ✓ Adstock applied (carryover effects)")
    print("        ✓ Saturation applied (diminishing returns)")
    
    print("  [3/4] Bayesian MCMC sampling...")
    print("        ✓ Posterior distributions sampled")
    
    print("  [4/4] Budget optimization...")
    optimization = results['optimization']
    total_budget = results['metrics']['total_spend'].sum()
    print("        ✓ Optimal allocation computed")
    
    print("\n" + "=" * 70)
    print("ATTRIBUTION RESULTS")
    print("=" * 70)
    print("\n" + results['metrics'].to_string(index=False))
    
    print("\n" + "=" * 70)
    print("POSTERIOR SUMMARY (Beta Coefficients)")
    print("=" * 70)
    if hasattr(pipeline.attribution_model, 'get_posterior_summary'):
        posterior = pipeline.attribution_model.get_posterior_summary()
        print("\n" + posterior.to_string())
    
    print("\n" + "=" * 70)
    print("BUDGET OPTIMIZATION")
    print("=" * 70)
    print(f"\nTotal Budget: ${total_budget:,.0f}\n")
    print(optimization[['channel', 'current_allocation', 'optimized_allocation', 'change_pct']].to_string(index=False))
    
    print("\n" + "=" * 70)
    print("✓ Pipeline complete!")
    print("=" * 70)
    print("\n💡 Next steps:")
    print("  • Run dashboard: streamlit run app/dashboard_bayesian.py")
    print("  • Adjust parameters in this script and re-run")
    print("  • Explore posterior distributions in dashboard")
    print()
    metrics_df = pd.DataFrame(results['metrics'])
    metrics_df.to_csv('bayesian_mmm_metrics.csv', index=False)


if __name__ == "__main__":
    main()
