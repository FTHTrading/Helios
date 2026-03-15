# SOVEREIGN DESIGN SYSTEM — Master Spec v1

**Version:** 1.0.0  
**Status:** Active  
**Scope:** All brands, all surfaces, all devices  
**Brands:** FTH · UnyKorn · xxxiii · Helios · NIL33 · Y3K  

---

## 1. Design Philosophy

One sovereign product language. Not six websites — one interface operating system that stretches across web, mobile, dashboard, watch, glasses, XR/VR, and AI agent console.

Every surface — whether it serves capital flows, proof systems, athletic performance, creative tools, or settlement infrastructure — speaks the same visual-operational language: clarity, motion, proof, and action.

---

## 2. Design DNA — 10 Laws

| # | Law | Meaning |
|---|-----|---------|
| 1 | **One focal object** | Every screen has exactly one primary visual anchor |
| 2 | **One active panel** | Only one interactive panel expanded at any time |
| 3 | **Progressive reveal** | Complexity unfolds on demand, never on arrival |
| 4 | **Motion is guidance** | Animation communicates state, not decoration |
| 5 | **Glass is selective** | Blur/transparency used only for overlays and nav — never cards |
| 6 | **Readability beats spectacle** | If it's hard to read, it's wrong — period |
| 7 | **Proof is visible** | Every transaction, certificate, or AI action shows its receipt |
| 8 | **AI is behavior** | Intelligence manifests as adaptive layout, not chatbot chrome |
| 9 | **Every screen must convert** | No dead-end pages — every view drives toward an action |
| 10 | **Every system should feel alive** | Subtle pulse, status indicators, live data — never frozen UI |

---

## 3. Product Framework — 5 Layers

Every page, every app, every surface follows this progression:

```
ATTRACT → ORIENT → ACT → MONITOR → EXPAND
```

| Layer | Purpose | Components |
|-------|---------|------------|
| **Attract** | Draw attention, build trust | Hero core, headline, social proof strip |
| **Orient** | Explain the system, show position | Module constellation, status indicators |
| **Act** | Enable the primary action | Command CTA, dock panel, form flows |
| **Monitor** | Show results, proof, status | Metric cards, proof strip, live status pill |
| **Expand** | Drive network growth | Signal cards, automation rail, referral flows |

---

## 4. Token Architecture

### 4.1 Theme Tokens

The base layer. Every brand overrides these and nothing else.

```css
/* ── Surfaces ── */
--sv-bg:              /* Page background */
--sv-bg-card:         /* Card / panel background */
--sv-bg-hover:        /* Interactive hover state */
--sv-bg-elevated:     /* Modal / dropdown / overlay */

/* ── Typography ── */
--sv-text:            /* Primary text */
--sv-text-muted:      /* Secondary / caption text */
--sv-text-inverse:    /* Text on accent backgrounds */

/* ── Brand Colors ── */
--sv-accent-1:        /* Primary brand accent */
--sv-accent-2:        /* Secondary brand accent */
--sv-accent-3:        /* Tertiary / supporting accent */

/* ── Semantic Colors ── */
--sv-success:         /* Positive state */
--sv-warning:         /* Caution state */
--sv-danger:          /* Error / destructive state */
--sv-info:            /* Informational state */

/* ── Effects ── */
--sv-glow:            /* Accent glow color for emphasis */
--sv-glass-fill:      /* Glass panel background */
--sv-glass-border:    /* Glass panel border */
--sv-glass-blur:      /* Backdrop blur radius */
--sv-border:          /* Standard border color */

/* ── Metal System ── */
--sv-metal:           /* Mid-tone metallic */
--sv-metal-light:     /* Light metallic */
--sv-metal-dark:      /* Dark metallic */
--sv-chrome:          /* Brightest metallic */
```

### 4.2 Motion Tokens

