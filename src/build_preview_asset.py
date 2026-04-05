"""Assemble a lightweight README preview image from the generated report figures."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = PROJECT_ROOT / "reports" / "figures"
OUTPUT_PATH = PROJECT_ROOT / "assets" / "readme_preview.png"

PANEL_SPECS = [
    ("conversions_actual_vs_predicted.png", "Model fit"),
    ("channel_incremental_conversions.png", "Channel contribution"),
    ("response_curves.png", "Response curves"),
]


def main() -> None:
    missing = [name for name, _ in PANEL_SPECS if not (FIG_DIR / name).exists()]
    if missing:
        missing_str = ", ".join(missing)
        raise SystemExit(f"Missing figure(s): {missing_str}. Run src/mmm_pipeline.py first.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(16, 10), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=[1.1, 1.0])

    top_ax = fig.add_subplot(grid[0, :])
    bottom_left_ax = fig.add_subplot(grid[1, 0])
    bottom_right_ax = fig.add_subplot(grid[1, 1])
    axes = [top_ax, bottom_left_ax, bottom_right_ax]

    for ax, (filename, title) in zip(axes, PANEL_SPECS):
        image = plt.imread(FIG_DIR / filename)
        ax.imshow(image)
        ax.set_title(title, fontsize=16)
        ax.axis("off")

    fig.suptitle("Meridian MMM portfolio preview", fontsize=20)
    fig.savefig(OUTPUT_PATH, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
