"""
01_scrape_reviews.py

Scrape public Canva reviews from the Google Play Store into
data/raw/canva_play_reviews.csv. Loops the paginated reviews() endpoint
(newest first) until the target count is reached.

Only public fields are stored (review id, rating, date, up-votes, text);
usernames are not kept.
"""
from __future__ import annotations
import time
from pathlib import Path

import pandas as pd
from google_play_scraper import Sort, reviews

APP_ID = "com.canva.editor"          # Canva: Visual Suite (Google Play)
COUNTRIES = ["us"]                    # English review stream; expandable
TARGET_PER_COUNTRY = 12000            # newest reviews to collect per country
BATCH = 200                           # Play Store max per request

OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "canva_play_reviews.csv"


def scrape_country(country: str, target: int) -> list[dict]:
    collected: list[dict] = []
    token = None
    while len(collected) < target:
        batch, token = reviews(
            APP_ID,
            lang="en",
            country=country,
            sort=Sort.NEWEST,
            count=min(BATCH, target - len(collected)),
            continuation_token=token,
        )
        if not batch:
            break
        for r in batch:
            r["country"] = country
        collected.extend(batch)
        if token is None:
            break
        time.sleep(0.4)  # be polite to the endpoint
    return collected


def main() -> None:
    rows: list[dict] = []
    for c in COUNTRIES:
        got = scrape_country(c, TARGET_PER_COUNTRY)
        print(f"  {c}: {len(got)} reviews")
        rows.extend(got)

    df = pd.DataFrame(rows)
    keep = ["reviewId", "country", "at", "score", "thumbsUpCount",
            "reviewCreatedVersion", "content", "replyContent", "repliedAt"]
    df = df[[c for c in keep if c in df.columns]]
    df = df.drop_duplicates(subset="reviewId")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8")

    print(f"\nSaved {len(df):,} unique reviews -> {OUT}")
    print(f"Date range : {df['at'].min()}  ->  {df['at'].max()}")
    print("Star distribution:")
    print(df["score"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
