# Meridian Runtime Check

## What was verified
This project does not just reference Meridian in theory. The official `google-meridian` package was installed in the project virtual environment and exercised against the synthetic dataset in `data/synthetic_meridian_mmm.csv`.

## Command run
```bash
python src/meridian_smoke_test.py --posterior
```

## Result
- **Model build:** 0.41s
- **Prior sample:** 0.24s
- **Tiny posterior run:** 77.68s on CPU
- **Dataset size:** 110 weekly observations
- **Channels modeled:** Search, Social, Video, TV, Affiliate
- **Controls included:** seasonality, economy, price, promos, organic sessions, holiday flag

The runtime summary is also saved as machine-readable JSON in `reports/meridian_runtime_check.json`.

## Practical interpretation
- Meridian is **installable and runnable** in this environment from the host shell.
- A **small CPU posterior** is feasible for portfolio/demo purposes.
- For day-to-day storytelling, the deterministic pipeline in `src/mmm_pipeline.py` is still useful because it regenerates charts and business insights in seconds instead of waiting on Bayesian sampling.

## Caveats
- This is a **national model**, so Meridian automatically resets some hierarchical parameters for national use and emits expected warnings.
- The server has **no CUDA GPU**, so TensorFlow falls back to CPU.
- The posterior run here is intentionally tiny. It proves runtime viability, not final production calibration quality.
