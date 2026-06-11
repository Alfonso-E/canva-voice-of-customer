# Dashboard — Looker Studio (or Power BI)

These CSVs are the analysis outputs, shaped to drop straight into a BI tool.
The intended dashboard is one page that lets a product team answer:
*"What are users most unhappy about, how loud is it, and what's getting worse?"*

## Files
| File | Grain | Use for |
|---|---|---|
| `category_summary.csv` | one row per product area | bar chart of negative volume; KPI scorecards (% negative, avg ★) |
| `weekly_trend.csv` | area × week | line chart of negative volume over time (the "rising issue" view) |
| `representative_quotes.csv` | top quotes per area | a "voice of the user" panel |
| `reviews_negative.csv` | one row per negative review | filterable detail table (drill-down by area / week) |
| `overview.csv` | one row of top-line totals | KPI scorecards — total reviews, avg rating, % negative |

## Build it in Looker Studio (free, ~5 min)
1. Go to **lookerstudio.google.com → Create → Data source → File upload** and upload
   `category_summary.csv` (repeat for the others, or use *Blend* later).
2. **Create → Report** and add:
   - a **bar chart**: dimension `category`, metric `negative_mentions` (sort desc) → *Top pain points*
   - **scorecards**: `negative_mentions` total, average `avg_rating`, average `pct_negative`
   - a **time-series** from `weekly_trend.csv`: dimension `week`, breakdown `category`, metric `negative_mentions`
   - a **table** from `reviews_negative.csv`: `at`, `score`, `primary_category`, `content`, with a date + category filter control
3. **Share → Anyone with the link can view**, then paste that link below and in the main README.

> **▶️ Live dashboard:** https://lookerstudio.google.com/reporting/4a1a3ddc-4b06-4b32-9118-b61768640a6d

Tip: a couple of screenshots saved into `reports/figures/` and embedded in the main
README make the repo instantly skimmable for a recruiter.
