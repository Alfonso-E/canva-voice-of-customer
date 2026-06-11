# Insight Brief — Canva Mobile Feedback

**Prepared by:** Alfonso Enriquez · independent portfolio analysis
**Window:** 21 Apr – 9 Jun 2026 · **Source:** 12,000 public Google Play reviews
**Method:** multi-label taxonomy + NMF theme discovery; sentiment from star rating

---

## Executive summary

Sentiment is healthy overall — **avg 4.37★, 84% positive, 5% neutral** — so this brief focuses on
the **11% of reviews that are negative (1–2★)**, where the actionable signal lives.

Negative feedback is **highly concentrated**: just three product areas —
**Crashes & Performance, Billing & Subscription, and Export & Quality** — account for the
large majority of negative volume *and* the loudest reviews (by user up-votes). Two of
these are reliability/trust issues that disproportionately hit **paying** users, which
makes them higher-stakes than their raw volume suggests.

**If the team fixes one thing this cycle:** app stability for paid users.
**The early-warning flag:** Export & Quality complaints are rising (~+55% w/w).

---

## Top pain points

| Product area | Neg. reviews | % of mentions negative | Avg ★ | Up-votes (reach) | Trend (w/w) |
|---|---:|---:|---:|---:|:--:|
| Crashes & Performance | 176 | 57% | 2.35 | 269 | → (+10%) |
| Billing & Subscription | 157 | 60% | 2.38 | **298** | ▼ (−12%) |
| Export & Quality | 95 | 51% | 2.61 | 103 | ▲ **(+55%)** |
| Editor & Usability | 58 | 33% | 3.40 | 90 | ▼ |
| Templates / Fonts / Content | 62 | 18% | 4.01 | 83 | ▼ |

*Reviews are multi-label (one review can touch several areas); "% negative" shows how
sour a topic is whenever it comes up. Billing and Crashes are both ~60% negative — when
users mention them, they are usually upset.*

---

## Deep dives

### 1. Crashes & Performance — *fix first*
Highest negative volume (176) and high reach (269 up-votes). The most-upvoted negative
review in the entire dataset is a **paying** user driven to cancel by instability:

> *"…unsubbed and deleted. App is horrible. I have tried EVERYTHING Canva says to do, app
> still freezes and locks up for a paid user. I refuse to pay for a sub-par app…"* — 1★, 92 up-votes

Theme discovery on negatives echoes this: *slow, downloading, lag, loading, freezes, offline.*
**Recommended action:** a stability/performance sprint prioritised by paid-user crash
telemetry; reliability for subscribers is both a churn and a reputation risk.

### 2. Billing & Subscription — *trust problem*
Most up-voted pain area overall (298). Three recurring patterns: **free-trial auto-charge
surprise**, **double-charging across accounts**, and **hard cancellation/refund**:

> *"…careful putting credit cards on file… I created a second account under a different
> email, checked my card statement only to find they were charging me on both…"* — 1★, 8 up-votes

> *"…I did the Canva Pro free trial and when it ended it said it cancelled itself, and when
> I checked…"* — 2★, 8 up-votes

**Recommended action:** pre-charge trial reminders, clearer cancel/refund flows, and a bug
review of multi-account billing. These are mostly *transparency* fixes, not pricing changes.

### 3. Export & Quality — *rising; watch closely*
Lower volume (95) but **trending up ~55% week-over-week** — the clearest emerging issue.
Complaints cluster around slow/failed downloads and saved output not matching the editor:

> *"…takes too long to download a single file… there seems to be a bug on copying and
> pasting and when editing text…"* — 1★, 8 up-votes

> *"…when you save a video with text… the text disappears…"* — 1★, 7 up-votes

**Recommended action:** treat as a possible recent regression — pull the export/render
path changes from the last ~3 weeks and validate text-on-video and download reliability.

---

## Recommendation summary (prioritised)

1. **Paid-user app stability** (Crashes) — highest impact on churn + reputation.
2. **Billing transparency** (trial reminders, cancel/refund clarity, multi-account charge bug) — quick trust wins.
3. **Investigate the Export & Quality regression** (rising) — contain before it grows.
4. Monitor Editor & Usability ("needs a diploma to use it") for onboarding opportunities.

## Limitations
Play Store ≈ individual/mobile/free-tier users, **not** enterprise/business users;
single channel; ~7-week point-in-time window; keyword taxonomy misses some paraphrasing
(partly offset by the NMF theme layer). See repo README for the full note.

## Appendix — auto-discovered negative themes (NMF)
`bad/expensive/install` · `slow/downloading/lag/loading` · `worst/subscription/cancelled/pro`
· `video editing/waste time/useless` · `subscription/money/refund/trial` · `working/offline/internet`
(full list in `reports/discovered_themes.txt`)
