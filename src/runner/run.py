import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.transformers import PassthroughTransformer
from src.models import SpendProportionalModel
from src.datasources.csv import CSVDataSource
from src.optimizers import ScipyOptimizer

def main():
    csv_dir = Path(__file__).parent.parent.parent / "data"
    dataSource = CSVDataSource(str(csv_dir))
    raw_data = dataSource.load_data("synthetic_mmm_data.csv")
    media_columns = dataSource.get_media_columns(raw_data)
    print(raw_data.head())

    transformer = PassthroughTransformer()
    transformed_data = transformer.apply_transforms(raw_data, media_columns) 
    print(transformed_data.head())

    model = SpendProportionalModel()
    metrics = model.fit(transformed_data, media_columns, raw_df=raw_data)

    optimizer = ScipyOptimizer()
    total_budget = raw_data[media_columns].sum().sum()
    optimization_results = optimizer.optimize(metrics, total_budget)

    print(optimization_results.head())
if __name__ == "__main__":
    main()