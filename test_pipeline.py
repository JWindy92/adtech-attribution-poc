from src.pipeline import Pipeline
from src.datasources.csv import CSVDataSource
from src.transformers.passthrough import PassthroughTransformer
from src.models.spend_proportional import SpendProportionalModel
from src.optimizers.simple import SimpleOptimizer


def main():
    print("=" * 60)
    print("FULL PIPELINE TEST - Stage 2 Complete")
    print("=" * 60)
    
    pipeline = Pipeline(
        data_source=CSVDataSource("data"),
        transformer=PassthroughTransformer(),
        attribution_model=SpendProportionalModel(),
        optimizer=SimpleOptimizer()
    )
    
    print("\nRunning pipeline with pluggable components...")
    results = pipeline.run("dummy_media_data.csv")
    
    print(f"\n✓ Loaded {len(results['raw_data'])} rows")
    print("\nChannel Metrics:")
    print(results['metrics'].to_string(index=False))
    
    print("\nOptimization Results:")
    print(results['optimization'].to_string(index=False))
    
    print("\n" + "=" * 60)
    print("✅ STAGE 2 COMPLETE - Pluggable architecture working!")
    print("=" * 60)
    print("\nArchitecture benefits:")
    print("  • Swap CSV for Databricks later")
    print("  • Swap SpendProportional for BayesianMMM later")
    print("  • Easy to mock for testing")
    print("\nNext: Run 'streamlit run app/dashboard.py' to view dashboard")


if __name__ == "__main__":
    main()
