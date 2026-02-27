import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# ── Constants ────────────────────────────────────────────────────────────────

CHANNELS = ["tv", "digital", "social", "radio"]
DECAY_RATES = {"tv": 0.6, "digital": 0.3, "social": 0.2, "radio": 0.4}
N_WEEKS = 104
RANDOM_SEED = 42


# ── 1. Data Generation ───────────────────────────────────────────────────────


def generate_spend_data():
    np.random.seed(RANDOM_SEED)
    return pd.DataFrame(
        {
            "week": pd.date_range("2022-01-01", periods=N_WEEKS, freq="W"),
            "tv": np.random.gamma(2, 50, N_WEEKS),
            "digital": np.random.gamma(3, 30, N_WEEKS),
            "social": np.random.gamma(4, 20, N_WEEKS),
            "radio": np.random.gamma(2, 15, N_WEEKS),
        }
    )


def generate_sales(df):
    seasonality = 1 + 0.3 * np.sin(2 * np.pi * np.arange(N_WEEKS) / 52)
    sales = (
        200
        + 0.35 * df["tv"]
        + 0.50 * df["digital"]
        + 0.25 * df["social"]
        + 0.10 * df["radio"]
        + 40 * seasonality
        + np.random.normal(0, 15, N_WEEKS)
    )
    df["sales"] = sales
    df["seasonality"] = seasonality
    return df


# ── 2. Adstock (Carry-over) ──────────────────────────────────────────────────


def apply_adstock(spend, decay):
    result = np.zeros_like(spend, dtype=float)
    result[0] = spend[0]
    for t in range(1, len(spend)):
        result[t] = spend[t] + decay * result[t - 1]
    return result


def add_adstock_columns(df):
    for ch in CHANNELS:
        df[f"{ch}_adstock"] = apply_adstock(df[ch].values, DECAY_RATES[ch])
    return df


# ── 3. Saturation Curve ──────────────────────────────────────────────────────


def hill_saturation(x, alpha, gamma):
    """
    Hill function: flattens spend effect as x grows.
      alpha = slope steepness
      gamma = half-saturation point (spend level at 50% of max effect)
    """
    return x**alpha / (x**alpha + gamma**alpha)


def apply_saturation(df):
    """Apply Hill saturation to each adstock column."""
    for ch in CHANNELS:
        col = df[f"{ch}_adstock"].values
        # Simple fixed params — could also be priors in the model
        alpha, gamma = 2.0, col.mean()
        df[f"{ch}_saturated"] = hill_saturation(col, alpha, gamma)
    return df


# ── 4. Feature Scaling ───────────────────────────────────────────────────────


def scale_features(df):
    saturated_cols = [f"{ch}_saturated" for ch in CHANNELS]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[saturated_cols])
    return X_scaled, scaler


# ── 5. Bayesian Model ────────────────────────────────────────────────────────


def build_model(X_scaled, y, seasonality):
    with pm.Model() as model:
        intercept = pm.Normal("intercept", mu=200, sigma=50)
        season_coef = pm.Normal("season_coef", mu=0, sigma=50)
        sigma = pm.HalfNormal("sigma", sigma=30)
        beta_tv = pm.HalfNormal("beta_tv", sigma=1)
        beta_digital = pm.HalfNormal("beta_digital", sigma=1)
        beta_social = pm.HalfNormal("beta_social", sigma=1)
        beta_radio = pm.HalfNormal("beta_radio", sigma=1)
        betas = pm.math.stack([beta_tv, beta_digital, beta_social, beta_radio])
        mu = intercept + season_coef * seasonality + pm.math.dot(X_scaled, betas)
        _ = pm.Normal("obs", mu=mu, sigma=sigma, observed=y)
    return model


def sample_model(model):
    with model:
        trace = pm.sample(
            draws=2000,
            tune=1000,
            target_accept=0.9,
            return_inferencedata=True,
            random_seed=RANDOM_SEED,
        )
    return trace


def run_posterior_predictive(model, trace):
    with model:
        ppc = pm.sample_posterior_predictive(trace, random_seed=RANDOM_SEED)
    return ppc


# ── 6. Attribution ───────────────────────────────────────────────────────────


