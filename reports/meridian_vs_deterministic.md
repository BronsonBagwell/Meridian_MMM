# Meridian Posterior ROI vs. Deterministic ROI

This report closes the gap flagged elsewhere in the repo: the two modeling tracks used to run on the same dataset without ever being compared numerically. Below is that comparison.

## Setup

- **Data:** the bundled synthetic national-level dataset (`data/synthetic_meridian_mmm.csv`, 110 weekly observations), converted to Meridian `InputData` exactly as in `src/meridian_smoke_test.py` (spend mapped to exposure via simple CPM assumptions, `max_lag=4`).
- **Meridian posterior settings:** `google-meridian==1.5.3`, **2 chains, 200 adaptation, 200 burn-in, 200 kept draws per chain** (400 retained draws total), seed 42, CPU-only. Sampling took **~42 seconds** on this machine. This is a meaningful step up from the 1-chain 10/10/10 runtime smoke test, but still far short of a production posterior (which would use more chains, more draws, and convergence diagnostics).
- **Deterministic ROI:** from `reports/metrics.json`, produced by `src/mmm_pipeline.py` (bounded least squares with non-negative media coefficients and an intercept).
- **Posterior ROI:** per-channel `roi` draws from Meridian's `Analyzer`, summarized as the posterior mean and the 5th–95th percentile (90% credible interval).

## Results

| Channel   | Deterministic ROI | Meridian posterior mean ROI | Meridian 90% credible interval |
|-----------|------------------:|----------------------------:|-------------------------------:|
| Affiliate | 3.88x             | 3.65x                       | [2.08x, 6.02x]                 |
| Search    | 0.19x             | 1.80x                       | [1.28x, 2.76x]                 |
| Social    | 0.19x             | 1.56x                       | [0.80x, 2.58x]                 |
| Video     | 0.00x             | 2.17x                       | [1.02x, 5.12x]                 |
| TV        | 0.00x             | 1.25x                       | [0.87x, 1.78x]                 |

## Honest reading

**Where they agree:** both tracks rank **Affiliate as the clear best channel**, and the point estimates are strikingly close (3.88x deterministic vs. 3.65x posterior mean, with the deterministic value sitting comfortably inside the 90% credible interval). That is the headline business conclusion of the repo, and it survives the switch from a bounded least-squares fit to a Bayesian model.

**Where they diverge:** the deterministic solve pins **Video and TV at exactly zero** (the non-negativity bound is active) and gives Search and Social only ~0.19x, while Meridian assigns every channel a positive ROI with credible intervals mostly above 1x. This divergence is expected rather than alarming: Meridian's default ROI priors are informative and centered on positive values, and with only 110 national-level (single-geo) weekly observations and a small posterior, the data is not strong enough to pull prior-influenced channels down to zero. The deterministic model, by contrast, has no prior and happily zeroes out channels that add no in-sample explanatory power.

**Caveats:** this is a **directional comparison only**. The dataset is synthetic and national (no geo hierarchy for Meridian to exploit), the posterior is small and was run without formal convergence diagnostics (R-hat, ESS), and the exposure series is a CPM-based proxy derived from spend. None of these numbers should be read as decision-grade; the point is that the two tracks now talk to each other, agree on the winner, and disagree exactly where a prior-driven Bayesian model and an unregularized bounded fit would be expected to disagree.
