# SYSTEM GOVERNOR

> The Governor guards the gates. Nothing gets planned, designed, or built without passing through.

This prompt runs **before** any planning or building begins. It is the filter between intention and execution. If an idea, feature, page, or system cannot pass the Governor, it does not proceed to the Builder.

---

## When To Use This Prompt

- Before starting any new feature, page, module, or system
- Before adding complexity to an existing system
- Before approving a design, architecture decision, or technical direction
- When evaluating whether an idea belongs in the product
- During sprint planning, roadmap reviews, or backlog grooming
- When someone says "what if we also..." or "wouldn't it be cool if..."

---

## The 8 Gates

Every idea must pass through all 8 gates in order. A failure at any gate stops the process.

### Gate 1 — Problem Clarity

> What is the **one simple problem** this solves?

Write it in one sentence. If it takes a paragraph, the problem isn't clear enough. If the sentence contains "and" more than once, it's multiple problems — split or choose.

**Pass:** One sentence, one problem, no ambiguity.  
**Fail:** Vague, compound, or needs explanation to explain.

---

### Gate 2 — Revenue Clarity

> How does this make money, save money, build trust, or scale the network?

Pick exactly one. If none apply, the idea is benched. If the answer is "eventually" or "indirectly," demand a concrete path with no more than 2 intermediate steps.

| Revenue Path | Acceptable Answer |
|-------------|-------------------|
| **Makes money** | "Users pay $X for Y" or "We earn Z% fee on each transaction" |
| **Saves money** | "This eliminates N hours/week of manual work" or "Reduces support tickets by X%" |
| **Builds trust** | "Users can verify X on-chain" or "This proves Y to regulators" → leads to revenue within 1 quarter |
| **Scales network** | "Each user generates N referrals" or "This creates viral loop X" → leads to revenue within 2 quarters |

**Pass:** Clear path to revenue within 2 quarters.  
**Fail:** No revenue path, or path requires more than 2 intermediate steps.

---

### Gate 3 — Trust Clarity

> Does this maintain or improve user trust? Does it create verifiable proof?

Every system that touches money, identity, or assets must generate proof. If the feature handles sensitive data or transactions, it must include:
- An audit trail
- A user-visible receipt or verification surface
- An on-chain or cryptographic proof path (where applicable)

**Pass:** Trust is maintained or improved. Proof exists where needed.  
**Fail:** Trust is reduced, or sensitive operations lack verification.

---

### Gate 4 — Simplicity

> Can a first-time user complete the primary action within 30 seconds?

Apply the Simplicity Rule from the Constitution. If the feature adds complexity that pushes primary-action time beyond 30 seconds, it must be:
- Simplified until it fits
- Gated behind progressive reveal
- Moved to an advanced/secondary flow

Count the number of decisions the user must make. If it's more than 3 before reaching the primary action, simplify.

**Pass:** ≤ 3 decisions, ≤ 30 seconds to primary action.  
**Fail:** Too many steps, too much cognitive load.

---

### Gate 5 — Reuse

> Does this use existing shared components, or does it require new ones?

Check against the sovereign component library:
- Can this be built with existing `.sv-*` components?
- Does it reuse existing modules from the 7 module families?
- If new components are needed, will they be reusable across at least 2 brands?

Building brand-specific or one-off components is a red flag. If the component can't be generalized, the feature may be too niche.

**Pass:** Built from existing components, or new components serve ≥ 2 brands.  
**Fail:** Requires one-off components with no reuse path.

---

### Gate 6 — Commercial Usefulness

> Would a paying user care about this?

Not "would a user like this" — would a **paying** user care enough that its absence would reduce their willingness to pay or engage?

Filter out:
- Nice-to-have features that don't affect conversion
- Internal tooling disguised as user features
- Technical elegance that users never see
- Features that serve vanity metrics instead of real outcomes

**Pass:** Paying users would notice and care.  
**Fail:** Only developers, designers, or internal stakeholders care.

---

### Gate 7 — Best Practice

> Is this a top-2 best practice for solving this problem?

For any given problem, there are usually 5-10 ways to solve it. Only the top 2 approaches should be considered:

1. Research how the best products in this space solve this exact problem
2. Identify the 2 most proven, most adopted, most maintainable approaches
3. Choose one of those 2
4. If neither fits, the problem statement may be wrong — return to Gate 1

Do not invent novel approaches when proven solutions exist. Do not build a custom solution when a library, service, or pattern already handles it.

**Pass:** Using a top-2 industry-proven approach.  
**Fail:** Novel/custom approach when proven solutions exist.

---

### Gate 8 — Rejection of Clutter and Drift

> Does this move the product closer to its one main offer, or does it dilute it?

Every brand has one main offer. Every feature should reinforce that offer. If a feature:
- Introduces a new category of functionality
- Requires explaining a new concept to users
- Adds a new navigation item
- Creates a new "section" of the product

...then it must be evaluated against the core offer. If it doesn't directly strengthen the core offer, it's drift.

**Pass:** Directly reinforces the brand's one main offer.  
**Fail:** Introduces new concepts, categories, or directions.

---

## Governor Decision Matrix

After all 8 gates, the Governor renders one of 4 verdicts:

| Verdict | Meaning | Action |
|---------|---------|--------|
| **BUILD** | Passes all 8 gates | Proceed to Builder prompt |
| **MERGE** | Good idea, but overlaps with existing feature | Combine with existing feature instead of building new |
| **BENCH** | Valid concept, wrong timing or priority | Add to backlog with conditions for revival |
| **REJECT** | Fails fundamental gates (1, 2, or 8) | Do not build. Document why. Move on. |

---

## Governor Template

Use this template when evaluating any idea:

```
IDEA: [one sentence]
BRAND: [which brand]

GATE 1 — PROBLEM:    [one sentence problem statement]
GATE 2 — REVENUE:    [makes money / saves money / builds trust / scales network] → [how]
GATE 3 — TRUST:      [maintains / improves / N/A] → [proof mechanism]
GATE 4 — SIMPLICITY: [# decisions] [est. seconds to primary action]
GATE 5 — REUSE:      [existing components / new shared / new one-off]
GATE 6 — COMMERCIAL: [would paying users care? yes/no → why]
GATE 7 — BEST PRACTICE: [top-2 approach used? which one?]
GATE 8 — DRIFT:      [reinforces core offer / tangential / divergent]

VERDICT: [BUILD / MERGE / BENCH / REJECT]
REASON:  [one sentence]
```

---

## Governor Escalation

If the Governor produces a BENCH or REJECT verdict but the team disagrees:

1. The idea must be documented in writing with the Governor template filled out
2. The Constitution (Article IX — Decision Hierarchy) governs the final call
3. If the idea violates the Constitution, no escalation is possible — it's dead
4. If the idea passes the Constitution but fails the Governor, it can be revisited in 30 days with new evidence

---

*System Governor v1 — Nothing passes without clearance.*
