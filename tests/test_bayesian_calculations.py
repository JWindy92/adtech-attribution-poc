"""
Unit tests for the attribution pipeline's core mathematical calculations.

Covers three critical correctness properties that were previously buggy:
  1. Baseline subtraction — organic (intercept) conversions must be removed
     before attributing the remainder to media channels.
  2. Transformed-spend weighting — contribution weights must use beta ×
     saturated_spend, not beta × raw_dollars.
  3. Metric invariants — attribution_pct sums to 100, attributed conversions
     never exceed total conversions, CPC is positive.

Also covers deterministic math in AdstockTransformer and SaturationTransformer.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import pytest
from unittest.mock import MagicMock

from src.models.bayesian_mmm import BayesianMMMModel
from src.transformers.adstock_transformer import AdstockTransformer
from src.transformers.saturation_transformer import SaturationTransformer
from src.transformers.chain import TransformerChain


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_trace(beta_values, intercept_value):
    """Return a MagicMock that looks enough like an ArviZ InferenceData trace
    for _compute_metrics() to use.  No MCMC sampling is performed."""
    betas_da = MagicMock()
    betas_da.mean.return_value.values = np.array(beta_values, dtype=float)

    intercept_da = MagicMock()
    intercept_da.mean.return_value.values = np.float64(intercept_value)

    mock_trace = MagicMock()
    mock_trace.posterior.__getitem__ = MagicMock(
        side_effect=lambda key: {"betas": betas_da, "intercept": intercept_da}[key]
    )
    return mock_trace


def _model_with_trace(beta_values, intercept_value):
    """Return a BayesianMMMModel that has a pre-injected mock trace."""
    model = BayesianMMMModel()
    model.trace = _make_mock_trace(beta_values, intercept_value)
    return model


# ---------------------------------------------------------------------------
# Adstock transformer — deterministic math
# ---------------------------------------------------------------------------

class TestAdstockTransformer:

    def test_single_week_no_lag_equals_input(self):
        """With only one time step, adstock = the input value itself."""
        transformer = AdstockTransformer({"ch": {"decay": 0.5, "max_lag": 4}})
        df = pd.DataFrame({"ch": [1000.0], "conversions": [100.0]})
        out = transformer.apply_transforms(df, ["ch"])
        assert out["ch"].iloc[0] == pytest.approx(1000.0)

    def test_geometric_decay_second_period(self):
        """
        t=0: spend=100  → adstock[0] = 100
        t=1: spend=0    → adstock[1] = 0 + 100*decay = 100*0.6 = 60
        """
        transformer = AdstockTransformer({"ch": {"decay": 0.6, "max_lag": 4}})
        df = pd.DataFrame({"ch": [100.0, 0.0, 0.0], "conversions": [0, 0, 0]})
        out = transformer.apply_transforms(df, ["ch"])
        assert out["ch"].iloc[0] == pytest.approx(100.0)
        assert out["ch"].iloc[1] == pytest.approx(60.0)    # carryover
        assert out["ch"].iloc[2] == pytest.approx(36.0)    # 100 * 0.6^2

    def test_zero_spend_produces_zero_adstock(self):
        transformer = AdstockTransformer({"ch": {"decay": 0.7, "max_lag": 6}})
        df = pd.DataFrame({"ch": [0.0] * 10, "conversions": [0.0] * 10})
        out = transformer.apply_transforms(df, ["ch"])
        assert (out["ch"].values == 0.0).all()

    def test_untouched_channels_pass_through(self):
        """Channels without params in adstock_params should be left unchanged."""
        transformer = AdstockTransformer({"ch_a": {"decay": 0.5, "max_lag": 4}})
        df = pd.DataFrame({
            "ch_a": [100.0, 200.0],
            "ch_b": [50.0, 75.0],
            "conversions": [0, 0],
        })
        out = transformer.apply_transforms(df, ["ch_a", "ch_b"])
        assert list(out["ch_b"]) == [50.0, 75.0]


# ---------------------------------------------------------------------------
# Saturation transformer — deterministic math
# ---------------------------------------------------------------------------

class TestSaturationTransformer:

    def test_half_saturation_point(self):
        """
        Hill equation: x^α / (γ^α + x^α)
        When x == γ, the equation simplifies to γ^α / (2 * γ^α) = 0.5
        regardless of alpha.
        """
        for alpha in [0.5, 1.0, 1.5, 2.0]:
            gamma = 50_000.0
            transformer = SaturationTransformer(
                {"ch": {"alpha": alpha, "gamma": gamma}}
            )
            df = pd.DataFrame({"ch": [gamma], "conversions": [100.0]})
            out = transformer.apply_transforms(df, ["ch"])
            assert out["ch"].iloc[0] == pytest.approx(0.5, rel=1e-6), (
                f"Hill equation at x=gamma should equal 0.5 (alpha={alpha})"
            )

    def test_zero_spend_gives_zero_saturation(self):
        transformer = SaturationTransformer({"ch": {"alpha": 1.2, "gamma": 10_000.0}})
        df = pd.DataFrame({"ch": [0.0], "conversions": [0.0]})
        out = transformer.apply_transforms(df, ["ch"])
        assert out["ch"].iloc[0] == pytest.approx(0.0)

    def test_output_bounded_between_zero_and_one(self):
        """Saturation output must stay in [0, 1] for all positive inputs."""
        transformer = SaturationTransformer({"ch": {"alpha": 1.5, "gamma": 100_000.0}})
        spends = [0, 1_000, 50_000, 100_000, 500_000, 10_000_000]
        df = pd.DataFrame({"ch": spends, "conversions": [0] * len(spends)})
        out = transformer.apply_transforms(df, ["ch"])
        assert (out["ch"].values >= 0.0).all()
        assert (out["ch"].values <= 1.0).all()

    def test_saturation_is_monotonically_increasing(self):
        """More spend → more saturated output (never decreases)."""
        transformer = SaturationTransformer({"ch": {"alpha": 1.0, "gamma": 50_000.0}})
        spends = list(range(0, 200_001, 10_000))
        df = pd.DataFrame({"ch": spends, "conversions": [0] * len(spends)})
        out = transformer.apply_transforms(df, ["ch"])
        vals = out["ch"].values
        assert (np.diff(vals) >= 0).all()


# ---------------------------------------------------------------------------
# TransformerChain — fluent composition
# ---------------------------------------------------------------------------

class TestTransformerChain:

    def test_chain_applies_in_order(self):
        """
        Adstock then saturation should differ from saturation alone.
        The chain must apply them sequentially, not skip one.
        """
        adstock_params = {"ch": {"decay": 0.5, "max_lag": 3}}
        sat_params = {"ch": {"alpha": 1.0, "gamma": 500.0}}

        adstock = AdstockTransformer(adstock_params)
        saturation = SaturationTransformer(sat_params)
        chain = adstock.then(saturation)

        df = pd.DataFrame({"ch": [1000.0, 0.0, 0.0, 0.0], "conversions": [0] * 4})
        media_cols = ["ch"]

        chained_out = chain.apply_transforms(df, media_cols)

        # Manual step-by-step
        after_adstock = adstock.apply_transforms(df, media_cols)
        after_both = saturation.apply_transforms(after_adstock, media_cols)

        np.testing.assert_array_almost_equal(
            chained_out["ch"].values,
            after_both["ch"].values,
        )

    def test_chain_is_a_transformer(self):
        """TransformerChain must itself satisfy the Transformer interface."""
        from src.core.interfaces import Transformer
        chain = AdstockTransformer().then(SaturationTransformer())
        assert isinstance(chain, Transformer)

    def test_then_returns_chain(self):
        a = AdstockTransformer()
        b = SaturationTransformer()
        result = a.then(b)
        assert isinstance(result, TransformerChain)


# ---------------------------------------------------------------------------
# BayesianMMMModel._compute_metrics — fix #1: baseline subtraction
# ---------------------------------------------------------------------------

class TestBaselineSubtraction:

    def test_attributed_conversions_exclude_baseline(self):
        """
        intercept_mean = 10, n_weeks = 10  →  baseline = 100
        total_conversions = 200           →  media_conversions = 100
        sum(attributed_conversions) must equal 100, not 200.
        """
        model = _model_with_trace(beta_values=[100.0, 50.0], intercept_value=10.0)

        n_weeks = 10
        df = pd.DataFrame({
            "conversions": [20.0] * n_weeks,   # total = 200
            "ch_a": [0.6] * n_weeks,
            "ch_b": [0.4] * n_weeks,
        })
        raw_df = df.copy()
        raw_df["ch_a"] = 10_000.0
        raw_df["ch_b"] = 5_000.0

        metrics = model._compute_metrics(df, raw_df, ["ch_a", "ch_b"])

        expected_media_conversions = 200.0 - (10.0 * 10)  # = 100
        assert metrics["attributed_conversions"].sum() == pytest.approx(
            expected_media_conversions, rel=1e-6
        )

    def test_zero_intercept_attributes_all_conversions(self):
        """When intercept=0 there is no organic baseline; all conversions are media-driven."""
        model = _model_with_trace(beta_values=[1.0, 1.0], intercept_value=0.0)

        df = pd.DataFrame({"conversions": [500.0] * 4, "ch_a": [0.5] * 4, "ch_b": [0.5] * 4})
        raw_df = df.copy()

        metrics = model._compute_metrics(df, raw_df, ["ch_a", "ch_b"])
        assert metrics["attributed_conversions"].sum() == pytest.approx(2000.0, rel=1e-6)

    def test_large_intercept_clamps_to_zero(self):
        """If baseline > total conversions, attributed conversions must be 0, not negative."""
        # intercept=1000, n_weeks=4 → baseline=4000 > total_conversions=400
        model = _model_with_trace(beta_values=[1.0, 1.0], intercept_value=1000.0)

        df = pd.DataFrame({"conversions": [100.0] * 4, "ch_a": [0.5] * 4, "ch_b": [0.5] * 4})
        raw_df = df.copy()

        metrics = model._compute_metrics(df, raw_df, ["ch_a", "ch_b"])
        assert metrics["attributed_conversions"].sum() == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# BayesianMMMModel._compute_metrics — fix #2: transformed spend weighting
# ---------------------------------------------------------------------------

class TestTransformedSpendWeighting:

    def test_weights_come_from_transformed_not_raw_spend(self):
        """
        Equal betas, so the only thing that differentiates channels is spend.
        ch_a: transformed=0.8, raw=$1 000    ← high saturation, low budget
        ch_b: transformed=0.2, raw=$9 000    ← low saturation, high budget

        ch_a should receive 4x more attributed conversions than ch_b
        (0.8 / 0.2 = 4) because weights come from transformed spend.
        If raw spend were used instead, ch_b would dominate (9:1 ratio).
        """
        model = _model_with_trace(beta_values=[1.0, 1.0], intercept_value=0.0)

        n_weeks = 4
        df = pd.DataFrame({
            "conversions": [100.0] * n_weeks,
            "ch_a": [0.8] * n_weeks,
            "ch_b": [0.2] * n_weeks,
        })
        raw_df = pd.DataFrame({
            "conversions": [100.0] * n_weeks,
            "ch_a": [1_000.0] * n_weeks,
            "ch_b": [9_000.0] * n_weeks,
        })

        metrics = model._compute_metrics(df, raw_df, ["ch_a", "ch_b"])

        ch_a_conv = metrics.loc[metrics["channel"] == "ch_a", "attributed_conversions"].values[0]
        ch_b_conv = metrics.loc[metrics["channel"] == "ch_b", "attributed_conversions"].values[0]

        # ch_a gets 80% of media conversions (transformed weight 0.8 vs 0.2)
        assert ch_a_conv > ch_b_conv, (
            "ch_a has higher transformed spend; it must receive more attribution "
            "regardless of raw dollar budget"
        )
        assert ch_a_conv / ch_b_conv == pytest.approx(4.0, rel=1e-5)

    def test_exact_contribution_values_match_formula(self):
        """
        betas = [200, 100]
        transformed_spend per channel (sum over n_weeks) = [3.0, 2.0]
        contributions = [200*3, 100*2] = [600, 200], total = 800
        intercept=0 → media_conversions = total_conversions = 1000
        ch_a attributed = (600/800)*1000 = 750
        ch_b attributed = (200/800)*1000 = 250
        """
        model = _model_with_trace(beta_values=[200.0, 100.0], intercept_value=0.0)

        df = pd.DataFrame({
            "conversions": [250.0] * 4,    # total = 1000
            "ch_a": [0.75] * 4,            # sum = 3.0
            "ch_b": [0.50] * 4,            # sum = 2.0
        })
        raw_df = df.copy()

        metrics = model._compute_metrics(df, raw_df, ["ch_a", "ch_b"])

        ch_a = metrics.loc[metrics["channel"] == "ch_a", "attributed_conversions"].values[0]
        ch_b = metrics.loc[metrics["channel"] == "ch_b", "attributed_conversions"].values[0]
        np.testing.assert_allclose(ch_a, 750.0, rtol=1e-6)
        np.testing.assert_allclose(ch_b, 250.0, rtol=1e-6)


# ---------------------------------------------------------------------------
# BayesianMMMModel._compute_metrics — metric invariants
# ---------------------------------------------------------------------------

class TestMetricInvariants:

    def _run(self, betas, intercept, conversions_per_week, transformed_spend, n_weeks=10):
        model = _model_with_trace(betas, intercept)
        n_ch = len(betas)
        df = pd.DataFrame(
            {"conversions": [conversions_per_week] * n_weeks}
            | {f"ch_{i}": [transformed_spend[i]] * n_weeks for i in range(n_ch)}
        )
        raw_df = df.copy()
        cols = [f"ch_{i}" for i in range(n_ch)]
        return model._compute_metrics(df, raw_df, cols)

    def test_attribution_pct_sums_to_100(self):
        metrics = self._run([100.0, 200.0, 50.0], 5.0, 300.0, [0.5, 0.7, 0.3])
        assert metrics["attribution_pct"].sum() == pytest.approx(100.0, rel=1e-6)

    def test_attributed_conversions_do_not_exceed_total(self):
        metrics = self._run([80.0, 120.0], 20.0, 200.0, [0.4, 0.6])
        total_conversions = 200.0 * 10
        assert metrics["attributed_conversions"].sum() <= total_conversions + 1e-9

    def test_cpc_is_positive_when_conversions_positive(self):
        metrics = self._run([100.0, 200.0], 0.0, 500.0, [0.5, 0.5])
        assert (metrics["cost_per_conversion"] > 0).all()

    def test_output_channels_match_input(self):
        media_cols = ["search", "social", "ctv"]
        model = _model_with_trace([1.0, 2.0, 0.5], 10.0)
        df = pd.DataFrame(
            {"conversions": [100.0] * 5, "search": [0.4] * 5, "social": [0.3] * 5, "ctv": [0.6] * 5}
        )
        metrics = model._compute_metrics(df, df.copy(), media_cols)
        assert list(metrics["channel"]) == media_cols
