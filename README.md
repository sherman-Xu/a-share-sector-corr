# a-share-sector-corr

Agent Skill for generating Chinese A-share theme sector **Pearson correlation heatmaps** (5 / 10 / 20 / 60 trading days).

Compatible with the open [Agent Skills](https://agentskills.io) standard (`SKILL.md`).

## Sectors

| Sector | ETF codes (equal-weight returns) |
|--------|-----------------------------------|
| AI | 159819.SZ, 588200.SS |
| 高端制造 | 159770.SZ, 159326.SZ |
| 新能源电池 | 159755.SZ, 588830.SS |
| 有色 | 159871.SZ |
| 医药 | 159992.SZ |
| 银行 | 512800.SS |
| 消费 | 515170.SS, 159825.SZ, 159865.SZ |

## Install

### Option A — skills CLI
```bash
npx skills add https://github.com/<YOUR_USER>/a-share-sector-corr
```

### Option B — manual
Copy the `a-share-sector-corr/` folder into one of:
- `~/.claude/skills/a-share-sector-corr/`
- `.agents/skills/a-share-sector-corr/`
- your agent's equivalent skills directory

## Run the script directly
```bash
pip install pandas matplotlib seaborn requests
python3 a-share-sector-corr/scripts/generate_sector_corr.py \
  --windows 5,10,20,60 \
  --outdir ./output
```

Optional flags:
- `--days 160` — calendar days of history to fetch
- `--outdir PATH` — where to save `sector_corr_{N}d.png`

## Data source
Daily closes from Yahoo Finance chart API for the listed China ETFs. Network access required. Results depend on market data availability.

## Method
- Daily returns: `pct_change()`
- Correlation: Pearson (`pandas.DataFrame.corr()`, sample covariance)
- Charts: seaborn heatmap, Chinese labels via Noto CJK when available

## License
MIT
