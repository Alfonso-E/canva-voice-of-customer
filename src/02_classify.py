"""
02_classify.py

Tag each review using two methods:
  1. A keyword TAXONOMY (regex, multi-label) — tags reviews into product areas
     (Billing, Crashes, Paywall, Login, ...). Easy to read and extend.
  2. THEME DISCOVERY (TF-IDF + NMF) over the negative reviews — surfaces topics
     the fixed taxonomy might miss.

Sentiment is derived from the star rating (1-2 = Negative, 3 = Neutral,
4-5 = Positive), so no separate sentiment model is needed.

Input : data/raw/canva_play_reviews.csv
Output: data/processed/reviews_tagged.csv
        reports/discovered_themes.txt
"""
from __future__ import annotations
import sys
from pathlib import Path

import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "canva_play_reviews.csv"
OUT = ROOT / "data" / "processed" / "reviews_tagged.csv"
THEMES = ROOT / "reports" / "discovered_themes.txt"

# --- The taxonomy: product area -> regex of trigger phrases (word-boundaried) -
TAXONOMY: dict[str, str] = {
    "Billing & Subscription": r"\b(charg\w*|refund\w*|subscrib\w*|subscription|payment|paid|money|expensive|cancel\w*|trial|billed|auto.?renew|fee)\b",
    "Pro / Paywall / Watermark": r"(paywall|watermark|\blocked?\b|premium|\bpro\b|upgrade|behind a pay|have to pay|need to pay)",
    "Crashes & Performance": r"(crash\w*|\blag\w*|slow|freez\w*|frozen|\bbug\w*|glitch\w*|stuck|won.?t load|not loading|keeps? loading|force clos\w*|hang\w*|not working|stops? working)",
    "Login & Account": r"(log ?in|sign ?in|signed out|\baccount\b|password|verif\w*|locked out|can.?t access|two.?factor)",
    "Export & Quality": r"(export\w*|download\w*|\bsave\b|resolution|blurr\w*|pixelat\w*|low quality|image quality|\bhd\b)",
    "Editor & Usability": r"(hard to use|confus\w*|too complicated|complicated|interface|\bui\b|user.?friendly|can.?t find|difficult|clunky|not intuitive|hard to navigate)",
    "Templates / Fonts / Content": r"(template\w*|\bfont\w*|stock photo|\bphotos?\b|\bimages?\b|design options|more options|\belements?\b)",
    "Ads": r"(\bads?\b|advertisement\w*|pop.?ups?)",
    "AI Features": r"(\bai\b|magic (write|design|edit|eraser|media)|text to image|background remover|generat\w*)",
    "Feature Requests": r"(please add|wish (it|they|you)|would be (nice|great)|should add|need an? option|add an? option|hope (they|you) add|suggestion|feature request)",
    "Customer Support": r"(customer (service|support)|no response|no help|help ?desk|contact (them|support)|reach (out|them)|unresponsive)",
    "Praise": r"(love it|i love|\blove\b|\bgreat\b|awesome|amazing|best app|so helpful|helpful|easy to use|excellent|perfect|thank you|highly recommend|\bgood\b|\bnice\b|useful|handy)",
}

# Priority for choosing a single primary_category (problems before praise).
PRIORITY = [
    "Billing & Subscription", "Pro / Paywall / Watermark", "Crashes & Performance",
    "Login & Account", "Export & Quality", "Customer Support", "Editor & Usability",
    "Ads", "Templates / Fonts / Content", "AI Features", "Feature Requests", "Praise",
]


def sentiment(score: int) -> str:
    return "Negative" if score <= 2 else "Neutral" if score == 3 else "Positive"


def main() -> None:
    df = pd.read_csv(RAW)
    df["content"] = df["content"].fillna("").astype(str)
    df = df[df["content"].str.strip().str.len() > 0].copy()
    df["at"] = pd.to_datetime(df["at"], errors="coerce")
    df = df.dropna(subset=["at"])
    df["week"] = df["at"].dt.to_period("W").dt.start_time
    df["sentiment"] = df["score"].astype(int).map(sentiment)

    low = df["content"].str.lower()
    for cat, pattern in TAXONOMY.items():
        # non-capturing groups keep pandas from warning about match groups
        df[cat] = low.str.contains(pattern.replace("(", "(?:"), regex=True, na=False)

    cat_cols = list(TAXONOMY)
    df["n_categories"] = df[cat_cols].sum(axis=1)

    def primary(row) -> str:
        for c in PRIORITY:
            if row[c]:
                return c
        return "Other / Uncategorised"
    df["primary_category"] = df[cat_cols].apply(primary, axis=1)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8")
    tagged = (df["n_categories"] > 0).mean()
    print(f"Tagged {len(df):,} reviews | {tagged:.0%} matched >=1 taxonomy category")

    # --- Unsupervised theme discovery on negative reviews -------------------
    neg = df.loc[df["sentiment"] == "Negative", "content"]
    extra_stop = {"app", "apps", "canva", "good", "nice", "really", "just",
                  "use", "using", "used", "don", "aap", "hai", "ok", "okay", "ll", "ve"}
    stop = list(ENGLISH_STOP_WORDS | extra_stop)
    vec = TfidfVectorizer(stop_words=stop, ngram_range=(1, 2),
                          min_df=5, max_df=0.4, max_features=3000)
    X = vec.fit_transform(neg)
    nmf = NMF(n_components=8, init="nndsvda", random_state=42, max_iter=400)
    nmf.fit(X)
    terms = vec.get_feature_names_out()
    lines = ["Discovered themes in NEGATIVE reviews (NMF over TF-IDF):", ""]
    for i, comp in enumerate(nmf.components_, 1):
        top = [terms[j] for j in comp.argsort()[-10:][::-1]]
        lines.append(f"Theme {i}: " + ", ".join(top))
    THEMES.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
