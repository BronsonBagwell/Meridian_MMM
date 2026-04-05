# Methodology, Insights, and Limitations

## What this document is for
This repo has two audiences:
- people who want the business takeaway quickly
- people who want to know whether the technical setup is real or just dressed-up MMM theater

This document is for the second group.

## Data design
- `data/synthetic_meridian_mmm.csv` contains **110 weekly observations** from 2022-01-03 to 2024-02-05.
- The dataset includes paid media spend for **Search, Social, Video, TV, and Affiliate** plus control variables for seasonality, pricing, macro conditions, promos, organic traffic, and holidays.
- `src/data_generation.py` makes the synthetic assumptions inspectable instead of hand-wavy, which matters in a portfolio project.

The dataset is synthetic on purpose. That keeps the repo shareable, reproducible, and honest about what is demonstration versus what would require real client data.

## Modeling approach
This repo uses a **two-track structure** instead of forcing one tool to do every job badly.

### Track 1: Fast portfolio pipeline
Implemented in `src/mmm_pipeline.py`.

What it does:
- adstock transformation by channel
- saturation/response-curve transformation
- regression-based decomposition into channel contributions
- ROI summary by channel
- chart generation and JSON metric export

Why it exists:
- it runs in seconds
- it is easy for reviewers to reproduce
- it generates the charts and metrics that actually carry the portfolio story

This is the default path because it optimizes for clarity, speed, and inspectability.

### Track 2: Official Meridian runtime check
Implemented in `src/meridian_smoke_test.py`.

What it does:
- converts the synthetic dataset into Meridian `InputData`
- maps spend into a simple exposure proxy so the package can be exercised realistically
- builds a real `Meridian` model
- samples from the prior
- optionally runs a tiny posterior on CPU

Observed runtime in this repo:
- model build: **0.36s**
- prior sample: **0.23s**
- tiny posterior: **77.68s** when explicitly enabled

See `reports/meridian_runtime_check.md` and `reports/meridian_runtime_check.json`.

## Why the split is intentional
This is not two half-finished solutions. It is one sensible portfolio architecture.

- The deterministic path is what makes the repo pleasant to review.
- The Meridian path is what makes the repo technically credible.

Together, they answer the useful question: can this person produce a clear MMM-style recommendation flow **and** use a real Bayesian framework without turning the project into sludge?

## Main business insights from the deterministic run
1. **Affiliate has the strongest headroom.**
   - ~30k incremental conversions
   - ~4.75x modeled ROI
   - low weekly base spend makes scaling tests look justified

2. **Search is still worth protecting.**
   - ~37k incremental conversions
   - ~1.41x modeled ROI
   - fits the classic demand-capture pattern: not glamorous, still valuable

3. **Social is positive, but not a star.**
   - ~0.79x modeled ROI
   - potentially maintainable, but not the first place to look for aggressive growth

4. **TV and Video look bloated in the current mix.**
   - both show negative modeled contribution in this synthetic setup
   - that usually points to saturation, weak creative, poor timing, overlap, or simple over-allocation

5. **Controls matter.**
   - seasonality, promos, and organic activity all explain part of the outcome variation
   - that keeps the media story from collapsing into fake certainty

## Why this is portfolio-worthy
A lot of MMM demos fail in predictable ways:
- they are mathematically cute but unusable
- they are visually polished but technically hollow
- they imply production-grade rigor where none exists

This repo avoids that by being explicit about tradeoffs:
- the charts and stakeholder summary are ready to show
- the official Meridian package is actually installed and exercised
- the limitations are written down instead of hidden behind jargon

## Important limitations
- **Synthetic data:** useful for demonstration, not for real budget decisions.
- **National model:** does not show Meridian's richer geo-level hierarchical strengths.
- **Lightweight default Meridian path:** proves runtime viability, not full posterior rigor.
- **Tiny posterior option:** helpful as extra proof, but still not equivalent to a production-quality inference setup.
- **Exposure proxy:** media exposures are approximated from spend using simple CPM-style assumptions for the smoke test.

## What would change in a real deployment
If this moved from portfolio artifact to real case work, the upgrade path is straightforward:
1. replace the synthetic CSV with real weekly geo-level data
2. define stronger priors and posterior settings in Meridian
3. validate Meridian outputs against the fast deterministic baseline
4. add diagnostics, scenario planning, and budget-allocation outputs for decision-makers
5. package the results in a lightweight dashboard or recurring reporting workflow

## Final takeaway
The point of this repo is not to fake a complete enterprise MMM deployment. The point is to show the harder and more useful skill set: structuring the problem cleanly, producing believable outputs, documenting tradeoffs honestly, and leaving a realistic path into a fuller Meridian workflow.

That is a much better signal than a repo that looks impressive until someone actually tries to run it.
