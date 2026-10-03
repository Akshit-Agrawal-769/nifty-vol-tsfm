import glob, numpy as np, pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

files = sorted(glob.glob(str(ROOT / "data/raw/indiavix/*.csv")))
vix = pd.concat(pd.read_csv(f) for f in files)
vix.columns = [c.strip() for c in vix.columns]
print(vix.columns.tolist(), vix.head(2))          # check names/format once
vix["Date"] = pd.to_datetime(vix["Date"], dayfirst=True, format="mixed")
vix = vix.drop_duplicates("Date").sort_values("Date").set_index("Date")
vix = vix[["Close"]].rename(columns={"Close": "india_vix"})
vix["india_vix"] = pd.to_numeric(vix["india_vix"].astype(str).str.replace(",", ""), errors="coerce")
vix.to_parquet(ROOT / "data/clean/india_vix.parquet")

# Sanity check: VIX should track NIFTY 50 realised vol
panel = pd.read_parquet(ROOT / "data/clean/panel.parquet")
n50 = panel.xs("NIFTY_50", level="index")
rv22 = np.sqrt(n50["gk_on"].rolling(22).mean() * 252) * 100
both = pd.concat([rv22.rename("rv22"), vix["india_vix"]], axis=1).dropna()
print("rows:", len(both), " corr(VIX, 22d realised vol):", round(both.corr().iloc[0, 1], 2))