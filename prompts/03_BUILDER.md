# LIQUID GLASS BUILDER

> The Builder is the architect. It takes what passed the Governor and makes it real.

This prompt governs **how** things are built — the visual language, component architecture, module structure, device adaptation, and code patterns. Everything the Builder produces must comply with the Constitution and must have passed the Governor.

---

## When To Use This Prompt

- When designing any page, component, or module
- When writing front-end code (HTML, CSS, JavaScript)
- When structuring back-end endpoints that serve UI data
- When building new components for the sovereign library
- When adapting existing systems for new brands
- When implementing any visual or interactive behavior

---

## Part 1 — The Liquid Glass Visual Language

### Core Principle

Every surface is a **translucent, layered pane** — never a flat card on a flat background. The UI should feel like looking through intelligent glass that organizes information in depth.

### Visual Rules

1. **Depth, not decoration.** Layers communicate hierarchy. Background → mid-ground → foreground. Never add shadow, blur, or transparency for aesthetics alone — each layer must represent a different level of information priority.

2. **One focal point per view.** Every screen has exactly one primary element that captures attention. Everything else supports it. If two elements compete for attention, one must be demoted or the view must be split.

3. **One active panel at a time.** On any screen, only one panel accepts input or drives the primary action. Secondary panels are visible but receded. Expanding a panel collapses or dims others.

4. **Breathing space.** Minimum padding: 1rem between components, 2rem between sections. Content never touches edges. Whitespace is structural, not decorative.

5. **Motion is meaning.** Animations only when they communicate state change: something appeared, something moved, something completed. Duration: 200-400ms. Easing: ease-out for entries, ease-in for exits. Never animate for delight alone.

6. **Glass layers.** Surfaces use `backdrop-filter: blur()` and semi-transparent backgrounds to create depth. Each layer has a defined blur radius and opacity:
   - Background layer: `blur(40px)`, 5-10% opacity
   - Mid-ground (cards, panels): `blur(20px)`, 60-80% opacity  
   - Foreground (modals, popovers): `blur(10px)`, 85-95% opacity
   - Active/focused: Reduce blur, increase opacity — clarity means attention

7. **Color through light, not paint.** Brand colors appear as glows, gradients, and tinted glass — not as solid fills on large areas. Solid color is reserved for:
   - Primary action buttons
   - Status indicators (success, warning, error)
   - Active state highlights
   - Accent text (sparingly)

---

## Part 2 — The 3D Bubble Portal System

### What It Is

The primary navigation metaphor across all brands. Instead of traditional page links, users interact with floating, glass-like orbs that represent destinations, features, or actions.

### How It Behaves

1. **Bubbles float in a gravitational field.** They drift slowly, responding to scroll position and cursor/touch proximity. They are not static grid items.

2. **Proximity activation.** When cursor/touch approaches a bubble, it:
   - Grows slightly (scale 1.0 → 1.08, max 1.15)
   - Increases clarity (blur decreases, opacity increases)
   - Shows a label or preview
   - Emits a subtle light in the brand's accent color

3. **Selection.** Tapping/clicking a bubble transitions the view to that destination. The bubble expands to fill the viewport, becoming the new context. Other bubbles recede or fade.

4. **Hierarchy.** Larger bubbles = more important destinations. Size ratios:
   - Primary (core features): 1x base size
   - Secondary (supporting features): 0.7x
   - Tertiary (settings, info): 0.5x

5. **Constellation mode.** When zoomed out or on a dashboard view, bubbles form a constellation — a spatial map of the entire product. Lines or energy paths can connect related bubbles.

### Implementation Pattern

```
<div class="sv-constellation" data-brand="helios">
  <div class="sv-bubble sv-bubble--primary" data-destination="/dashboard">
    <span class="sv-bubble__icon"><!-- SVG --></span>
    <span class="sv-bubble__label">Dashboard</span>
  </div>
  <div class="sv-bubble sv-bubble--secondary" data-destination="/vault">
    <span class="sv-bubble__icon"><!-- SVG --></span>
    <span class="sv-bubble__label">Vault</span>
  </div>
</div>
```

---

## Part 3 — The AI Narration Rail

### What It Is

A persistent, context-aware AI assistant surface that lives at the edge of every view. It narrates what the user is seeing, suggests next actions, and provides explanations without requiring the user to ask.

### Behavior Rules

1. **Position:** Right rail on desktop (280-320px wide), bottom sheet on mobile (40vh max).

2. **Always present, never intrusive.** The rail is collapsed by default to a thin indicator strip. It expands when:
   - The user hovers/taps the indicator
   - The system has a proactive insight to share
   - The user completes a significant action

