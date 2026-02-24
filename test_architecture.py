from src.pipeline import Pipeline
from src.datasources.csv import CSVDataSource
from src.datasources.base import DataSource
from src.transformers.passthrough import PassthroughTransformer
from src.models.spend_proportional import SpendProportionalModel
from src.optimizers.simple import SimpleOptimizer
import pandas as pd
from typing import List


class MockDataSource(DataSource):
    def load_data(self, identifier: str) -> pd.DataFrame:
        return pd.DataFrame({
            'week': pd.date_range('2024-01-01', periods=10, freq='W'),
            'ctv_spend': [10000] * 10,
            'social_spend': [5000] * 10,
            'conversions': [100] * 10
        })
    
    def get_media_columns(self, df: pd.DataFrame) -> List[str]:
        return ['ctv_spend', 'social_spend']


def test_with_mock():
    print("Testing with Mock Data Source:")
    pipeline = Pipeline(
        data_source=MockDataSource(),
        transformer=PassthroughTransformer(),
        attribution_model=SpendProportionalModel(),
        optimizer=SimpleOptimizer()
    )
    
    results = pipeline.run("mock")
    print(results['metrics'])
    print("\n✓ Mock data source works!\n")


def test_with_csv():
    print("Testing with CSV Data Source:")
    pipeline = Pipeline(
        data_source=CSVDataSource("data"),
        transformer=PassthroughTransformer(),
        attribution_model=SpendProportionalModel(),
        optimizer=SimpleOptimizer()
    )
    
    results = pipeline.run("dummy_media_data.csv")
    print(f"✓ Loaded {len(results['raw_data'])} rows from CSV\n")


if __name__ == "__main__":
    test_with_mock()
    test_with_csv()
    
    print("=" * 60)
    print("Pluggable Architecture Demo Complete")
    print("=" * 60)
    print("\nYou can now easily swap:")
    print("  • CSVDataSource → DatabricksDataSource")
    print("  • SpendProportionalModel → BayesianMMMModel")
    print("  • SimpleOptimizer → ScipyOptimizer")
    print("\nJust pass different implementations to Pipeline()!")
