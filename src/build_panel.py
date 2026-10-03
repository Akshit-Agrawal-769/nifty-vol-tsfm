import glob, os, numpy as np, pandas as pd

RAW, OUT = "data/raw/niftyindices", "data/clean"
os.makedirs(OUT, exist_ok=True)
PRICES = ["Open", "High", "Low", "Close"]

def load_index(folder):
    df = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{folder}/*.csv")))
    df.columns = [c.strip().title() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y")
    for c in PRICES:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", ""), errors="coerce")
    return df.drop_duplicates("Date").sort_values("Date").set_index("Date")[PRICES]

def variances(df):
    o, h, l, c = (np.log(df[x]) for x in PRICES)
    out = pd.DataFrame(index=df.index)
    out["ret"] = c - c.shift(1)
    out["overnight"] = (o - c.shift(1))**2
    out["parkinson"] = (h - l)**2 / (4*np.log(2))
    out["gk"] = 0.5*(h - l)**2 - (2*np.log(2) - 1)*(c - o)**2
    out["rs"] = (h - c)*(h - o) + (l - c)*(l - o)
    out["gk_on"] = out["gk"] + out["overnight"]
    return out

reports, excluded, panel = [], [], {}
for folder in sorted(glob.glob(f"{RAW}/*")):
    name = os.path.basename(folder)
    df = load_index(folder)
    print(f"\n=== {name}")

    # 1) close-only rows: drop the leading block, flag any later ones
    full = df[PRICES].notna().all(axis=1)
    first_full = full.idxmax()
    lead = df.loc[:first_full].iloc[:-1]
    later = df.loc[first_full:][~full.loc[first_full:]]
    print(f"first full OHLC: {first_full.date()}  (dropped {len(lead)} leading close-only rows)")
    if len(later): print("  WARNING close-only rows after start:", [d.date() for d in later.index])
    for d in lead.index: excluded.append((name, d.date(), "close-only (pre-OHLC history)"))
    df = df.loc[first_full:].dropna()

    # 2) gaps > 5 calendar days
    gaps = df.index.to_series().diff().dt.days
    for d, g in gaps[gaps > 5].items():
        print(f"  gap of {int(g)} days ending {d.date()}")

    # 3) bad high/low rows -> keep row, mark range-based variances missing
    bad = (df.High < df[["Open","Close"]].max(axis=1)) | (df.Low > df[["Open","Close"]].min(axis=1))
    if bad.any(): print("  bad high/low rows:\n", df[bad])
    for d in df.index[bad]: excluded.append((name, d.date(), "high/low inconsistent"))

    # 4) big moves (check against news; keep if genuine)
    big = np.log(df.Close).diff().abs()
    print("  >10% moves on:", [d.date() for d in big[big > 0.10].index])

    v = variances(df)
    v.loc[bad, ["parkinson", "gk", "rs", "gk_on"]] = np.nan
    panel[name] = pd.concat([df, v], axis=1)
    reports.append({"index": name, "start": df.index.min().date(), "end": df.index.max().date(),
                    "rows": len(df), "bad_hilo": int(bad.sum()), "gaps_gt5d": int((gaps > 5).sum())})

report = pd.DataFrame(reports)
common_start = max(report["start"])
print("\n", report.to_string(index=False))
print(f"\nCommon start date (all indices have full OHLC): {common_start}")

report.to_csv(f"{OUT}/quality_report.csv", index=False)
pd.DataFrame(excluded, columns=["index", "date", "reason"]).to_csv(f"{OUT}/excluded_rows.csv", index=False)
pd.concat(panel, names=["index", "date"]).to_parquet(f"{OUT}/panel.parquet")