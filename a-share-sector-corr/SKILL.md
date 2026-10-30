---
name: a-share-sector-corr
description: Generate Chinese A-share theme sector correlation heatmaps for fixed windows (5/10/20/60 trading days). Use when the user asks for 各板块相关性, 板块相关系数, AI/高端制造/新能源/有色/医药/银行/消费 热力图, sector correlation charts, or to regenerate the usual domestic sector correlation figures.
---

# A-Share Sector Correlation Heatmaps

Generate Pearson correlation heatmaps for the standard domestic theme sectors used in this workflow.

## Default sectors

Equal-weight daily returns of the listed ETFs:

| Sector | ETF codes |
|--------|-----------|
| AI | 159819.SZ, 588200.SS |
| 高端制造 | 159770.SZ, 159326.SZ |
| 新能源电池 | 159755.SZ, 588830.SS |
| 有色 | 159871.SZ |
| 医药 | 159992.SZ |
| 银行 | 512800.SS |
| 消费 | 515170.SS, 159825.SZ, 159865.SZ |

Do not change the mapping unless the user explicitly asks. Multi-ETF sectors use mean of available member daily returns.

## Windows and titles

Always produce four charts unless the user asks for a subset:

- 近5个交易日
- 近10个交易日
- 近20个交易日
- 近60个交易日

Title format:

```text
各版块相关性（近{N}个交易日）
```

Save files to:

```text
/home/workdir/artifacts/sector_corr_{N}d.png
```

## Data fetch

Prefer the Yahoo chart API via `requests` (no yfinance dependency required):

```python
url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start}&period2={end}&interval=1d"
```

Use adjusted close when available. Align dates, drop rows with missing sector returns, then compute `pct_change()`.

Fetch about 160 calendar days of history so the 60-day window is reliable after weekends/holidays.

If Yahoo fails for a ticker, skip that ticker and build the sector from remaining members. If a whole sector has no data, omit it and note the omission.

## Correlation method

- Input series: daily returns
- Statistic: Pearson correlation (`pandas.DataFrame.corr()`, sample covariance, `ddof=1`)
- Round displayed values to 2 decimals

## Chart style

- Library: matplotlib + seaborn heatmap
- Colormap: `RdYlBu_r`
- `center=0.2`, `vmin=-0.8`, `vmax=1.0`
- Annotate cells with correlation values
- Chinese labels require Noto CJK:

```python
font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
fm.fontManager.addfont(font_path)
prop = fm.FontProperties(fname=font_path)
```

Apply `prop` to title, tick labels, and colorbar label (`相关系数`).

## Preferred execution

When possible, run the bundled script instead of rewriting the pipeline:

```bash
python3 /home/workdir/.grok/skills/a-share-sector-corr/scripts/generate_sector_corr.py
```

Optional args:

```bash
python3 .../generate_sector_corr.py --windows 5,10,20,60 --outdir /home/workdir/artifacts
```

## Response pattern

1. State the data-as-of date (last available trading day).
2. Render the four PNG files with `render_file`.
3. Briefly list sector composition.
4. Ask whether the user wants an interpretation.

## Common follow-ups

- Explain one pair (e.g. 银行 vs 高端制造): show the last N daily returns and step through Pearson formula.
- Regenerate after market close on a later date: rerun the same script/pipeline.
- Modify sectors: update the mapping table first, then regenerate.
