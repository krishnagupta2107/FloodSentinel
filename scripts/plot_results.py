import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import sys

RESULTS_CSV = Path(r"c:/Users/Lenovo/OneDrive/Desktop/Flood Sentinals/runs/detect/flood_sentinels_v3/results.csv")
OUT_DIR = RESULTS_CSV.parent

if not RESULTS_CSV.exists():
    print("ERROR: results.csv not found at", RESULTS_CSV)
    sys.exit(1)

df = pd.read_csv(RESULTS_CSV)
df.columns = df.columns.str.strip()
print("Columns:", list(df.columns))
epochs = df["epoch"] + 1

TC = "#00D4FF"; VC = "#FF6B6B"; M50 = "#FFD93D"
M95 = "#6BCB77"; PC = "#FF922B"; RC = "#CC5DE8"

def style(ax, title, ylabel=""):
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("Epoch", fontsize=10, color="#AAAAAA")
    ax.set_ylabel(ylabel, fontsize=10, color="#AAAAAA")
    ax.tick_params(colors="#AAAAAA")
    ax.grid(True, linestyle="--", alpha=0.3, color="#555555")
    ax.legend(fontsize=9, framealpha=0.4)
    for sp in ax.spines.values():
        sp.set_edgecolor("#444444")

plt.style.use("dark_background")

# Figure 1: Loss Curves
fig1, axes = plt.subplots(1, 3, figsize=(18, 5))
fig1.patch.set_facecolor("#1A1A2E")
fig1.suptitle("Training vs Validation Loss", fontsize=16, fontweight="bold", color="white", y=1.02)
loss_pairs = [
    ("train/box_loss","val/box_loss","Box Loss"),
    ("train/cls_loss","val/cls_loss","Class Loss"),
    ("train/dfl_loss","val/dfl_loss","DFL Loss"),
]
for ax,(tc,vc,title) in zip(axes, loss_pairs):
    ax.set_facecolor("#16213E")
    if tc in df.columns: ax.plot(epochs, df[tc], color=TC, lw=2, label="Train", marker="o", ms=3)
    if vc in df.columns: ax.plot(epochs, df[vc], color=VC, lw=2, label="Val",   marker="s", ms=3, ls="--")
    style(ax, title, "Loss")
fig1.tight_layout()
out1 = OUT_DIR / "loss_curves.png"
fig1.savefig(out1, dpi=150, bbox_inches="tight", facecolor=fig1.get_facecolor())
print("Saved:", out1)

# Figure 2: Accuracy
fig2, axes2 = plt.subplots(1, 3, figsize=(18, 5))
fig2.patch.set_facecolor("#1A1A2E")
fig2.suptitle("Model Accuracy Metrics", fontsize=16, fontweight="bold", color="white", y=1.02)
cols_map = [
    ("metrics/mAP50(B)","metrics/mAP50-95(B)","mAP@0.5 vs mAP@0.5:0.95",M50,M95,"mAP@0.5","mAP@0.5:0.95"),
    ("metrics/precision(B)",None,"Precision",PC,None,"Precision",None),
    ("metrics/recall(B)",None,"Recall",RC,None,"Recall",None),
]
for ax,(c1,c2,title,col1,col2,l1,l2) in zip(axes2, cols_map):
    ax.set_facecolor("#16213E")
    if c1 in df.columns: ax.plot(epochs, df[c1], color=col1, lw=2, label=l1, marker="o", ms=3)
    if c2 and c2 in df.columns: ax.plot(epochs, df[c2], color=col2, lw=2, label=l2, marker="s", ms=3, ls="--")
    style(ax, title, "Score")
    ax.set_ylim(0, 1.05)
fig2.tight_layout()
out2 = OUT_DIR / "accuracy_metrics.png"
fig2.savefig(out2, dpi=150, bbox_inches="tight", facecolor=fig2.get_facecolor())
print("Saved:", out2)

# Figure 3: Dashboard
fig3 = plt.figure(figsize=(20, 10))
fig3.patch.set_facecolor("#0F0F23")
fig3.suptitle("Flood Sentinels - YOLOv8 Training Dashboard", fontsize=18, fontweight="bold", color="white", y=0.98)
gs = gridspec.GridSpec(2, 4, figure=fig3, hspace=0.45, wspace=0.4)
panels = [
    (gs[0,0],"train/box_loss","val/box_loss","Box Loss",TC,VC,"Train","Val"),
    (gs[0,1],"train/cls_loss","val/cls_loss","Cls Loss",TC,VC,"Train","Val"),
    (gs[0,2],"train/dfl_loss","val/dfl_loss","DFL Loss",TC,VC,"Train","Val"),
    (gs[0,3],"metrics/mAP50(B)","metrics/mAP50-95(B)","mAP",M50,M95,"mAP@0.5","mAP@0.5:0.95"),
    (gs[1,0],"metrics/precision(B)",None,"Precision",PC,None,"Precision",None),
    (gs[1,1],"metrics/recall(B)",None,"Recall",RC,None,"Recall",None),
]
for spec,c1,c2,title,col1,col2,l1,l2 in panels:
    ax = fig3.add_subplot(spec)
    ax.set_facecolor("#16213E")
    if c1 in df.columns: ax.plot(epochs, df[c1], color=col1, lw=2, label=l1, marker="o", ms=2)
    if c2 and c2 in df.columns: ax.plot(epochs, df[c2], color=col2, lw=2, label=l2, marker="s", ms=2, ls="--")
    style(ax, title)

last = df.iloc[-1]
def safe(c): return f"{last[c]:.4f}" if c in df.columns else "N/A"
ax_t = fig3.add_subplot(gs[1, 2:])
ax_t.set_facecolor("#0D1B2A")
ax_t.axis("off")
lines = [
    f"  Final Epoch Summary (Epoch {int(last['epoch'])+1})",
    "",
    f"  Train Box Loss  : {safe('train/box_loss')}",
    f"  Train Cls Loss  : {safe('train/cls_loss')}",
    f"  Train DFL Loss  : {safe('train/dfl_loss')}",
    "",
    f"  Val Box Loss    : {safe('val/box_loss')}",
    f"  Val Cls Loss    : {safe('val/cls_loss')}",
    "",
    f"  mAP@0.5         : {safe('metrics/mAP50(B)')}",
    f"  mAP@0.5:0.95    : {safe('metrics/mAP50-95(B)')}",
    f"  Precision       : {safe('metrics/precision(B)')}",
    f"  Recall          : {safe('metrics/recall(B)')}",
]
ax_t.text(0.05, 0.95, "\n".join(lines), transform=ax_t.transAxes,
          fontsize=11, va="top", fontfamily="monospace", color="#E0E0E0",
          bbox=dict(boxstyle="round,pad=0.8", facecolor="#1A2744", edgecolor="#3A5A8A", lw=1.5))

out3 = OUT_DIR / "training_dashboard.png"
fig3.savefig(out3, dpi=150, bbox_inches="tight", facecolor=fig3.get_facecolor())
print("Saved:", out3)
plt.close("all")
print("All 3 graphs saved to:", OUT_DIR)
