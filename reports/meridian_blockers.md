# Meridian Runtime Notes and Residual Blockers

## What initially failed
The first isolated build attempt hit environment-level network resolution issues. In that environment, `pip install google-meridian` failed with DNS resolution errors (`[Errno -2] Name or service not known`).

## What actually worked
Outside that restricted environment, the project virtual environment was able to install `google-meridian==1.5.3` successfully from PyPI. After installation:
- `import meridian` worked
- a Meridian model object was created from the synthetic dataset
- prior sampling succeeded
- a tiny posterior run on CPU succeeded in about 78 seconds

See `src/meridian_smoke_test.py` and `reports/meridian_runtime_check.md` for the reproducible proof.

## Remaining practical blockers
These are real constraints worth documenting for reviewers:

1. **CPU-only runtime**
   - TensorFlow reports that CUDA is unavailable, so Meridian runs on CPU.
   - Fine for small demos, slower for richer posterior analysis.

2. **Tiny posterior only in this portfolio**
   - The included Meridian run is intentionally lightweight (`1` chain, `10` adapt, `10` burn-in, `10` kept samples).
   - Good enough to prove viability, not enough for production-grade posterior diagnostics.

3. **National synthetic dataset**
   - This portfolio uses a single-market national dataset.
   - Meridian emits expected warnings that some hierarchical parameters are deterministically zero for national models.
   - A geo-level dataset would be more realistic for a full-scale production Meridian engagement.

## Why the fallback pipeline still exists
The deterministic pipeline in `src/mmm_pipeline.py` is kept on purpose:
- it renders the portfolio charts quickly
- it provides instant business storytelling for reviewers
- it lets a hiring manager run the project without waiting on Bayesian sampling

In short: Meridian works here, but the fast fallback is the better portfolio default while the official Meridian smoke test proves technical credibility.
