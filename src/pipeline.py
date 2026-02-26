from src.core.interfaces import Optimizer, AttributionModel, DataSource, Transformer

class Pipeline:
    def __init__(
        self,
        data_source: DataSource,
        transformer: Transformer,
        attribution_model: AttributionModel,
        optimizer: Optimizer
    ):
        self.data_source = data_source
        self.transformer = transformer
        self.attribution_model = attribution_model
        self.optimizer = optimizer
        self.raw_data = None
        self.transformed_data = None
        self.metrics = None
        self.optimization_results = None
    
    def run(self, data_identifier: str):
        self.raw_data = self.data_source.load_data(data_identifier)
        media_columns = self.data_source.get_media_columns(self.raw_data)
        
        self.transformed_data = self.transformer.apply_transforms(self.raw_data, media_columns)
        
        self.metrics = self.attribution_model.fit(self.transformed_data, media_columns, raw_df=self.raw_data)
        
        total_budget = self.raw_data[media_columns].sum().sum()
        self.optimization_results = self.optimizer.optimize(self.metrics, total_budget)
        
        return {
            'raw_data': self.raw_data,
            'metrics': self.metrics,
            'optimization': self.optimization_results
        }
