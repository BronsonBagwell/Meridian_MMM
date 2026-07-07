# Meridian MMM Portfolio

A portfolio-ready marketing mix modeling project built around **Google's open-source Meridian**.

Most MMM demos make one of two mistakes: they are either technically cute but impossible to run, or visually polished but mostly bullshit. This repo tries not to do either.

It is designed to do two jobs well:
1. **Tell a clear business story** with charts, ROI takeaways, and stakeholder-friendly summaries.
2. **Prove the Meridian stack actually runs** on the same dataset instead of name-dropping Bayesian tooling for decoration.

## What this project shows
- A realistic synthetic weekly MMM dataset for a single-market ecommerce-style business
- A fast deterministic pipeline for portfolio visuals and business interpretation
- A lightweight but real **official Meridian** runtime check using the same inputs
- Clear documentation of what works, what is simplified, and what would change in production

## Why this repo exists
Hiring managers and recruiters usually do not want a 40-minute lecture on priors. They want to know:
- can this person structure an MMM problem cleanly?
- can they turn outputs into decisions?
- can they use a real framework without making the repo miserable to run?

This repo is built to answer **yes** to all three.

## Repository Layout
```text
├── data/
│   ├── synthetic_meridian_mmm.csv      # 110 weeks of synthetic spend + controls + outcomes
│   └── synthetic_metadata.json         # dataset profile
├── src/
│   ├── data_generation.py              # synthetic dataset generator
│   ├── mmm_pipeline.py                 # fast portfolio pipeline (adstock + saturation + ROI)
│   └── meridian_smoke_test.py          # official google-meridian runtime check
├── reports/
│   ├── executive_summary.md            # stakeholder-facing summary
│   ├── methodology_and_insights.md     # technical notes + business interpretation
│   ├── meridian_blockers.md            # precise runtime constraints and caveats
│   ├── meridian_runtime_check.md       # official Meridian proof-of-run summary
│   ├── meridian_runtime_check.json     # runtime details from smoke test
│   ├── meridian_vs_deterministic.md    # Meridian posterior ROI vs deterministic ROI comparison
│   ├── metrics.json                    # deterministic pipeline metrics, holdout MAPE, channel ROI
│   └── figures/
│       ├── channel_incremental_conversions.png
│       ├── conversions_actual_vs_predicted.png
│       └── response_curves.png
├── requirements.txt
└── README.md
```

## Quickstart
### Fast path
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/data_generation.py
MPLCONFIGDIR=reports/mplconfig python src/mmm_pipeline.py
python src/meridian_smoke_test.py
```

### Notebook path
```bash
pip install -r requirements-notebook.txt
jupyter notebook notebooks/meridian_walkthrough.ipynb
```

### Optional heavier check
```bash
python src/meridian_smoke_test.py --posterior
```

The default experience is intentionally light. The posterior run is optional because portfolio reviewers care more about a clean demo than watching your laptop do Bayesian CrossFit.

## What runs successfully
### 1) Portfolio pipeline
`src/mmm_pipeline.py` runs end-to-end and generates:
- actual vs. predicted conversions chart
- channel contribution chart
- response curve chart
- machine-readable metrics in `reports/metrics.json`

Observed result on the bundled dataset:
- **MAPE (in-sample, full fit):** 0.0211
- **Holdout MAPE (time-based out-of-sample):** 0.0294 — the same bounded solve refit on the first 88 weeks and scored on the final 22 weeks. Slightly worse than in-sample, which is expected and a sign the fit is not purely memorizing the estimation window.
- **Top ROI channels:** Affiliate (~3.88x), then Search and Social (both modest at ~0.19x)

The pipeline constrains media effects to be non-negative and includes an intercept, mirroring how real MMM tooling (including Meridian's priors) treats media contributions.

### 2) Official Meridian runtime check
`src/meridian_smoke_test.py` successfully:
- builds Meridian `InputData`
- instantiates a `Meridian` model
- samples from the prior

Observed lightweight result from the latest notebook/default run:
- **Model build:** 0.13s
- **Prior sample:** 0.06s
- **Posterior run:** skipped by default

### 3) Optional tiny posterior proof
`src/meridian_smoke_test.py --posterior` additionally:
- runs a tiny CPU posterior for runtime validation

Observed result on this server:
- **Posterior sample:** 77.68s

See `reports/meridian_runtime_check.md` for the readable version.

## Why there are two tracks
Because portfolio projects should be honest and pleasant to run.

- The **deterministic pipeline** is the default because it is fast, reproducible, and good for storytelling.
- The **official Meridian runtime check** exists to prove the repo is genuinely Meridian-oriented rather than just borrowing the vocabulary.

That split is intentional, not a compromise. It is the difference between a usable demo and a needlessly fragile science project.

## Business takeaway from the bundled run
- **Affiliate** is still the clear winner, with the best modeled ROI at **~3.88x**.
- **Search** contributes, but modestly, at about **0.19x** ROI.
- **Social** is in the same modest band as Search at about **0.19x** ROI.
- **TV** and **Video** show **no measurable positive incremental effect** once media effects are constrained non-negative (in the earlier unconstrained fit they appeared as artificial negatives). Their budgets should be challenged before more is spent.

## Limits of this portfolio
- The dataset is synthetic.
- The bundled Meridian smoke-test posterior is intentionally tiny; a modest 2-chain posterior (200 adapt / 200 burn-in / 200 kept) backs the ROI comparison in `reports/meridian_vs_deterministic.md`, but neither is production-grade inference.
- The data is national, not geo-level, so it does not showcase Meridian's richer hierarchical strengths.

## If this became a real case study
The next upgrade path is straightforward:
1. swap the synthetic CSV for real weekly geo-level data
2. tune priors and posterior settings properly in Meridian
3. compare Meridian posterior outputs with the fast deterministic baseline (a first directional comparison already lives in `reports/meridian_vs_deterministic.md`)
4. wrap the outputs in a lightweight decision-maker dashboard

## Best way to review this repo
If you are skimming, do this in order:
1. open `notebooks/meridian_walkthrough.ipynb`
2. read `reports/executive_summary.md`
3. inspect `reports/metrics.json`
4. check `reports/meridian_runtime_check.md`
5. see how the two tracks line up in `reports/meridian_vs_deterministic.md`

That gives you the business story, the technical proof, and the limitations without making you excavate the repo like an archaeologist.
