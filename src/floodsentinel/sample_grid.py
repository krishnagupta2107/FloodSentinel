"""
Visual grid banayenge 12 sample predictions ka, check karne ke liye.
"""

import random
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

PRED_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "runs"
    / "detect"
    / "predictions_v3_test"
)
OUT_FILE = (
    Path(__file__).resolve().parent.parent.parent
    / "runs"
    / "detect"
    / "flood_sentinels_v3"
    / "sample_predictions.png"
)

images = sorted(PRED_DIR.glob("*.jpg"))
print(f"Total predicted images: {len(images)}")

random.seed(42)
sample = random.sample(images, min(12, len(images)))

fig, axes = plt.subplots(3, 4, figsize=(22, 14))
fig.patch.set_facecolor("#0F0F23")
fig.suptitle(
    "Flood Sentinels v3 - Sample Predictions (Test Set, conf=0.25)",
    fontsize=16,
    fontweight="bold",
    color="white",
    y=0.98,
)

for ax, img_path in zip(axes.flat, sample):
    img = mpimg.imread(img_path)
    ax.imshow(img)
    ax.set_title(img_path.stem[:35] + "...", fontsize=7, color="#AAAAAA", pad=4)
    ax.axis("off")
    for spine in ax.spines.values():
        spine.set_edgecolor("#333355")

for ax in axes.flat[len(sample) :]:
    ax.axis("off")

plt.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(OUT_FILE, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved: {OUT_FILE}")
plt.close()
