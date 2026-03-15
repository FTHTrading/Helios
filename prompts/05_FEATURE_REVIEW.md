# FEATURE REVIEW

> The Feature Review prevents drift. It runs after something is built to verify it still belongs.

This prompt is the quality gate between "built" and "shipped." It catches features that passed the Governor but drifted during implementation, features that accumulated scope, and features that no longer fit the product's direction. It is also the recurring audit tool for existing features.

---

## When To Use This Prompt

- After a feature is built and before it ships
- During quarterly audits of existing features
- When the product feels bloated, slow, or unfocused
- When a user reports confusion or a support ticket reveals complexity
- When someone says "we should probably revisit this"
- When preparing for a major release or launch

---

## The 6 Feature Review Questions

Every feature — new or existing — must answer all 6 questions. These are not suggestions. They are requirements.

### Question 1 — What simple problem does this solve?

Write the answer in one sentence with no commas.

**Good:** "Shows the user their current treasury balance."  
**Bad:** "Provides a comprehensive view of the user's financial position, including staked assets, pending rewards, and transaction history."

If the answer requires a comma, the feature solves more than one problem. Split it into multiple features and review each one separately.

**If no simple problem:** The feature is a candidate for removal.

---

### Question 2 — Does it fit the one main offer?

Every brand has one main offer:

| Brand | One Main Offer |
|-------|---------------|
| **Helios** | Infrastructure network for energy, treasury, and trust |
| **FTH** | Trading intelligence and financial operations |
| **UnyKorn** | Sovereign technology ecosystem |
| **xxxiii** | Creative intelligence and provenance |
| **NIL33** | Athlete identity and NIL protection |
| **Y3K** | Climate-action token infrastructure |

Does this feature directly serve the brand's one main offer? Not "eventually" or "tangentially" — directly.

**Test:** Remove this feature from the product description. Does the one main offer still make sense? If yes, the feature might be supplementary — which is fine, but it should never get priority over features that directly serve the core offer.

**If it doesn't fit:** BENCH or REMOVE.

---

### Question 3 — Does it improve revenue, trust, or scale?

Pick exactly one:

| Impact | Evidence Required |
|--------|------------------|
| **Revenue** | Show the dollar amount or conversion rate this feature affects. No handwaving. |
| **Trust** | Show the verification mechanism this feature provides. If no cryptographic or auditable proof, it's not trust — it's branding. |
| **Scale** | Show the viral coefficient or network effect. If removing this feature doesn't reduce growth, it doesn't scale. |

**If none:** The feature is a candidate for removal. "It improves user experience" is not sufficient unless tied to one of the three above.

---

### Question 4 — Is it a top-2 best practice?

The same gate from the Governor, but now applied to the implementation, not just the plan.

1. How do the top 3 products in this space implement this feature?
2. Is our implementation one of the top 2 most proven approaches?
3. If we built something custom, can we now replace it with a proven approach?

Features that started as MVPs or experiments often use ad-hoc implementations. During review, these should be upgraded to best-practice implementations or removed.

**If not top-2:** Rebuild using a top-2 approach, or remove.

---

### Question 5 — Should it be built now?

Timing matters. A good feature at the wrong time is a bad feature.

| Timing Signal | Action |
|--------------|--------|
| Users are asking for this | BUILD NOW |
| Revenue depends on this within 30 days | BUILD NOW |
| Competitors have this and we're losing users because of it | BUILD NOW |
| "Nice to have" for future growth | BENCH — revisit in 90 days |
| Internal team wants this but users haven't asked | BENCH — validate with users first |
| Technology enables this but no user demand exists | BENCH — wait for demand |

**If not now:** Move to backlog with a specific revisit date and condition for revival.

---

### Question 6 — What gets benched?

Every feature added should trigger a review of what to remove. Product capacity is finite. It's not about what we can build — it's about what we should keep.

For every feature added, identify:
- **One feature to bench** (move to backlog, disable, or reduce prominence)
- **One feature to simplify** (reduce scope, merge with another, or automate)

If nothing can be benched or simplified, the product may be at capacity. Adding more without removing increases complexity, maintenance burden, and user confusion.

---

