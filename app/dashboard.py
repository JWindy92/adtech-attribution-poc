import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.pipeline import Pipeline
from src.datasources.csv import CSVDataSource
from src.transformers.passthrough import PassthroughTransformer
from src.models.spend_proportional import SpendProportionalModel
from src.optimizers.simple import SimpleOptimizer


@st.cache_data
def load_pipeline_data():
    data_dir = Path(__file__).parent.parent / "data"
    
    pipeline = Pipeline(
        data_source=CSVDataSource(str(data_dir)),
        transformer=PassthroughTransformer(),
        attribution_model=SpendProportionalModel(),
        optimizer=SimpleOptimizer()
    )
    
    results = pipeline.run("dummy_media_data.csv")
    return results['raw_data'], results['metrics'], results['optimization']


def main():
    st.set_page_config(page_title="MMM Dashboard", page_icon="📊", layout="wide")
    
    st.title("🎯 Media Mix Modeling Dashboard")
    st.markdown("**Cross-Channel Attribution & Budget Optimization**")
    
    df, metrics, optimization_results = load_pipeline_data()
    
    st.header("Channel Attribution (Spend-Proportional)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(metrics, x='channel', y='attribution_pct', 
                     title='Attribution by Channel')
        fig.update_layout(yaxis_title='Attribution %', xaxis_title='Channel')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(metrics, x='channel', y='cost_per_conversion',
                     title='Cost per Conversion')
        fig.update_layout(yaxis_title='Cost per Conversion', xaxis_title='Channel')
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(metrics, use_container_width=True)
    
    st.header("Budget Optimization Recommendations")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Current', x=optimization_results['channel'], 
                         y=optimization_results['current_spend']))
    fig.add_trace(go.Bar(name='Optimal', x=optimization_results['channel'], 
                         y=optimization_results['optimal_spend']))
    fig.update_layout(barmode='group', title='Current vs Optimal Budget Allocation',
                     yaxis_title='Spend ($)', xaxis_title='Channel')
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(optimization_results, use_container_width=True)
    
    st.info("💡 Note: Currently using spend-proportional attribution. Bayesian MMM will be added in Stage 3.")


if __name__ == "__main__":
    main()
