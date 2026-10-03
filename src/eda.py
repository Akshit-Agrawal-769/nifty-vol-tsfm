import numpy as np, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"; FIG.mkdir(parents=True, exist_ok=True)
SAMPLE_START = "2012-02-27"

panel = pd.read_parquet(ROOT / "data/clean/panel.parquet")
panel = panel[panel.index.get_level_values("date") >= SAMPLE_START]
idx = panel.index.get_level_values("index").unique()

# Rolling 22-day volatility, one panel per index
fig, axes = plt.subplots(4, 3, figsize=(15, 12), sharex=True)
for ax, name in zip(axes.flat, idx):
    d = panel.xs(name, level="index")
    ann = np.sqrt(d["gk_on"].rolling(22).mean() * 252) * 100
    ax.plot(ann.index, ann, lw=0.8); ax.set_title(name, fontsize=9); ax.set_ylabel("% ann.")
for ax in axes.flat[len(idx):]: ax.axis("off")
plt.tight_layout(); plt.savefig(FIG / "rolling_vol.png", dpi=150); plt.close()

# Average annualised volatility by estimator
rows = []
for name in idx:
    d = panel.xs(name, level="index")
    rows.append({
        "index": name,
        "close_to_close": d["ret"].std() * np.sqrt(252) * 100,
        "parkinson": np.sqrt(d["parkinson"].mean() * 252) * 100,
        "garman_klass": np.sqrt(d["gk"].mean() * 252) * 100,
        "rogers_satchell": np.sqrt(d["rs"].mean() * 252) * 100,
        "gk_plus_overnight": np.sqrt(d["gk_on"].mean() * 252) * 100,
    })
tab = pd.DataFrame(rows).round(1)
tab["overnight_share_%"] = (100 * (1 - (tab.garman_klass / tab.gk_plus_overnight) ** 2)).round(0)
print(tab.to_string(index=False))
tab.to_csv(ROOT / "results" / "estimator_comparison.csv", index=False)