## Feature Review Scorecard

Score each feature 0-2 on each question:

| Score | Meaning |
|-------|---------|
| **2** | Clear, strong, unambiguous pass |
| **1** | Passes with caveats or conditions |
| **0** | Fails — action required |

| Question | Score | Notes |
|----------|-------|-------|
| 1. Simple problem | /2 | |
| 2. Fits main offer | /2 | |
| 3. Revenue/trust/scale | /2 | |
| 4. Top-2 best practice | /2 | |
| 5. Right timing | /2 | |
| 6. What gets benched | /2 | |
| **TOTAL** | **/12** | |

### Verdict By Score

| Score | Verdict | Action |
|-------|---------|--------|
| **10-12** | **SHIP** | Proceeds to production |
| **7-9** | **ITERATE** | Address weak areas, re-review |
| **4-6** | **BENCH** | Move to backlog with conditions |
| **0-3** | **REMOVE** | Delete or disable |

---

## Feature Review Template

```
FEATURE: [name]
BRAND: [which brand]
STATUS: [new / existing / modified]
REVIEWER: [name or AI]
DATE: [YYYY-MM-DD]

Q1 — SIMPLE PROBLEM:
[one sentence, no commas]
SCORE: [0/1/2]

Q2 — FITS MAIN OFFER:
[which main offer] → [directly / supplementary / tangential]
SCORE: [0/1/2]

Q3 — IMPACT:
[revenue / trust / scale] → [evidence]
SCORE: [0/1/2]

Q4 — BEST PRACTICE:
[top-2 approach used?] → [which one?]
[if custom: can it be replaced?]
SCORE: [0/1/2]

Q5 — TIMING:
[build now / bench] → [reason]
SCORE: [0/1/2]

Q6 — BENCH TRADE:
[feature to bench:] →
[feature to simplify:] →
SCORE: [0/1/2]

TOTAL: [/12]
VERDICT: [SHIP / ITERATE / BENCH / REMOVE]
NOTES: [any additional context]
```

---

## Quarterly Full-Product Review

Every 90 days, run the Feature Review against the entire product:

1. **List every feature** visible to users (every page, button, flow, surface)
2. **Score each feature** using the scorecard
3. **Sort by score** ascending (weakest first)
4. **Action the bottom 20%:** Remove, bench, or merge
5. **Identify the top 3:** These get investment for improvement
6. **Document results** in a Feature Review Report

### Feature Review Report Template

```
QUARTERLY FEATURE REVIEW
Brand: [brand]
Period: [Q# YYYY]
Total Features Reviewed: [N]
Features Shipped: [N] (score 10+)
Features Iterated: [N] (score 7-9)
Features Benched: [N] (score 4-6)
Features Removed: [N] (score 0-3)

TOP 3 FEATURES (invest):
1. [name] — score [/12] — [why it's strong]
2. [name] — score [/12] — [why it's strong]
3. [name] — score [/12] — [why it's strong]

BOTTOM 3 FEATURES (action required):
1. [name] — score [/12] — ACTION: [remove/bench/merge]
2. [name] — score [/12] — ACTION: [remove/bench/merge]
3. [name] — score [/12] — ACTION: [remove/bench/merge]

NET CHANGE: [+N added / -N removed / N simplified]
COMPLEXITY TREND: [increasing / stable / decreasing]
```

---

## Drift Detection Patterns

These are common signs that a product is drifting. If 3 or more are true, trigger a full Feature Review immediately:

1. **Navigation overflow.** More than 7 top-level navigation items.
2. **Settings sprawl.** More than 15 user-configurable settings.
3. **Onboarding creep.** Onboarding takes more than 3 screens or 2 minutes.
4. **Support signal.** Most support tickets are "how do I..." rather than bugs.
5. **Feature invisibility.** Analytics show <5% of users use a feature that's prominently placed.
6. **Explanation debt.** A feature requires a help article, tooltip, or walkthrough to understand.
7. **Build time inflation.** New features take 2x longer because they must account for existing complexity.
8. **Brand confusion.** Users confuse one brand's features with another's.

---

*Feature Review v1 — What gets shipped must stay worthy. What drifts gets corrected.*
