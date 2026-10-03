import glob, pandas as pd

files = sorted(glob.glob("data/raw/niftyindices/NIFTY_50_*.csv"))
df = pd.concat(pd.read_csv(f) for f in files)

df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y")
df = df.drop_duplicates("Date").sort_values("Date").reset_index(drop=True)

gaps = df["Date"].diff().dt.days

print(df["Date"].min(), df["Date"].max(), len(df))
print(df.loc[gaps > 5, "Date"])   # any hit = a missing chunkx