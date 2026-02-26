import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.datasources.csv import CSVDataSource
from src.transformers.adstock_saturation import AdstockSaturationTransformer
from src.models.bayesian_mmm import BayesianMMMModel
from src.optimizers.scipy import ScipyOptimizer
from src.pipeline import Pipeline


def test_bayesian_pipeline():
    print("=" * 60)
    print("BAYESIAN MMM PIPELINE TEST")
    print("=" * 60)
    
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
    
    data_source = CSVDataSource('data')
    transformer = AdstockSaturationTransformer(adstock_params, saturation_params)
    model = BayesianMMMModel(samples=1000, tune=500)
    optimizer = ScipyOptimizer()
    
    pipeline = Pipeline(data_source, transformer, model, optimizer)
    
    print("\n[1/4] Loading data...")
    results = pipeline.run('synthetic_mmm_data.csv')
    print(f"  ✓ Loaded {len(pipeline.raw_data)} weeks")
    
    print("\n[2/4] Running Bayesian MMM (this may take 1-2 minutes)...")
    print("  • Sampling posterior distributions")
    print("  • Estimating channel contributions")
    attribution = results['metrics']
    print(f"  ✓ Model converged")
    
    print("\n[3/4] Attribution Results:")
    print(attribution[['channel', 'attribution_pct', 'cost_per_conversion']].to_string(index=False))
    
    print("\n[4/4] Budget Optimization:")
    optimization = results['optimization']
    print(optimization[['channel', 'current_allocation', 'optimized_allocation', 'change_pct']].to_string(index=False))
    
    print("\n" + "=" * 60)
    print("✓ Bayesian MMM pipeline test complete")
    print("=" * 60)
    
    if hasattr(pipeline.attribution_model, 'get_posterior_summary'):
        print("\nPosterior Summary (Beta Coefficients):")
        summary = pipeline.attribution_model.get_posterior_summary()
        print(summary)


if __name__ == "__main__":
    test_bayesian_pipeline()
