import numpy as np, pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
panel = pd.read_parquet(ROOT / "data/clean/panel.parquet")
panel = panel[panel.index.get_level_values("date") >= "2012-02-27"]

rows = []
for name in panel.index.get_level_values("index").unique():
    d = panel.xs(name, level="index")
    base = d["gk_on"].rolling(66, min_periods=22).median().shift(1)   # past ~3 months only
    ratio = d["gk_on"] / base
    for date in ratio[ratio > 20].index:
        r = d.loc[date]
        rows.append({"index": name, "date": date.date(), "ratio_to_median": round(ratio[date], 1),
                     "open": r.Open, "high": r.High, "low": r.Low, "close": r.Close,
                     "intraday_range_%": round(100 * np.log(r.High / r.Low), 2),
                     "close_move_%": round(100 * r.ret, 2), "event": ""})

flags = pd.DataFrame(rows).sort_values(["date", "index"])
print(flags.to_string(index=False))
print("\nNIFTY_50 on 2012-10-05:\n", panel.loc[("NIFTY_50", "2012-10-05")])
flags.to_csv(ROOT / "results" / "flagged_days.csv", index=False)