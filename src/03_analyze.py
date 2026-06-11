"""
03_analyze.py

Aggregate the tagged reviews into:
  - category summary (negative volume, % negative, avg rating, up-votes)
  - weekly trend per category
  - top representative quotes per category
  - charts (reports/figures/) and CSV extracts for the dashboard (dashboard/*.csv)

Also prints a summary to stdout.

Input : data/processed/reviews_tagged.csv
Output: reports/figures/*.png, dashboard/*.csv
"""
from __future__ import annotations
import re
import sys
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAGGED = ROOT / "data" / "processed" / "reviews_tagged.csv"
FIG = ROOT / "reports" / "figures"
DASH = ROOT / "dashboard"

CATS = [
    "Billing & Subscription", "Pro / Paywall / Watermark", "Crashes & Performance",
    "Login & Account", "Export & Quality", "Editor & Usability",
    "Templates / Fonts / Content", "Ads", "AI Features", "Feature Requests",
    "Customer Support", "Praise",
]
TOP_N = 5


def clean(text: str, width: int = 240) -> str:
    t = re.sub(r"\s+", " ", str(text)).strip()
    return textwrap.shorten(t, width=width, placeholder=" …")


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    DASH.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TAGGED, parse_dates=["at", "week"])
    for c in CATS:
        df[c] = df[c].astype(bool)
    neg = df[df["sentiment"] == "Negative"]

    total = len(df)
    print("=" * 70)
    print(f"DATASET: {total:,} reviews | {df['at'].min():%Y-%m-%d} → {df['at'].max():%Y-%m-%d}")
    print(f"Avg rating: {df['score'].mean():.2f} | "
          f"Negative {len(neg)/total:.0%} | "
          f"Positive {(df['sentiment']=='Positive').mean():.0%}")

    # --- category summary --------------------------------------------------
    rows = []
    for c in CATS:
        mentions = int(df[c].sum())
        neg_m = int((df[c] & (df["sentiment"] == "Negative")).sum())
        if mentions == 0:
            continue
        rows.append({
            "category": c,
            "total_mentions": mentions,
            "negative_mentions": neg_m,
            "pct_negative": round(neg_m / mentions, 3),
            "avg_rating": round(df.loc[df[c], "score"].mean(), 2),
            "neg_upvotes": int(df.loc[df[c] & (df["sentiment"] == "Negative"), "thumbsUpCount"].sum()),
        })
    summary = pd.DataFrame(rows).sort_values("negative_mentions", ascending=False)
    summary.to_csv(DASH / "category_summary.csv", index=False)

    pain = summary[summary["category"] != "Praise"].head(TOP_N)
    print("\nTOP PAIN POINTS (by negative volume):")
    print(pain.to_string(index=False))

    # --- weekly trend for top pain points ----------------------------------
    trend_rows = []
    for c in pain["category"]:
        wk = (df[df[c] & (df["sentiment"] == "Negative")]
              .groupby("week").size())
        for week, n in wk.items():
            trend_rows.append({"week": week.date(), "category": c, "negative_mentions": int(n)})
    trend = pd.DataFrame(trend_rows)
    trend.to_csv(DASH / "weekly_trend.csv", index=False)

    print("\nRISING ISSUES (last 2 wks vs first 2 wks, negative volume):")
    pivot = trend.pivot_table(index="week", columns="category",
                              values="negative_mentions", aggfunc="sum").fillna(0).sort_index()
    full_weeks = pivot.iloc[1:-1] if len(pivot) > 3 else pivot  # drop partial end weeks
    for c in pain["category"]:
        if c not in full_weeks.columns or len(full_weeks) < 4:
            continue
        first, last = full_weeks[c].iloc[:2].mean(), full_weeks[c].iloc[-2:].mean()
        chg = (last - first) / first * 100 if first else 0
        arrow = "▲" if chg > 10 else "▼" if chg < -10 else "→"
        print(f"  {arrow} {c:<32} {first:5.1f} → {last:5.1f} /wk ({chg:+.0f}%)")

    # --- representative quotes ---------------------------------------------
    print("\nREPRESENTATIVE VERBATIMS (most-upvoted 1–2★ per pain point):")
    quote_rows = []
    for c in pain["category"]:
        sub = (df[df[c] & (df["score"] <= 2)]
               .sort_values("thumbsUpCount", ascending=False).head(3))
        print(f"\n  ── {c} ──")
        for _, r in sub.iterrows():
            print(f"    [{r['score']}★ · {int(r['thumbsUpCount'])}👍 · {r['at']:%Y-%m-%d}] {clean(r['content'])}")
            quote_rows.append({"category": c, "score": r["score"],
                               "upvotes": int(r["thumbsUpCount"]),
                               "date": r["at"].date(), "quote": clean(r["content"], 300)})
    pd.DataFrame(quote_rows).to_csv(DASH / "representative_quotes.csv", index=False)

    # --- dashboard: negative reviews table ---------------------------------
    cols = ["at", "week", "score", "thumbsUpCount", "primary_category", "country", "content"]
    df[df["sentiment"] == "Negative"][cols].to_csv(DASH / "reviews_negative.csv", index=False)

    # --- figures -----------------------------------------------------------
    plt.figure(figsize=(7, 4))
    df["score"].value_counts().sort_index().plot(kind="bar", color="#6c5ce7")
    plt.title("Canva Play Store reviews — star distribution")
    plt.xlabel("Star rating"); plt.ylabel("Reviews"); plt.tight_layout()
    plt.savefig(FIG / "fig1_star_distribution.png", dpi=130); plt.close()

    plt.figure(figsize=(8, 4.5))
    p = summary[summary["category"] != "Praise"].head(8).iloc[::-1]
    plt.barh(p["category"], p["negative_mentions"], color="#d63031")
    plt.title("Top pain points — negative-review volume by product area")
    plt.xlabel("Negative reviews (1–2★)"); plt.tight_layout()
    plt.savefig(FIG / "fig2_top_pain_points.png", dpi=130); plt.close()

    plt.figure(figsize=(8.5, 4.5))
    for c in pain["category"].head(3):
        s = pivot[c] if c in pivot.columns else None
        if s is not None:
            plt.plot(s.index, s.values, marker="o", label=c)
    plt.title("Weekly trend — top 3 pain points (negative volume)")
    plt.ylabel("Negative reviews / week"); plt.legend(fontsize=8)
    plt.xticks(rotation=30, ha="right"); plt.tight_layout()
    plt.savefig(FIG / "fig3_weekly_trend.png", dpi=130); plt.close()

    print("\nSaved 3 figures → reports/figures/ and 4 CSVs → dashboard/")


if __name__ == "__main__":
    main()
