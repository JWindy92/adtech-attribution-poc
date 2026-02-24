from src.datasources.csv import CSVDataSource
from src.transformers.passthrough import PassthroughTransformer
from src.models.spend_proportional import SpendProportionalModel
from src.optimizers.simple import SimpleOptimizer
from src.pipeline import Pipeline


def main():
    pipeline = Pipeline(
        data_source=CSVDataSource("data"),
        transformer=PassthroughTransformer(),
        attribution_model=SpendProportionalModel(),
        optimizer=SimpleOptimizer()
    )
    
    results = pipeline.run("dummy_media_data.csv")
    
    print("Loaded:", len(results['raw_data']), "rows")
    print("\nFirst 5 rows:")
    print(results['raw_data'].head())
    print("\nColumns:", list(results['raw_data'].columns))


if __name__ == "__main__":
    main()
