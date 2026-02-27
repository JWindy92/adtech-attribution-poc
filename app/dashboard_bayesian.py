import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.pipeline import Pipeline
from src.datasources.csv import CSVDataSource
from src.transformers import AdstockTransformer, SaturationTransformer, PassthroughTransformer
from src.models.spend_proportional import SpendProportionalModel
from src.models.bayesian_mmm import BayesianMMMModel
from src.optimizers.simple import SimpleOptimizer
from src.optimizers.scipy import ScipyOptimizer
import src.config as config


@st.cache_data
def load_simple_pipeline():
    data_dir = Path(__file__).parent.parent / "data"
    
    pipeline = Pipeline(
        data_source=CSVDataSource(str(data_dir)),
        transformer=PassthroughTransformer(),
        attribution_model=SpendProportionalModel(),
        optimizer=SimpleOptimizer()
    )
    
    results = pipeline.run("synthetic_mmm_data.csv")
    return results


@st.cache_resource
def load_bayesian_pipeline():
    data_dir = Path(__file__).parent.parent / "data"

    adstock = AdstockTransformer(adstock_params=config.DEFAULT_ADSTOCK_PARAMS)
    saturation = SaturationTransformer(saturation_params=config.DEFAULT_SATURATION_PARAMS)

    transformer = adstock.then(saturation)
    
    pipeline = Pipeline(
        data_source=CSVDataSource(str(data_dir)),
        transformer=transformer,
        attribution_model=BayesianMMMModel(samples=2000, tune=2000, target_accept=0.95),
        optimizer=ScipyOptimizer(method="saturation")
    )
    
    results = pipeline.run("synthetic_mmm_data.csv")
    return results, pipeline


def main():
    st.set_page_config(page_title="MMM Dashboard", page_icon="📊", layout="wide")
    
    st.title("🎯 Media Mix Modeling Dashboard")
    st.markdown("**Cross-Channel Attribution & Budget Optimization**")
    
    model_type = st.sidebar.radio(
        "Select Attribution Model",
        ["Spend-Proportional (Simple)", "Bayesian MMM (Advanced)"]
    )
    
    if model_type == "Spend-Proportional (Simple)":
        results = load_simple_pipeline()
        metrics = results['metrics']
        optimization_results = results['optimization']
        
        st.header("Channel Attribution (Spend-Proportional)")
        st.info("ℹ️ Simple baseline: attribution proportional to spend")
        
    else:
        with st.spinner("Running Bayesian MMM (may take 1-2 minutes)..."):
            results, pipeline = load_bayesian_pipeline()
            metrics = results['metrics']
            optimization_results = results['optimization']
        
        st.header("Channel Attribution (Bayesian MMM)")
        st.info("ℹ️ Bayesian hierarchical model with adstock & saturation effects")
        
        if hasattr(pipeline.attribution_model, 'get_posterior_summary'):
            with st.expander("📊 View Posterior Distributions"):
                summary = pipeline.attribution_model.get_posterior_summary()
                st.dataframe(summary)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(metrics, x='channel', y='attribution_pct', 
                     title='Attribution by Channel',
                     color='channel')
        fig.update_layout(yaxis_title='Attribution %', xaxis_title='Channel', showlegend=False)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        fig = px.bar(metrics, x='channel', y='cost_per_conversion',
                     title='Cost per Conversion',
                     color='channel')
        fig.update_layout(yaxis_title='Cost per Conversion ($)', xaxis_title='Channel', showlegend=False)
        st.plotly_chart(fig, width='stretch')
    
    st.subheader("Attribution Metrics")
    st.dataframe(metrics, width='stretch')
    
    st.header("Budget Optimization Recommendations")
    
    if 'current_spend' in optimization_results.columns:
        current_col = 'current_spend'
        optimal_col = 'optimal_spend'
    else:
        current_col = 'current_allocation'
        optimal_col = 'optimized_allocation'
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Current', x=optimization_results['channel'], 
                         y=optimization_results[current_col],
                         marker_color='lightblue'))
    fig.add_trace(go.Bar(name='Optimal', x=optimization_results['channel'], 
                         y=optimization_results[optimal_col],
                         marker_color='darkblue'))
    fig.update_layout(barmode='group', title='Current vs Optimal Budget Allocation',
                     yaxis_title='Spend ($)', xaxis_title='Channel')
    st.plotly_chart(fig, width='stretch')
    
    st.subheader("Optimization Details")
    st.dataframe(optimization_results, width='stretch')
    
    total_budget = metrics['total_spend'].sum()
    st.metric("Total Budget", f"${total_budget:,.0f}")


if __name__ == "__main__":
    main()