3. **Context-driven content.** The rail reads the current view and surfaces:
   - What this page/data means in plain language
   - What the user should do next
   - Warnings or opportunities based on the data
   - Related actions (max 3)

4. **Tone:** Conversational but concise. First person plural ("We see...", "Your network..."). Never robotic. Never condescending. Match the brand voice from the Brand Skin prompt.

5. **Memory.** The rail remembers recent interactions within the session. It does not repeat the same suggestion twice. It builds on previous context.

### Implementation Pattern

```
<aside class="sv-rail" aria-label="AI Assistant">
  <div class="sv-rail__indicator">
    <span class="sv-rail__pulse"></span>
  </div>
  <div class="sv-rail__content">
    <div class="sv-rail__narration">
      <!-- AI-generated context -->
    </div>
    <div class="sv-rail__actions">
      <!-- Suggested next actions -->
    </div>
  </div>
</aside>
```

---

## Part 4 — Proof Surfaces

### What They Are

Visual elements that display verifiable proof of system activity. They make the invisible visible — transactions confirmed, nodes active, rewards distributed, certificates issued.

### Rules

1. **Every transaction surface shows a receipt.** Any action involving money, tokens, or assets produces a visible, timestamped proof element.

2. **Live counters are always real.** Never display animated counters that count up to a static number. Every number must reflect a live query or a cached real value with a visible timestamp.

3. **Proof strips.** Horizontal bars showing live system stats. Always visible on key pages (dashboard, vault, network). Updated via polling or WebSocket.

4. **Certificate surfaces.** Any earned credential, badge, or certificate renders as a verifiable card with:
   - Issue date
   - Issuer identity
   - Verification method (link, QR, hash)
   - Visual distinction from regular cards

### Proof Strip Pattern

```
<div class="sv-proof-strip">
  <div class="sv-proof-strip__item">
    <span class="sv-proof-strip__label">Active Nodes</span>
    <span class="sv-proof-strip__value" data-live="node-count">--</span>
  </div>
  <div class="sv-proof-strip__item">
    <span class="sv-proof-strip__label">Total Staked</span>
    <span class="sv-proof-strip__value" data-live="total-staked">--</span>
  </div>
  <div class="sv-proof-strip__item">
    <span class="sv-proof-strip__label">Last Block</span>
    <span class="sv-proof-strip__value" data-live="last-block">--</span>
  </div>
</div>
```

---

## Part 5 — Device Adaptation

### Philosophy

Not "responsive design" — **adaptive intelligence.** Each device class gets a purpose-appropriate experience, not a reflowed version of the desktop.

### Device Classes

| Class | Viewport | Primary Interaction | UI Adaptation |
|-------|----------|-------------------|---------------|
| **Watch** | < 200px | Glance + tap | Single metric + one action. Status/notification only. |
| **Phone** | 200-767px | Touch + scroll | Stacked flow. One panel visible. Bottom sheet for rail. Bubble nav collapses to dock. |
| **Tablet** | 768-1199px | Touch + keyboard | Split view option. Rail as sidebar. Bubble constellation partially visible. |
| **Desktop** | 1200-1799px | Cursor + keyboard | Full layout. Rail as right sidebar. Full constellation. Multi-panel. |
| **Ultra-wide** | 1800px+ | Cursor + keyboard | Expanded workspace. Side-by-side panels. Constellation as background layer. |

### Adaptation Rules

1. **Content priority shifts by device.** Phone shows the single most important metric and action. Desktop shows the full context. Never hide critical information — re-prioritize it.

2. **Touch targets.** Minimum 44x44px on touch devices. Minimum 32x32px on cursor devices. No exceptions.

3. **Navigation transformation:**
   - Phone: Bottom dock (max 5 items) + hamburger for overflow
   - Tablet: Side rail (collapsed) or bottom dock
   - Desktop: Top nav + bubble constellation
   - Watch: Single-action screen, swipe between views

4. **Progressive disclosure.** More detail appears as screen size increases. Phone shows summary → Tablet shows summary + chart → Desktop shows summary + chart + table + rail.

---

## Part 6 — The Shared Shell Architecture

### What Never Changes Between Brands

These architectural elements are identical across all brands. Only the visual tokens (colors, fonts, spacing scale) change.

1. **Grid system.** 12-column fluid grid with consistent breakpoints.
2. **Component API.** Every `.sv-*` component accepts the same props/attributes.
3. **Data flow.** API → State → Component → Render. Same pattern everywhere.
4. **Auth flow.** Login → Session → Token refresh. Same everywhere.
5. **Routing structure.** Same URL patterns, same page types.
6. **Error handling.** Same error states, same recovery patterns.
7. **Accessibility.** Same ARIA patterns, same keyboard navigation, same screen reader support.
8. **Performance budgets.** Same targets:
   - First Contentful Paint: < 1.5s
   - Largest Contentful Paint: < 2.5s
   - Total Blocking Time: < 200ms
   - Cumulative Layout Shift: < 0.1
   - Bundle size: < 200KB initial JS, < 50KB initial CSS

