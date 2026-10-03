# nifty-vol-tsfm
Do time-series foundation models forecast Indian index volatility better than HAR/GARCH?

## Data
- Index OHLC: Nifty Indices historical data (niftyindices.com), downloaded [3 Oct 2026]
- India VIX: nseindia.com historical VIX, downloaded [3 Oct 2026]
- Indices (12): NIFTY 50, MIDCAP 100, BANK, FINANCIAL SERVICES, IT, FMCG, PHARMA, AUTO, METAL, ENERGY, REALTY, PSU BANK
- Main sample: 2012-02-27 to 2026-10-01 (first date all 12 indices have full OHLC)
- Excluded rows: data/clean/excluded_rows.csv (early close-only history; one inconsistent MIDCAP 100 row on 2010-06-04)
- Flagged extreme days: results/flagged_days.csv (kept in the main analysis; capped in a robustness check)
- Volatility target: Garman-Klass + squared overnight return (`gk_on`)
- Raw data is not redistributed; run the scripts below to rebuild it.

## Reproduce
python src/build_panel.py
python src/build_vix.py
python src/eda.py
python src/flag_outliers.py

## Results so far
- results/estimator_comparison.csv: 20–37% of daily variance occurs overnight;
  range-only estimators understate NIFTY 50 volatility (12.9% vs 16.2% annualised)
- results/figures/rolling_vol.png: 22-day rolling volatility, all indices
- results/flagged_days.csv: extreme days with event labels