def extract_beta_means(trace):
    post = trace.posterior
    return {
        "tv": float(post["beta_tv"].mean()),
        "digital": float(post["beta_digital"].mean()),
        "social": float(post["beta_social"].mean()),
        "radio": float(post["beta_radio"].mean()),
    }


def calculate_contributions(df, beta_means, scaler):
    contributions = {}
    for i, ch in enumerate(CHANNELS):
        contributions[ch] = (beta_means[ch] / scaler.scale_[i]) * df[
            f"{ch}_saturated"
        ].sum()
    return contributions


def calculate_roi(df, contributions):
    return {ch: contributions[ch] / df[ch].sum() for ch in CHANNELS}


# ── 7. Reporting ─────────────────────────────────────────────────────────────


def print_posterior_summary(trace):
    print(
        az.summary(
            trace,
            var_names=[
                "intercept",
                "season_coef",
                "beta_tv",
                "beta_digital",
                "beta_social",
                "beta_radio",
                "sigma",
            ],
        )
    )


def print_attribution_report(contributions, roi):
    total = sum(contributions.values())
    print("\n── Channel Attribution ─────────────────────────")
    for ch in CHANNELS:
        print(
            f"  {ch:>10s}:  "
            f"contribution={contributions[ch]:8,.0f}  "
            f"share={100 * contributions[ch] / total:5.1f}%  "
            f"ROI={roi[ch]:.2f}x"
        )


# ── 8. Plots ─────────────────────────────────────────────────────────────────


def plot_posterior_predictive(df, ppc):
    y_hat = ppc.posterior_predictive["obs"].mean(dim=["chain", "draw"]).values
    plt.figure(figsize=(14, 4))
    plt.plot(df["week"], df["sales"], label="Actual")
    plt.plot(df["week"], y_hat, label="Predicted", linestyle="--")
    plt.fill_between(
        df["week"],
        ppc.posterior_predictive["obs"].quantile(0.05, dim=["chain", "draw"]),
        ppc.posterior_predictive["obs"].quantile(0.95, dim=["chain", "draw"]),
        alpha=0.2,
        label="90% CI",
    )
    plt.title("Posterior Predictive Check")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_saturation_curves(df):
    fig, axes = plt.subplots(1, len(CHANNELS), figsize=(14, 4), sharey=True)
    for ax, ch in zip(axes, CHANNELS):
        col = df[f"{ch}_adstock"].values
        x = np.linspace(0, col.max(), 200)
        y = hill_saturation(x, alpha=2.0, gamma=col.mean())
        ax.plot(x, y)
        ax.axvline(col.mean(), color="red", linestyle="--", label="mean spend")
        ax.set_title(f"{ch} saturation")
        ax.set_xlabel("Adstock spend")
    axes[0].set_ylabel("Saturation (0–1)")
    plt.suptitle("Hill Saturation Curves by Channel")
    plt.tight_layout()
    plt.show()


def plot_contributions(contributions):
    plt.figure(figsize=(8, 4))
    plt.bar(
        contributions.keys(),
        contributions.values(),
        color=["#4C72B0", "#DD8452", "#55A868", "#C44E52"],
    )
    plt.title("Channel Sales Contribution")
    plt.ylabel("Attributed Sales ($)")
    plt.tight_layout()
    plt.show()


# ── 9. Pipeline ──────────────────────────────────────────────────────────────


def run_mmm_pipeline():
    # Generate synthetic data
    df = generate_spend_data()
    df = generate_sales(df)

    # Apply transformations
    df = add_adstock_columns(df)
    df = apply_saturation(df)

    X, scaler = scale_features(df)  # ? Not sure this is needed/beneficial

    # Buiilding model
    model = build_model(X, df["sales"].values, df["seasonality"].values)
    trace = sample_model(model)

    ppc = run_posterior_predictive(model, trace)
    beta_means = extract_beta_means(trace)
    contributions = calculate_contributions(df, beta_means, scaler)
    roi = calculate_roi(df, contributions)

    print_posterior_summary(trace)
    print_attribution_report(contributions, roi)
    plot_posterior_predictive(df, ppc)
    plot_saturation_curves(df)
    plot_contributions(contributions)


if __name__ == "__main__":
    run_mmm_pipeline()