```css
--sv-speed-hover:     /* Hover transition (120ms) */
--sv-speed-panel:     /* Panel open/close (280ms) */
--sv-speed-fade:      /* Fade in/out (200ms) */
--sv-speed-dock:      /* Dock slide (320ms) */
--sv-ease-default:    /* cubic-bezier(.4, 0, .2, 1) */
--sv-ease-spring:     /* cubic-bezier(.34, 1.56, .64, 1) */
--sv-ease-decel:      /* cubic-bezier(0, 0, .2, 1) */
--sv-pulse-rhythm:    /* Breathing animation cycle (3s) */
--sv-orbit-drift:     /* Orbiting element cycle (15s) */
--sv-signal-sweep:    /* Signal sweep animation (8s) */
```

### 4.3 Layout Tokens

```css
--sv-max-width:       /* Content max-width (1200px) */
--sv-max-width-sm:    /* Narrow content (640px) */
--sv-max-width-lg:    /* Wide content (1440px) */
--sv-gap-xs:          /* 4px */
--sv-gap-sm:          /* 8px */
--sv-gap-md:          /* 16px */
--sv-gap-lg:          /* 24px */
--sv-gap-xl:          /* 40px */
--sv-gap-2xl:         /* 64px */
--sv-radius:          /* Panel radius (12px) */
--sv-radius-sm:       /* Small radius (8px) */
--sv-radius-pill:     /* Pill / button radius (980px) */
--sv-radius-round:    /* Circle (50%) */
--sv-nav-height:      /* Navigation bar height (64px) */
--sv-section-pad:     /* Section vertical padding (5rem) */
--sv-shadow:          /* Standard shadow */
--sv-shadow-lg:       /* Elevated shadow */
```

### 4.4 Typography Tokens

```css
--sv-font-ui:         /* 'Inter', -apple-system, sans-serif */
--sv-font-editorial:  /* 'EB Garamond', Georgia, serif */
--sv-font-mono:       /* 'SF Mono', 'Fira Code', monospace */
--sv-text-xs:         /* 0.75rem */
--sv-text-sm:         /* 0.85rem */
--sv-text-base:       /* 1rem */
--sv-text-lg:         /* 1.15rem */
--sv-text-xl:         /* 1.5rem */
--sv-text-2xl:        /* 2rem */
--sv-text-3xl:        /* 2.5rem */
--sv-text-hero:       /* 4rem */
--sv-leading-tight:   /* 1.2 */
--sv-leading-normal:  /* 1.7 */
--sv-tracking-tight:  /* -0.02em */
--sv-tracking-normal: /* -0.01em */
--sv-tracking-wide:   /* 0.08em */
--sv-tracking-caps:   /* 0.12em */
```

---

## 5. Component Families

### 5.1 Hero Core
The singular attention anchor at the top of any page.  
- One focal object (coin, logo mark, data visualization)  
- Radial gradient background (brand-tinted)  
- Hero title in metallic gradient text  
- Tagline in muted text  
- Action strip (1-2 CTAs max)  

### 5.2 Bubble Nav
Fixed top navigation with glass backdrop.  
- Logo left, links center/right  
- Glass background (blur + semi-transparent)  
- Active state: accent underline  
- Mobile: hamburger collapse to vertical stack  
- Density: compact on scroll (reduces height)  

