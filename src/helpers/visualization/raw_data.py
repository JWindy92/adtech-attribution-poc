import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

def plot_raw_signal(df):
    fig, ax = plt.subplots(
        nrows=3, ncols=2, figsize=(16, 9), sharex=True, sharey=False, layout="constrained"
    )
    sns.lineplot(x="date_week", y="x1", data=df, color="C0", ax=ax[0, 0])
    sns.lineplot(x="date_week", y="x2", data=df, color="C1", ax=ax[0, 1])
    sns.lineplot(x="date_week", y="x1_adstock", data=df, color="C0", ax=ax[1, 0])
    sns.lineplot(x="date_week", y="x2_adstock", data=df, color="C1", ax=ax[1, 1])
    sns.lineplot(x="date_week", y="x1_adstock_saturated", data=df, color="C0", ax=ax[2, 0])
    sns.lineplot(x="date_week", y="x2_adstock_saturated", data=df, color="C1", ax=ax[2, 1])
    fig.suptitle("Media Costs Data - Transformed", fontsize=18, fontweight="bold");


def plot_corr_matrix(df):
    plt.figure(figsize=(10,5))
    sns.heatmap(df.corr(),
                annot=True,
                linewidths=.5,
                center=0,
                cbar=False,
                cmap='RdBu_r')
    plt.show()


def plot_feat_importance(df):
    X = df.loc[:, df.columns != 'conversions']
    y = df['conversions']

    # Building Random Forest model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.25, random_state=0)
    model = RandomForestRegressor(random_state=1)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    feat_importances = pd.Series(model.feature_importances_, index=X.columns)
    feat_importances.nlargest(25).plot(kind='barh',figsize=(10,10))
    plt.show()