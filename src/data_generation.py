"""Generate a synthetic marketing dataset suitable for a Meridian-style MMM demo."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

OUTPUT_PATH = Path("data/synthetic_meridian_mmm.csv")
PROFILE_PATH = Path("data/synthetic_metadata.json")


def _seasonal_wave(length: int) -> np.ndarray:
    weeks = np.arange(length)
    annual = 1 + 0.25 * np.sin(2 * np.pi * weeks / 52)
    mid_term = 1 + 0.08 * np.cos(2 * np.pi * weeks / 26)
    return annual * mid_term


def _channel_spend(rng: np.random.Generator, length: int, mean: float, volatility: float,
                   pulses: list[tuple[int, int, float]]) -> np.ndarray:
    seasonal = _seasonal_wave(length)
    noise = rng.normal(0, volatility, length)
    spend = (mean * seasonal) + noise
    for start, duration, lift in pulses:
        end = min(start + duration, length)
        spend[start:end] += lift
    return np.clip(spend, 0, None)


def build_dataset() -> pd.DataFrame:
    rng = np.random.default_rng(22)
    weeks = pd.date_range("2022-01-03", periods=110, freq="W-MON")
    n = len(weeks)
    df = pd.DataFrame({"week_start": weeks})

    channel_specs = {
        "search": {"mean": 48000, "volatility": 6500, "pulses": [(12, 6, 9000), (60, 8, 11000)]},
        "social": {"mean": 26000, "volatility": 4800, "pulses": [(20, 10, 6000), (72, 12, 7000)]},
        "video": {"mean": 31000, "volatility": 5200, "pulses": [(8, 5, 5000), (48, 9, 8000)]},
        "tv": {"mean": 54000, "volatility": 8000, "pulses": [(30, 6, 14000), (80, 6, 15000)]},
        "affiliate": {"mean": 12000, "volatility": 2200, "pulses": [(15, 5, 2000), (55, 7, 2500)]},
    }

    for channel, spec in channel_specs.items():
        df[f"spend_{channel}"] = _channel_spend(rng, n, spec["mean"], spec["volatility"], spec["pulses"])

    df["seasonality_index"] = _seasonal_wave(n)
    df["economic_index"] = 100 + 3.5 * np.sin(np.linspace(0, 6, n)) + rng.normal(0, 1.5, n)
    df["price_index"] = 1 + 0.015 * np.cos(np.linspace(0, 8, n)) + rng.normal(0, 0.005, n)
    df["promo_events"] = rng.poisson(0.35, n).clip(0, 3)
    df["organic_sessions"] = np.clip(220000 * df["seasonality_index"] + rng.normal(0, 9000, n), 60000, None)

    # Base demand before paid media
    base = 900 + 260 * df["seasonality_index"] + 8 * (df["economic_index"] - 100) - 400 * (df["price_index"] - 1)
    base += 65 * df["promo_events"]

    channel_weights = {
        "search": {"scale": 38000, "lift": 520},
        "social": {"scale": 24000, "lift": 260},
        "video": {"scale": 30000, "lift": 320},
        "tv": {"scale": 52000, "lift": 410},
        "affiliate": {"scale": 10000, "lift": 150},
    }

    contributions = []
    for channel, params in channel_weights.items():
        spend = df[f"spend_{channel}"]
        transformed = params["lift"] * np.log1p(spend / params["scale"])
        contributions.append(transformed)

    media_effect = np.sum(contributions, axis=0)
    noise = rng.normal(0, 45, n)
    conversions = np.clip(base + media_effect + noise, 400, None)
    df["conversions"] = conversions.round().astype(int)
    avg_order_value = 210
    df["site_visits"] = (df["conversions"] / 0.032).round().astype(int)
    df["revenue"] = (df["conversions"] * avg_order_value).round(2)
    df["total_spend"] = df[[col for col in df.columns if col.startswith("spend_")]].sum(axis=1)
    df["market"] = "US"
    iso_weeks = df["week_start"].dt.isocalendar().week
    df["holiday_flag"] = ((df["week_start"].dt.month.isin([11, 12])) | (iso_weeks == 26)).astype(int)

    return df


def write_metadata(df: pd.DataFrame) -> None:
    profiles = {
        "record_count": int(df.shape[0]),
        "date_range": [df["week_start"].min().strftime("%Y-%m-%d"), df["week_start"].max().strftime("%Y-%m-%d")],
        "channels": [col.replace("spend_", "") for col in df.columns if col.startswith("spend_")],
        "currency": "USD",
        "target": "conversions",
        "notes": "Synthetic data emulating Google Meridian MMM input expectations (weekly granularity, spend + controls).",
    }
    PROFILE_PATH.write_text(json.dumps(profiles, indent=2))


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = build_dataset()
    df.to_csv(OUTPUT_PATH, index=False)
    write_metadata(df)
    print(f"Wrote {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
