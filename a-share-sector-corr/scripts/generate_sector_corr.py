#!/usr/bin/env python3
"""Generate A-share theme sector correlation heatmaps."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns

TICKERS = {
    "AI": ["159819.SZ", "588200.SS"],
    "高端制造": ["159770.SZ", "159326.SZ"],
    "新能源电池": ["159755.SZ", "588830.SS"],
    "有色": ["159871.SZ"],
    "医药": ["159992.SZ"],
    "银行": ["512800.SS"],
    "消费": ["515170.SS", "159825.SZ", "159865.SZ"],
}

HEADERS = {"User-Agent": "Mozilla/5.0"}
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def yahoo_close(symbol: str, days: int = 160) -> pd.Series | None:
    end = int(datetime.now().timestamp())
    start = int((datetime.now() - timedelta(days=days)).timestamp())
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?period1={start}&period2={end}&interval=1d"
    )
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        result = r.json()["chart"]["result"][0]
        ts = result["timestamp"]
        closes = result["indicators"]["quote"][0]["close"]
        s = pd.Series(closes, index=pd.to_datetime(ts, unit="s")).dropna()
        s.index = s.index.tz_localize(None).normalize()
        return s
    except Exception as exc:  # noqa: BLE001
        print(f"Fail {symbol}: {exc}")
        return None


def build_group_returns(days: int = 160) -> pd.DataFrame:
    symbols = sorted({t for ts in TICKERS.values() for t in ts})
    price_dict: dict[str, pd.Series] = {}
    for sym in symbols:
        s = yahoo_close(sym, days=days)
        if s is not None and len(s) > 30:
            price_dict[sym] = s
            print(sym, "OK", len(s), s.index[-1].date(), round(float(s.iloc[-1]), 3))
        else:
            print(sym, "FAIL or short")

    prices = pd.DataFrame(price_dict).sort_index()
    rets = prices.pct_change()

    group = pd.DataFrame(index=rets.index)
    for name, members in TICKERS.items():
        avail = [t for t in members if t in rets.columns]
        if avail:
            group[name] = rets[avail].mean(axis=1)
            print(name, "→", avail)
        else:
            print(name, "→ NO DATA")

    group = group.dropna()
    print("Group shape:", group.shape)
    if not group.empty:
        print("Range:", group.index.min().date(), "→", group.index.max().date())
    return group


def save_heatmaps(group: pd.DataFrame, windows: list[int], outdir: Path) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    prop = None
    if Path(FONT_PATH).exists():
        fm.fontManager.addfont(FONT_PATH)
        prop = fm.FontProperties(fname=FONT_PATH)
    else:
        print(f"Warning: Chinese font not found at {FONT_PATH}; labels may not render correctly.")
    paths: list[Path] = []

    for w in windows:
        if len(group) < w:
            print(f"Not enough data for {w}-day window")
            continue
        recent = group.iloc[-w:]
        corr = recent.corr().round(2)
        print(f"\n===== 近{w}日（截至 {group.index[-1].date()}） =====")
        print(corr.to_string())

        fig, ax = plt.subplots(figsize=(9, 8))
        sns.heatmap(
            corr,
            annot=True,
            fmt=".2f",
            cmap="RdYlBu_r",
            center=0.2,
            vmin=-0.8,
            vmax=1.0,
            square=True,
            linewidths=0.7,
            cbar_kws={"shrink": 0.75},
            ax=ax,
            annot_kws={"size": 11},
        )
        title_kw = {"fontsize": 15, "pad": 14}
        if prop is not None:
            title_kw["fontproperties"] = prop
        ax.set_title(f"各版块相关性（近{w}个交易日）", **title_kw)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            if prop is not None:
                label.set_fontproperties(prop)
            label.set_fontsize(11)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
        cbar = ax.collections[0].colorbar
        if prop is not None:
            cbar.set_label("相关系数", fontproperties=prop, fontsize=11)
        else:
            cbar.set_label("相关系数", fontsize=11)
        plt.tight_layout()
        out = outdir / f"sector_corr_{w}d.png"
        fig.savefig(out, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print("Saved", out)
        paths.append(out)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--windows", default="5,10,20,60", help="Comma-separated windows")
    parser.add_argument("--outdir", default="./output")
    parser.add_argument("--days", type=int, default=160, help="Calendar days of history")
    args = parser.parse_args()

    windows = [int(x.strip()) for x in args.windows.split(",") if x.strip()]
    group = build_group_returns(days=args.days)
    if group.empty:
        raise SystemExit("No sector return data available")
    save_heatmaps(group, windows, Path(args.outdir))
    print("\nDone")


if __name__ == "__main__":
    main()
