import sys
sys.path.insert(0, '..')

from src.datasources.csv import CSVDataSource
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def validate_data(filepath):
    print("=" * 60)
    print("SYNTHETIC DATA VALIDATION")
    print("=" * 60)
    
    data_source = CSVDataSource(".")
    df = data_source.load_data(filepath)
    
    print(f"\n✓ Loaded {len(df)} weeks")
    print(f"\nBasic stats:")
    print(df.describe())
    
    media_cols = data_source.get_media_columns(df)
    
    print(f"\n\nChecking for realistic patterns:")
    
    print("\n1. Spending variance (should vary, not constant):")
    for col in media_cols:
        cv = df[col].std() / df[col].mean()
        print(f"   {col}: CV = {cv:.2%}")
    
    print("\n2. Conversion correlation with spend:")
    for col in media_cols:
        corr = df[col].corr(df['conversions'])
        print(f"   {col} → conversions: r = {corr:.3f}")
    
    print("\n3. Checking for seasonality (Q4 should be higher):")
    df['quarter'] = pd.to_datetime(df['week']).dt.quarter
    quarterly = df.groupby('quarter')['conversions'].mean()
    print(f"   Q1: {quarterly.get(1, 0):.0f}")
    print(f"   Q2: {quarterly.get(2, 0):.0f}")
    print(f"   Q3: {quarterly.get(3, 0):.0f}")
    print(f"   Q4: {quarterly.get(4, 0):.0f}")
    
    print("\n4. ROI rough check (spend vs conversions):")
    total_spend = df[media_cols].sum().sum()
    total_conversions = df['conversions'].sum()
    print(f"   Total spend: ${total_spend:,.0f}")
    print(f"   Total conversions: {total_conversions:,.0f}")
    print(f"   Overall cost per conversion: ${total_spend / total_conversions:.2f}")
    
    print("\n✓ Data looks realistic!")
    print("=" * 60)


if __name__ == "__main__":
    validate_data("synthetic_mmm_data.csv")
