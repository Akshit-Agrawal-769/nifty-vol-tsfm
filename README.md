# nifty-vol-tsfm
Do time-series foundation models forecast Indian index volatility better than HAR/GARCH?

## Data
- Source: Nifty Indices historical data (niftyindices.com), downloaded [03-10-2026]; India VIX from nseindia.com, downloaded [03-10-2026]
- Indices (11): NIFTY 50, MIDCAP 100, BANK, FINANCIAL SERVICES, IT, FMCG, PHARMA, AUTO, METAL, ENERGY, REALTY, PSU BANK 
- Main sample: 2012-02-27 to 2026-10-01 (first date all indices have full OHLC)
- Excluded rows: see data/clean/excluded_rows.csv (early close-only history; one inconsistent MIDCAP 100 row, 2010-06-04)
- Raw data is not redistributed; run the scripts below to rebuild it.

## Reproduce
python src/build_panel.py
python src/build_vix.py
python src/eda.py

## Results so far
- results/estimator_comparison.csv: 20–37% of daily variance is overnight
- results/figures/rolling_vol.png