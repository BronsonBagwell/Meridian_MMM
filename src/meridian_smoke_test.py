"""Minimal official Google Meridian runtime check on the synthetic portfolio dataset."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from meridian.data.input_data import InputData
from meridian.model import model, spec

DATA_PATH = Path("data/synthetic_meridian_mmm.csv")
DEFAULT_OUTPUT_PATH = Path("reports/meridian_runtime_check.json")
MEDIA_CHANNELS = ["search", "social", "video", "tv", "affiliate"]
CONTROL_VARS = [
    "seasonality_index",
    "economic_index",
    "price_index",
    "promo_events",
    "organic_sessions",
    "holiday_flag",
]
CPM_ASSUMPTIONS = np.array([18.0, 9.0, 24.0, 35.0, 6.0])


def _da(name: str, values: np.ndarray, dims: list[str], coords: dict[str, list[str] | np.ndarray]) -> xr.DataArray:
    return xr.DataArray(values, dims=dims, coords=coords, name=name)


def build_input_data(df: pd.DataFrame) -> InputData:
    geo = ["US"]
    time_labels = df["week_start"].dt.strftime("%Y-%m-%d").tolist()
    spend = df[[f"spend_{channel}" for channel in MEDIA_CHANNELS]].to_numpy()
    media = spend / CPM_ASSUMPTIONS * 1000.0
    revenue_per_kpi = (df["revenue"] / df["conversions"]).to_numpy()

    return InputData(
        kpi=_da("kpi", df["conversions"].to_numpy()[None, :], ["geo", "time"], {"geo": geo, "time": time_labels}),
        kpi_type="non_revenue",
        population=_da("population", np.array([1_000_000.0]), ["geo"], {"geo": geo}),
        revenue_per_kpi=_da(
            "revenue_per_kpi",
            revenue_per_kpi[None, :],
            ["geo", "time"],
            {"geo": geo, "time": time_labels},
        ),
        controls=_da(
            "controls",
            df[CONTROL_VARS].to_numpy()[None, :, :],
            ["geo", "time", "control_variable"],
            {"geo": geo, "time": time_labels, "control_variable": CONTROL_VARS},
        ),
        media=_da(
            "media",
            media[None, :, :],
            ["geo", "media_time", "media_channel"],
            {"geo": geo, "media_time": time_labels, "media_channel": MEDIA_CHANNELS},
        ),
        media_spend=_da(
            "media_spend",
            spend[None, :, :],
            ["geo", "time", "media_channel"],
            {"geo": geo, "time": time_labels, "media_channel": MEDIA_CHANNELS},
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prior-draws", type=int, default=5, help="Number of prior draws to request")
    parser.add_argument("--posterior", action="store_true", help="Run a tiny posterior sample as a CPU smoke test")
    parser.add_argument("--chains", type=int, default=1)
    parser.add_argument("--adapt", type=int, default=10)
    parser.add_argument("--burnin", type=int, default=10)
    parser.add_argument("--keep", type=int, default=10)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Where to write the runtime summary JSON")
    args = parser.parse_args()

    if not DATA_PATH.exists():
        raise SystemExit("Synthetic dataset missing; run src/data_generation.py first")

    df = pd.read_csv(DATA_PATH, parse_dates=["week_start"])
    input_data = build_input_data(df)

    model_start = time.time()
    meridian_model = model.Meridian(input_data=input_data, model_spec=spec.ModelSpec(max_lag=4))
    model_build_seconds = round(time.time() - model_start, 2)

    prior_start = time.time()
    meridian_model.sample_prior(n_draws=args.prior_draws, seed=42)
    prior_seconds = round(time.time() - prior_start, 2)
    prior_vars = sorted(list(meridian_model.inference_data.prior.data_vars))

    payload: dict[str, object] = {
        "dataset_rows": int(len(df)),
        "date_range": [df["week_start"].min().strftime("%Y-%m-%d"), df["week_start"].max().strftime("%Y-%m-%d")],
        "media_channels": MEDIA_CHANNELS,
        "control_variables": CONTROL_VARS,
        "model_build_seconds": model_build_seconds,
        "prior_seconds": prior_seconds,
        "prior_draws": args.prior_draws,
        "prior_variables": prior_vars,
        "posterior_ran": False,
    }

    print(f"Meridian model built in {model_build_seconds}s")
    print(f"Prior sample complete in {prior_seconds}s with {len(prior_vars)} tracked variables")

    if args.posterior:
        posterior_start = time.time()
        meridian_model.sample_posterior(
            n_chains=args.chains,
            n_adapt=args.adapt,
            n_burnin=args.burnin,
            n_keep=args.keep,
            seed=42,
        )
        posterior_seconds = round(time.time() - posterior_start, 2)
        posterior_vars = sorted(list(meridian_model.inference_data.posterior.data_vars))
        payload.update({
            "posterior_ran": True,
            "posterior_seconds": posterior_seconds,
            "posterior_config": {
                "chains": args.chains,
                "adapt": args.adapt,
                "burnin": args.burnin,
                "keep": args.keep,
            },
            "posterior_variables": posterior_vars,
        })
        print(f"Posterior sample complete in {posterior_seconds}s")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2))
    print(f"Wrote runtime summary to {args.output}")


if __name__ == "__main__":
    main()
