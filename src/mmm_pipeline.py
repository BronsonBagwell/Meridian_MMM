"""Offline Meridian-inspired MMM pipeline used for fast portfolio outputs."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.optimize import lsq_linear

DATA_PATH = Path("data/synthetic_meridian_mmm.csv")
FIG_DIR = Path("reports/figures")
METRICS_PATH = Path("reports/metrics.json")
MPL_CONFIG = Path("reports/mplconfig")
CHANNELS = ["search", "social", "video", "tv", "affiliate"]
ADSTOCK_DECAY = {"search": 0.65, "social": 0.55, "video": 0.6, "tv": 0.7, "affiliate": 0.4}
SAT_PARAMS = {
    "search": {"scale": 42000, "power": 0.9},
    "social": {"scale": 26000, "power": 1.0},
    "video": {"scale": 30000, "power": 1.05},
    "tv": {"scale": 60000, "power": 0.95},
    "affiliate": {"scale": 14000, "power": 1.1},
}
CONTROL_FEATURES = [
    "seasonality_index",
    "price_index",
    "promo_events",
    "economic_index",
    "organic_sessions",
    "holiday_flag",
]

os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG.resolve()))
MPL_CONFIG.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="talk", font="DejaVu Sans")


def adstock(series: pd.Series, decay: float) -> np.ndarray:
    result = np.zeros(len(series))
    carry = 0.0
    for i, value in enumerate(series):
        carry = value + decay * carry
        result[i] = carry
    return result


def saturation_transform(values: np.ndarray, scale: float, power: float) -> np.ndarray:
    normalized = np.log1p(np.maximum(values, 0) / scale)
    return np.power(normalized, power)


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    features: Dict[str, np.ndarray] = {}
    for channel in CHANNELS:
        decay = ADSTOCK_DECAY[channel]
        params = SAT_PARAMS[channel]
        adstocked = adstock(df[f"spend_{channel}"], decay)
        features[f"{channel}_effect"] = saturation_transform(adstocked, params["scale"], params["power"])
    controls = df[CONTROL_FEATURES].copy()
    controls["organic_sessions"] = controls["organic_sessions"] / controls["organic_sessions"].max()
    controls["promo_events"] = controls["promo_events"].astype(float)
    controls["holiday_flag"] = controls["holiday_flag"].astype(float)
    controls["price_index"] = controls["price_index"] - controls["price_index"].mean()
    for col in controls.columns:
        features[col] = controls[col].to_numpy()
    features["intercept"] = np.ones(len(df))
    return pd.DataFrame(features, index=df.index)


def solve_regression(features: pd.DataFrame, target: pd.Series) -> np.ndarray:
    X = features.values
    y = target.values
    media_cols = {f"{c}_effect" for c in CHANNELS}
    lb = np.array([0.0 if col in media_cols else -np.inf for col in features.columns])
    ub = np.full(X.shape[1], np.inf)
    return lsq_linear(X, y, bounds=(lb, ub)).x  # media effects constrained >= 0


def summarize_channels(coeffs: np.ndarray, features: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    contribution_matrix = features.mul(coeffs, axis=1)
    summary_rows = []
    avg_order_value = float((df["revenue"].sum() / df["conversions"].sum()).round(2))
    for channel in CHANNELS:
        col = f"{channel}_effect"
        incremental_conv = contribution_matrix[col].sum()
        spend = df[f"spend_{channel}"].sum()
        avg_weekly_spend = df[f"spend_{channel}"].mean()
        incremental_rev = incremental_conv * avg_order_value
        roi = incremental_rev / spend if spend > 0 else np.nan
        summary_rows.append(
            {
                "channel": channel,
                "spend": float(spend),
                "avg_weekly_spend": float(avg_weekly_spend),
                "incremental_conversions": float(incremental_conv),
                "incremental_revenue": float(incremental_rev),
                "roi": float(roi),
            }
        )
    return pd.DataFrame(summary_rows)


def plot_actual_vs_pred(df: pd.DataFrame) -> None:
    long_df = df.melt(
        id_vars="week_start",
        value_vars=["conversions", "predicted_conversions"],
        var_name="series",
        value_name="value",
    )
    plt.figure(figsize=(13, 6))
    sns.lineplot(data=long_df, x="week_start", y="value", hue="series", linewidth=2.2)
    plt.title("Actual vs. Modeled Conversions")
    plt.xlabel("Week")
    plt.ylabel("Conversions")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "conversions_actual_vs_predicted.png", dpi=200, bbox_inches="tight")
    plt.close()


def plot_channel_contributions(channel_df: pd.DataFrame) -> None:
    ordered = channel_df.sort_values("incremental_conversions", ascending=False)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=ordered, x="channel", y="incremental_conversions", hue="channel", dodge=False, palette="viridis")
    plt.legend([], [], frameon=False)
    plt.title("Incremental Conversions by Channel")
    plt.xlabel("Channel")
    plt.ylabel("Conversions")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "channel_incremental_conversions.png", dpi=200, bbox_inches="tight")
    plt.close()


def steady_state_feature(spend: np.ndarray, channel: str) -> np.ndarray:
    decay = ADSTOCK_DECAY[channel]
    params = SAT_PARAMS[channel]
    steady_adstock = spend / max(1 - decay, 1e-3)
    return saturation_transform(steady_adstock, params["scale"], params["power"])


def plot_response_curves(channel_df: pd.DataFrame, coeffs: np.ndarray, features: pd.DataFrame) -> None:
    coeff_lookup = {col: coeff for col, coeff in zip(features.columns, coeffs)}
    fig, axes = plt.subplots(2, 3, figsize=(16, 9), constrained_layout=True)
    axes = axes.flatten()
    for idx, channel in enumerate(CHANNELS):
        avg_spend = channel_df.loc[channel_df.channel == channel, "avg_weekly_spend"].iloc[0]
        spends = np.linspace(avg_spend * 0.4, avg_spend * 1.6, 25)
        feature_vals = steady_state_feature(spends, channel)
        coeff = coeff_lookup[f"{channel}_effect"]
        conversions = feature_vals * coeff
        axes[idx].plot(spends / 1000, conversions, linewidth=2.4)
        axes[idx].set_title(f"{channel.title()} response")
        axes[idx].set_xlabel("Weekly spend (K USD)")
        axes[idx].set_ylabel("Incremental conversions")
        axes[idx].tick_params(labelsize=10)
    for ax in axes[len(CHANNELS):]:
        ax.axis("off")
    fig.suptitle("Modeled response curves (steady-state assumption)", fontsize=16)
    fig.savefig(FIG_DIR / "response_curves.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def export_metrics(df: pd.DataFrame, channel_df: pd.DataFrame, coeffs: np.ndarray, features: pd.DataFrame) -> dict[str, object]:
    mape = float((np.abs(df["conversions"] - df["predicted_conversions"]) / df["conversions"]).mean())
    payload: dict[str, object] = {
        "records": int(len(df)),
        "date_range": [df["week_start"].min().strftime("%Y-%m-%d"), df["week_start"].max().strftime("%Y-%m-%d")],
        "mape": round(mape, 4),
        "channel_summary": channel_df.to_dict(orient="records"),
        "coefficients": {col: coeff for col, coeff in zip(features.columns, coeffs)},
    }
    METRICS_PATH.write_text(json.dumps(payload, indent=2))
    return payload


def run_pipeline(data_path: Path = DATA_PATH) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    if not data_path.exists():
        raise SystemExit("Synthetic dataset missing; run src/data_generation.py first")

    df = pd.read_csv(data_path, parse_dates=["week_start"])
    features = build_feature_matrix(df)
    coeffs = solve_regression(features, df["conversions"])
    df["predicted_conversions"] = features.values @ coeffs
    channel_df = summarize_channels(coeffs, features, df)

    plot_actual_vs_pred(df)
    plot_channel_contributions(channel_df)
    plot_response_curves(channel_df, coeffs, features)
    metrics = export_metrics(df, channel_df, coeffs, features)
    return df, channel_df, metrics


def main() -> None:
    df, channel_df, metrics = run_pipeline()
    print("Pipeline complete.")
    print(f"MAPE: {metrics['mape']}")
    print("Top ROI channels:")
    for row in channel_df.sort_values("roi", ascending=False).head(3).itertuples():
        print(f"  - {row.channel}: ROI {row.roi:.2f}x on ${row.avg_weekly_spend:,.0f} avg weekly spend")


if __name__ == "__main__":
    main()