### 5.3 Dock Panel
The primary interactive panel on any page.  
- Slides in from right (desktop) or bottom (mobile)  
- Glass border, solid card background  
- Only one open at a time (Law #2)  
- Contains form inputs, controls, or detail views  

### 5.4 Proof Strip
A horizontal evidence bar showing verifiable data.  
- 3-5 cells in a row  
- Each cell: icon + value + label  
- Links to verification endpoints  
- Always positioned after the primary action  

### 5.5 Signal Cards
Content cards that drive expansion.  
- Glass border, solid background  
- Icon + title + description  
- Hover: border glow (accent), subtle lift  
- Used for features, benefits, protocol steps  

### 5.6 Metric Cards
Data display cards for dashboards and monitoring.  
- Value in large bold type  
- Label in muted caps  
- Optional gauge ring or trend indicator  
- Status dot (green/yellow/red)  

### 5.7 Automation Rail
A horizontal or vertical strip showing automated processes.  
- Pipeline visualization  
- Status indicators per step  
- Connects to AI/automation systems  

### 5.8 Live Status Pill
A small, persistent indicator of system health.  
- Pulsing dot + text  
- Fixed position (header or footer)  
- Colors: green (healthy), amber (degraded), red (down)  

### 5.9 Command CTA
The primary action button on any page.  
- Pill-shaped, gradient fill (accent-1)  
- Dark text on light gradient  
- Hover: scale 1.02, glow shadow  
- Only one per viewport (Law #1)  

### 5.10 Module Constellation
A visual map of interconnected system modules.  
- Orbital layout or grid  
- Nodes represent modules  
- Lines represent data flow  
- Interactive: click to expand details  

---

## 6. Brand Themes

### 6.1 xxxiii — Creative Luxury Intelligence

| Token | Value |
|-------|-------|
| `--sv-bg` | `#0a0a0c` (near-black) |
| `--sv-bg-card` | `#141418` |
| `--sv-bg-hover` | `#1e1e24` |
| `--sv-bg-elevated` | `#141418` |
| `--sv-text` | `#f0f0f5` (cold white) |
| `--sv-text-muted` | `#7a7a8e` |
| `--sv-accent-1` | `#2997ff` (electric blue) |
| `--sv-accent-2` | `#fbbf24` (gold) |
| `--sv-accent-3` | `#bf5af2` (purple) |
| `--sv-glow` | `rgba(41, 151, 255, 0.15)` |
| `--sv-metal` | `#a1a1b0` |
| `--sv-metal-light` | `#d1d1de` |
| `--sv-chrome` | `#e8e8f0` |

**Personality:** Cold precision. Electric minimalism. Every pixel earns its place.  
**Glass:** Selective — nav only. Cards are solid dark.  
**Typography:** Inter for UI, EB Garamond for editorial moments.  

### 6.2 Helios — Settlement Infrastructure

| Token | Value |
|-------|-------|
| `--sv-bg` | `#000000` (true black) |
| `--sv-bg-card` | `#1c1c1e` |
| `--sv-bg-hover` | `#2c2c2e` |
| `--sv-bg-elevated` | `#1c1c1e` |
| `--sv-text` | `#f5f5f7` |
| `--sv-text-muted` | `#86868b` |
| `--sv-accent-1` | `#fbbf24` (amber/gold) |
| `--sv-accent-2` | `#2997ff` (blue) |
| `--sv-accent-3` | `#bf5af2` (purple) |
| `--sv-glow` | `rgba(251, 191, 36, 0.12)` |
| `--sv-metal` | `#a1a1a6` |
| `--sv-metal-light` | `#d1d1d6` |
| `--sv-chrome` | `#e5e5ea` |

**Personality:** Liquid metal authority. Gold is the signal color. Titanium surfaces.  
**Glass:** Selective — nav and overlays only.  
**Typography:** Inter for UI, EB Garamond for formulas and editorial.  

### 6.3 NIL33 — Athletic Capital Intelligence

| Token | Value |
|-------|-------|
| `--sv-bg` | `#101014` (graphite) |
| `--sv-bg-card` | `#1a1a20` |
| `--sv-bg-hover` | `#252530` |
| `--sv-bg-elevated` | `#1a1a20` |
| `--sv-text` | `#f2f2f5` (silver-white) |
| `--sv-text-muted` | `#8a8a96` |
| `--sv-accent-1` | `#e5e5ea` (silver-white) |
| `--sv-accent-2` | `#30d158` (athletic green) |
| `--sv-accent-3` | `#ff6b35` (competition orange) |
| `--sv-glow` | `rgba(229, 229, 234, 0.10)` |
| `--sv-metal` | `#b0b0ba` |
| `--sv-metal-light` | `#d8d8e0` |
| `--sv-chrome` | `#ededf2` |

**Personality:** Precision athletic. Silver dominance with strategic color pops.  
**Glass:** Minimal — scoreboard surfaces only.  
**Typography:** Inter only. No serif. Clean athletic caps.  

### 6.4 Y3K — Future Systems Intelligence

| Token | Value |
|-------|-------|
| `--sv-bg` | `#050508` (deep black) |
| `--sv-bg-card` | `#0f1014` |
| `--sv-bg-hover` | `#1a1c22` |
| `--sv-bg-elevated` | `#0f1014` |
| `--sv-text` | `#e8f0f0` (ice-white) |
| `--sv-text-muted` | `#6a7a7a` |
| `--sv-accent-1` | `#10b981` (emerald) |
| `--sv-accent-2` | `#64d2ff` (ice-blue) |
| `--sv-accent-3` | `#fbbf24` (gold) |
| `--sv-glow` | `rgba(16, 185, 129, 0.12)` |
| `--sv-metal` | `#8a9a9a` |
| `--sv-metal-light` | `#b0c0c0` |
| `--sv-chrome` | `#d0e0e0` |

**Personality:** Cybernetic calm. Emerald pulse on black. Future-now aesthetics.  
**Glass:** Used for system panels and HUD overlays.  
**Typography:** Inter for UI. Monospace for data-heavy displays.  

### 6.5 UnyKorn — Sovereign Creative Platform

| Token | Value |
|-------|-------|
| `--sv-bg` | `#08080c` (deep black) |
| `--sv-bg-card` | `#12121a` |
| `--sv-bg-hover` | `#1c1c28` |
| `--sv-bg-elevated` | `#12121a` |
| `--sv-text` | `#f5f5fa` (pure white) |
| `--sv-text-muted` | `#7878a0` |
| `--sv-accent-1` | `#4a6fff` (royal electric blue) |
| `--sv-accent-2` | `#f5f5fa` (white) |
| `--sv-accent-3` | `#bf5af2` (purple) |
| `--sv-glow` | `rgba(74, 111, 255, 0.15)` |
| `--sv-metal` | `#9090b0` |
| `--sv-metal-light` | `#c0c0d8` |
| `--sv-chrome` | `#e0e0f0` |

**Personality:** Bold creative confidence. Royal blue on black. No compromise.  
**Glass:** Selective — creative preview overlays.  
**Typography:** Inter for UI, EB Garamond for artist statements.  

---

## 7. Device Adaptations

### 7.1 Desktop (1024px+)
- Full navigation bar with all links visible  
- 3-column grids for cards  
- Dock panel slides from right  
- Hero at full scale  
- Module constellation interactive  

### 7.2 Tablet (768px–1023px)
- Navigation: condensed links, key items only  
- 2-column grids  
- Dock panel: right-side overlay (narrower)  
- Hero: 80% scale  

### 7.3 Mobile (< 768px)
- Hamburger navigation, full-screen overlay  
- Single-column layout  
- Dock panel rises from bottom (sheet)  
- Hero: reduced padding, smaller focal object  
- Proof strip stacks to 2×2 grid  
- Metric cards full-width  

### 7.4 Watch (< 200px)
- Single metric display per screen  
- Swipe navigation between views  
- No glass effects (performance)  
- High contrast text only  
- Status pill as primary UI  

### 7.5 Glasses / AR
- HUD overlay positioning  
- Minimal text, large status indicators  
- Glass panels as spatial cards  
- Gaze-triggered progressive reveal  
- Accent glow for active elements  

### 7.6 XR / VR
- Spatial panel arrangement (orbital)  
- Module constellation as 3D space  
- Glass cards as floating panels  
- Depth-based hierarchy (closer = more important)  
- Hand-tracked interaction zones  

---

## 8. Universal Module Families

Every product across all brands assembles from these module types:

| Family | Purpose | Examples |
|--------|---------|----------|
| **Core** | Identity, authentication, profile | Login, member ID, avatar, settings |
| **Intelligence** | AI-driven insights and agents | Ask Helios, analytics, predictions |
| **Execution** | Actions and transactions | Activate, mint, transfer, redeem |
| **Capital** | Financial flows and treasury | Treasury, wallet, earnings, bonds |
| **RWA** | Real-world asset management | Gold vault, certificates, proof |
| **Trust** | Verification and compliance | KYC, proof strips, audit logs |
| **Agentic** | Autonomous AI operations | Automation rails, agent console |

---

## 9. Prompt Templates

### 9.1 New Page Generation
```
Build a [BRAND] page for [PURPOSE].
Use the Sovereign Design System:
- Load sovereign.css + [brand].theme.css
- Follow the 5-layer framework: Attract → Orient → Act → Monitor → Expand
- Apply the 10 Design DNA laws
- Use only sovereign tokens (--sv-*) for all values
- One hero focal object, one command CTA per viewport
- Include proof strip after primary action
- Mobile-responsive with device adaptation rules
```

### 9.2 Component Generation
```
Create a [COMPONENT TYPE] for [BRAND]:
- Reference sovereign.css component classes (.sv-*)
- Apply brand theme tokens from [brand].theme.css
- Follow Design DNA law: [RELEVANT LAW]
- Include hover state with --sv-speed-hover transition
- Ensure WCAG AA contrast ratios
```

### 9.3 Dashboard Generation
```
Build a [BRAND] dashboard for [DOMAIN]:
- Use metric cards with live data bindings
- Include proof strip with verification links
- Live status pill in header
- Signal cards for action items
- Automation rail for active processes
- Module constellation for system overview
```

---

## 10. Migration Path

### From Existing Helios CSS
The current `helios.css` maps directly to the sovereign system:

| Old Token | New Token |
|-----------|-----------|
| `--bg` | `--sv-bg` |
| `--bg-card` | `--sv-bg-card` |
| `--bg-hover` | `--sv-bg-hover` |
| `--bg-elevated` | `--sv-bg-elevated` |
| `--text` | `--sv-text` |
| `--text-muted` | `--sv-text-muted` |
| `--gold` | `--sv-accent-1` (Helios only) |
| `--blue` | `--sv-accent-2` (Helios only) |
| `--purple` | `--sv-accent-3` (Helios only) |
| `--green` | `--sv-success` |
| `--red` | `--sv-danger` |
| `--teal` | `--sv-info` |
| `--metal` | `--sv-metal` |
| `--metal-light` | `--sv-metal-light` |
| `--metal-dark` | `--sv-metal-dark` |
| `--chrome` | `--sv-chrome` |
| `--glass-bg` | `--sv-glass-fill` |
| `--glass-border` | `--sv-glass-border` |
| `--glass-blur` | `--sv-glass-blur` |
| `--border` | `--sv-border` |
| `--radius` | `--sv-radius` |
| `--shadow` | `--sv-shadow` |

### Implementation Order
1. `sovereign.css` loads first — defines all tokens with Helios defaults  
2. `[brand].theme.css` loads second — overrides token values only  
3. `helios.css` continues to work — existing classes remain valid  
4. New pages use `.sv-*` component classes  
5. Existing pages migrate incrementally  

---

## 11. File Architecture

```
static/css/
  sovereign.css          ← Token system + component library
  themes/
    helios.theme.css     ← Helios brand overrides
    xxxiii.theme.css     ← xxxiii brand overrides
    nil33.theme.css      ← NIL33 brand overrides
    y3k.theme.css        ← Y3K brand overrides
    unykorn.theme.css    ← UnyKorn brand overrides
  helios.css             ← Legacy (preserved, gradually migrated)
```

---

## 12. Versioning

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025 | Initial sovereign system — tokens, components, 5 themes |

---

*Sovereign Design System v1 — One language. Every brand. Every surface. Every device.*
