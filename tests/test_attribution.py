from src.datasources.csv import CSVDataSource
from src.transformers.passthrough import PassthroughTransformer
from src.models.spend_proportional import SpendProportionalModel


def main():
    data_source = CSVDataSource("data")
    transformer = PassthroughTransformer()
    model = SpendProportionalModel()
    
    df = data_source.load_data("dummy_media_data.csv")
    media_columns = data_source.get_media_columns(df)
    
    transformed_df = transformer.apply_transforms(df, media_columns)
    
    metrics = model.fit(transformed_df, media_columns)
    
    print("\nSpend-Proportional Attribution:")
    print(metrics[['channel', 'attribution_pct', 'attributed_conversions', 'cost_per_conversion']].to_string(index=False))


if __name__ == "__main__":
    main()
