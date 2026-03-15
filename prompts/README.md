# UnyKorn Prompt Constitution

> All systems must obey one constitution, pass one governor, and be built through one shared shell.

> If the system cannot be understood, trusted, shared, and converted in a few steps, it is not ready to sell.

---

## What This Is

This is a **7-layer command stack** that governs how every UnyKorn system is designed, evaluated, built, branded, sold, and maintained. It is not one giant prompt — it is a layered architecture where each layer has a specific role and authority.

These prompts are designed to be pasted directly into any AI coding assistant (VS Code Copilot, Cursor, or repo-level rules) or used as human decision frameworks.

---

## The 7 Layers

| # | Document | Role | Authority | Required |
|---|----------|------|-----------|----------|
| **01** | [Constitution](01_CONSTITUTION.md) | Defines the world | Highest law — overrides everything | Always |
| **02** | [Governor](02_GOVERNOR.md) | Guards the gates | Stops what shouldn't be built | Always |
| **03** | [Builder](03_BUILDER.md) | Creates the system | Defines how things are built | Always |
| **04** | [Brand Skin](04_BRAND_SKIN.md) | Changes the clothes | Defines what changes per brand | When deploying for a specific brand |
| **05** | [Feature Review](05_FEATURE_REVIEW.md) | Prevents drift | Audits what's been built | After building, quarterly, or when drift is detected |
| **06** | [Commerce & Distribution](06_COMMERCE_DISTRIBUTION.md) | Makes it sellable | Ensures every surface can sell, share, and convert | Always |
| **07** | [Standards Governor](07_STANDARDS_GOVERNOR.md) | Protects the brand | Helios-specific compliance, tone, and launch standards | When building Helios surfaces |

---

## How To Use

### For AI Assistants

Load the prompts in order. Each layer narrows the scope of what the AI can do:

1. **Always load 01 + 02 + 03 + 06** — these are the foundation
2. **Add 04** when working on a specific brand's deployment
3. **Add 05** when reviewing, auditing, or evaluating existing features
4. **Add 07** when building any Helios-facing surface, page, or flow

```
System prompt = 01_CONSTITUTION + 02_GOVERNOR + 03_BUILDER + 06_COMMERCE_DISTRIBUTION
Brand work    = System prompt + 04_BRAND_SKIN
Reviews       = System prompt + 05_FEATURE_REVIEW
Helios work   = System prompt + 04_BRAND_SKIN + 07_STANDARDS_GOVERNOR
```

### For Human Teams

Use the prompts as decision frameworks:

- **Planning:** Run every idea through the Governor (02) before adding to roadmap
- **Building:** Follow the Builder (03) patterns and checklist
- **Branding:** Reference the Brand Skin (04) for tone, naming, and visual decisions
- **Selling:** Apply Commerce & Distribution (06) to ensure every flow can convert and spread
- **Auditing:** Run the Feature Review (05) quarterly or when the product feels heavy

### For Repository Rules

Add to `.github/copilot-instructions.md`, `.cursorrules`, or equivalent:

```markdown
# System Rules
This repository follows the UnyKorn Prompt Constitution.
See /prompts/ for the full 6-layer command stack.
Always load 01, 02, 03, and 06 before making changes.
```

---

## Decision Flow

```
IDEA
  ↓
01 CONSTITUTION — Does it align with UnyKorn's identity and values?
  ↓ yes
02 GOVERNOR — Does it pass all 8 gates?
  ↓ yes (verdict: BUILD)
03 BUILDER — Build it following the liquid glass system
  ↓ built
06 COMMERCE — Does it have a sell/share/convert path?
  ↓ yes
04 BRAND SKIN — Apply the brand's 6 layers (if deploying)
  ↓ skinned
05 FEATURE REVIEW — Score it. Ship, iterate, bench, or remove.
  ↓ verdict
07 STANDARDS GOVERNOR — Does it meet Helios brand and launch standards? (if Helios)
  ↓ yes
SHIP or CORRECT
```

---

## Authority Hierarchy

If two prompts conflict, the higher-numbered layer yields to the lower:

```
01 Constitution  >  02 Governor  >  03 Builder  >  06 Commerce  >  07 Standards Governor  >  04 Brand Skin  >  05 Feature Review
```

The Constitution is absolute. The Governor enforces the Constitution. The Builder executes what the Governor approves. Commerce ensures it can sell and spread. The Standards Governor ensures Helios surfaces meet brand and launch standards. The Brand Skin customizes the result. The Feature Review audits everything.

No layer can override a layer above it. No exception.

> **Layer 07 (Standards Governor) operates alongside 06 (Commerce) — it does not override Commerce rules, but adds Helios-specific brand, compliance, and language standards on top.**

---

## File Manifest

```
prompts/
├── README.md                      ← You are here
├── 01_CONSTITUTION.md             ← The highest law
├── 02_GOVERNOR.md                 ← The filter (8 gates)
├── 03_BUILDER.md                  ← The architect (liquid glass, modules, code patterns)
├── 04_BRAND_SKIN.md               ← Per-brand overrides (6 brands × 6 layers)
├── 05_FEATURE_REVIEW.md           ← Drift prevention (6 questions, scorecard, quarterly audit)
├── 06_COMMERCE_DISTRIBUTION.md    ← Commerce, distribution, conversion, sharing
└── 07_STANDARDS_GOVERNOR.md       ← Helios brand, compliance, and launch standards
```

---

## Version

**Prompt Constitution v1.2**  
Created for the UnyKorn ecosystem — Helios, FTH, UnyKorn, xxxiii, NIL33, Y3K.

---

*One constitution. One governor. One standards layer. One shared shell. Six brands. Zero drift. Ready to sell.*
