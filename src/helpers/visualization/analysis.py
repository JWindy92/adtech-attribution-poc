import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd



def plot_residuals(df: pd.DataFrame, model):
    df['residuals'] = model.resid

    plt.figure(figsize=(12, 4))
    plt.plot(df.index, df['residuals'], label='Errors over time')
    plt.axhline(0, color='red', linestyle='--')
    plt.title("Is our 'Base' accurate? (Residual Plot)")
    plt.show()