### What Changes Between Brands

Only these elements change, and they change ONLY through the Brand Skin prompt:

1. Color tokens (palette, gradients, glass tints)
2. Typography emphasis (which font gets prominence)
3. Copy tone (formal ↔ casual spectrum)
4. Module naming (what features are called)
5. Voice personality (AI rail character)
6. Trust emphasis (which proof surfaces get priority)

---

## Part 7 — Module Architecture

### The 7 Module Families

Every feature maps to one of 7 module families. Modules are the building blocks of pages.

| Family | Purpose | Examples |
|--------|---------|----------|
| **Identity** | User profile, auth, credentials | Login, signup, profile, KYC |
| **Treasury** | Money, tokens, payments | Wallet, vault, staking, transactions |
| **Network** | Connections, referrals, nodes | Member map, node status, referral tree |
| **Intelligence** | AI, analytics, insights | Dashboard metrics, AI rail, reports |
| **Proof** | Certificates, verification, audit | Certificates, receipts, chain explorer |
| **Commerce** | Products, subscriptions, marketplace | Plans, upgrades, energy exchange |
| **Communication** | Messaging, notifications, alerts | SMS, email, in-app messages, alerts |

### Module Rules

1. **One module, one family.** If a module spans two families, split it.
2. **Modules are brand-agnostic.** They work across all brands with only token changes.
3. **Modules are composable.** Pages are assemblies of modules. A dashboard page might use: 1 Intelligence module + 1 Treasury module + 1 Network module.
4. **Modules own their data.** Each module fetches its own data through a dedicated API endpoint. No module reaches into another module's data.
5. **Modules declare their dependencies.** If Module A needs data from Module B, it declares that dependency explicitly, and the page orchestrator handles it.

---

## Part 8 — Code Patterns

### CSS

```css
/* Always use sovereign tokens */
.sv-component {
  background: var(--sv-glass-bg);
  border-radius: var(--sv-radius-lg);
  padding: var(--sv-space-4);
  color: var(--sv-text-primary);
  backdrop-filter: blur(var(--sv-blur-md));
  transition: var(--sv-transition-base);
}

/* States via data attributes, not class toggling */
.sv-component[data-state="active"] {
  background: var(--sv-glass-bg-active);
}

/* Brand customization via CSS custom properties only */
/* NEVER use brand-specific class names */
```

### HTML

```html
<!-- Semantic, accessible, data-driven -->
<section class="sv-module" data-module="treasury" data-brand="helios" role="region" aria-label="Treasury Overview">
  <header class="sv-module__header">
    <h2 class="sv-module__title">Treasury</h2>
  </header>
  <div class="sv-module__body">
    <!-- Module content -->
  </div>
</section>
```

### JavaScript

```javascript
// Config-driven, no hardcoded brand logic
const module = {
  init(config) {
    this.brand = config.brand;
    this.endpoint = config.endpoint;
    this.render(config.container);
  },
  async fetchData() {
    const res = await fetch(this.endpoint);
    return res.json();
  },
  render(container) {
    // Pure render from data — no brand conditionals
  }
};
```

### Python (Flask)

```python
# Modules expose clean API endpoints
@bp.route('/api/v1/<module>/summary')
def module_summary(module):
    """Every module has a summary endpoint."""
    engine = MODULE_ENGINES.get(module)
    if not engine:
        return jsonify({"error": "unknown_module"}), 404
    return jsonify(engine.get_summary())
```

---

## Builder Checklist

Before submitting any built feature, verify:

- [ ] Passes all 8 Governor gates
- [ ] Uses sovereign tokens (no hardcoded colors, sizes, or spacing)
- [ ] One focal point per view
- [ ] One active panel at a time
- [ ] Proof surfaces for any transaction or credential
- [ ] AI rail integration (context narration available)
- [ ] Adaptive behavior for phone, tablet, desktop (minimum)
- [ ] Accessible (ARIA labels, keyboard nav, screen reader tested)
- [ ] Performance within budget (check LCP, TBT, CLS)
- [ ] Module belongs to exactly one family
- [ ] Component is reusable across ≥ 2 brands
- [ ] No brand-specific conditionals in code (tokens only)

---

*Liquid Glass Builder v1 — The architect builds what the Governor approves, within the Constitution's laws.*
