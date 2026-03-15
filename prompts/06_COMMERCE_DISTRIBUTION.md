# COMMERCE & DISTRIBUTION

> If the system cannot be understood, trusted, shared, and converted in a few steps, it is not ready to sell.

This is the layer that turns a beautiful system into a **sellable system**. It governs how every interface supports selling, sharing, spreading, and converting — without breaking the calm, premium, minimal posture established by the layers below.

---

## When To Use This Prompt

- When building any user-facing flow
- When designing landing pages, onboarding, or activation paths
- When adding share, invite, or referral mechanics
- When evaluating whether a page has a clear commercial path
- When generating features that involve CTAs, distribution, or conversion
- Whenever you generate a feature, page, or flow — also define its commerce path

---

## The Forward Doctrine

**Even when the backend is complex, the product must feel simple, clear, premium, and easy to trust.**

This is the permanent operating rule from this point forward:

- All new systems follow this doctrine
- All redesigns move toward this doctrine
- All old systems get simplified toward this doctrine over time
- All features must justify themselves against this doctrine

### The 5-Point Check

For every system, ask:

| # | Question | Rule |
|---|----------|------|
| 1 | **What is the simple promise?** | One sentence only. |
| 2 | **What is the one main thing the user can do?** | Not five. One. |
| 3 | **What is the one reason they trust it?** | Proof, reserve, audit, contract, live state, track record. |
| 4 | **What is the one next action?** | Join, activate, verify, buy, launch, connect, share. |
| 5 | **What complexity can be hidden until later?** | Everything non-essential. |

### The Two-Layer Standard

| Layer | Rule |
|-------|------|
| **Public layer** | Simple, elegant, minimal, premium, obvious |
| **System layer** | Powerful, modular, scalable, compliant, adaptive |

The inside can be advanced. The outside must stay calm.

> **We accept backend complexity when necessary, but we never ship front-end confusion.**

### Decision Rule for Complicated Ideas

If something is complicated, do one of these — in this order:

1. **Compress it** — say it in fewer words, fewer screens, fewer steps
2. **Stage it** — break it into sequential reveals
3. **Hide it behind progressive reveal** — show on demand, not on arrival
4. **Turn it into an advanced mode** — default is simple, power-users opt in
5. **Bench it** — until the core path is clean

---

## The 5 Gears

Every system must now support all 5 gears. If any gear is missing, the system is not complete.

| Gear | Purpose | Test |
|------|---------|------|
| **1. Understand** | User knows what this is in 3 seconds | Can you explain the offer in one sentence? |
| **2. Trust** | User believes it's real, safe, and valuable | Is there a visible proof surface, receipt, or verification? |
| **3. Act** | User completes the primary action | Is there one clear CTA above the fold? |
| **4. Share** | User can spread it to others | Can they share by text, QR, vCard, or link in one tap? |
| **5. Convert** | The share leads to revenue | Does the shared link lead to a clear conversion path? |

---

## Part 1 — The Token/Core Visual Rule

The central token, orb, or core element stays. But it evolves:

| Property | Old | New |
|----------|-----|-----|
| **Spin speed** | Fast, attention-grabbing | Slow, gravitational, breathing |
| **Size** | Large, dominant | Central but proportionate — not the whole show |
| **Glow** | Bright, theatrical | Subtle, deep, expensive-feeling |
| **Depth** | Strong | Preserved — depth is identity |
| **Elegance** | Decorative | Intentional — every photon earns its place |
| **Motion** | Showcase | Living signal — like a heartbeat, not a firework |

**Think gravity, not fireworks.**

The token is proof the system is alive. It is not the product. The product is the action the user takes.

```css
/* Token/core refinement */
.sv-constellation {
  --sv-spin-speed: 30s;          /* was 8-12s — now slower, calmer */
  --sv-core-scale: 0.85;         /* was 1.0 — slightly reduced presence */
  --sv-glow-opacity: 0.25;       /* was 0.5+ — subtler */
  --sv-glow-spread: 40px;        /* was 60px+ — tighter */
}
```

---

## Part 2 — CTA Architecture

### The Rule

- **One primary CTA** — the main conversion action
- **One optional secondary CTA** — usually share or invite
- **Never more than two visible at once**

### Primary CTA Options

Choose one per page/view based on the user's stage:

| User Stage | Primary CTA |
|-----------|-------------|
| Cold visitor | **Get Access** or **Start** |
| Interested | **Join** or **Activate** |
| Onboarding | **Verify** or **Connect** |
| Active member | **Mint**, **Claim**, or **Upgrade** |
| Engaged member | **Invite** or **Share** |
| Commerce | **Book** or **Buy** |

### Secondary CTA Options

| Context | Secondary CTA |
|---------|--------------|
| Any public page | **Share** |
| Profile/contact pages | **Save Contact** |
| Verification pages | **Scan QR** |
| Network pages | **Invite** |

### CTA Design Rules

```html
<!-- Primary: solid, prominent, one per view -->
<button class="sv-btn sv-btn--primary sv-btn--commerce" data-action="join">
  Join Now
</button>

<!-- Secondary: outlined or text-style, subordinate -->
<button class="sv-btn sv-btn--secondary sv-btn--share" data-action="share">
  Share
</button>
```

- Primary CTA uses solid brand color, full contrast
- Secondary CTA uses outline or ghost style, reduced visual weight
- Both must be within the liquid-glass system language
- CTAs never float detached — they belong to a panel, section, or dock
- Mobile: primary CTA anchored to bottom safe area when scrolled past initial position

---

## Part 3 — Distribution Channels

Every system supports 5 native outbound channels. Not all channels are visible everywhere — show only what's relevant.

### Channel 1 — Text Message Link

**One tap.** User taps share → system generates a branded short link → opens native SMS/messaging composer with pre-filled message.

```
Hey — check this out: [Brand] [action]. [short-link]
```

- Pre-filled message: one sentence, one link
- No lengthy descriptions
- Link leads to a page that passes the 5-Gear test
- Mobile-first — must work from share sheet

### Channel 2 — QR Code

**One scan → one destination → one action.**

QR must not be decorative. Every QR code leads to exactly one of:
- Join
- Activate
- Verify
- Connect
- Claim
- Share contact
- Onboard

QR implementation:
- Generated server-side or client-side (no external dependency required)
- Branded — brand color, logo center embed optional
- Scannable at arm's length (minimum 200×200px)
- Downloadable as image
- Printable resolution (300dpi export option)

```html
<div class="sv-qr" data-destination="/join?ref=USER_ID">
  <canvas class="sv-qr__code"></canvas>
  <span class="sv-qr__label">Scan to Join</span>
  <button class="sv-btn sv-btn--ghost sv-qr__download">Save QR</button>
</div>
```

### Channel 3 — vCard Contact

When vCard is available, make it:
- Easy to download (one tap)
- Easy to text (share via messaging)
- Easy to scan (QR that imports contact)
- Clearly branded
- Tied to a real action path (the contact links back to a conversion page)
- Useful for networking, onboarding, and commerce

vCard fields:
```
FN: [Name]
ORG: [Brand / Organization]
TEL: [if available]
EMAIL: [if available]
URL: [profile or conversion page]
NOTE: [one-line brand promise]
PHOTO: [avatar or brand mark, base64 or URI]
```

vCard must open in the native contact app when tapped. No intermediate screens.

### Channel 4 — Copy Link

The simplest channel. One tap → branded link copied to clipboard → toast confirmation.

- Link is a clean short URL (no UTM spam visible to user)
- Tracking parameters are embedded transparently
- Toast: "Link copied" with brand accent, 2s auto-dismiss

### Channel 5 — Invite Flow

Structured referral path for members who want to bring others in:

- Enter recipient's name/phone/email (one field, auto-detect type)
- System sends branded invitation via the appropriate channel
- Invitation leads to a personalized landing page
- Inviter gets attribution (node telemetry, referral tracking)
- Recipient sees who invited them (trust signal)

---

## Part 4 — Share Scope

Sharing works for both individuals and groups.

### One-to-One Share

Default mode. User shares with one person via text, QR, vCard, or link.

### One-to-Many Share

Support flows for:

| Scope | Use Case | Implementation |
|-------|----------|----------------|
| **Team/Operator** | Operator distributes to their team | Bulk invite via CSV, link, or QR batch |
| **Ambassador** | Referral champion distributes widely | Personal referral page + shareable assets |
| **Event/Field** | In-person distribution | Printable QR sheet + NFC tap (future) |
| **Group message** | Share to a group chat | Single link that works in any messaging app |

### Group Share Rules

- One link, one destination — no per-recipient personalization in the link itself
- Attribution via referral code embedded in the URL
- Landing page is the same premium experience as direct visits
- Operator dashboard shows distribution analytics

---

## Part 5 — Share Objects

What can be shared through the distribution channels:

| Share Object | Contains | Leads To |
|-------------|----------|----------|
| **Product invite** | Brand name + one-line promise + link | Join/activate page |
| **Member card** | Name + role + avatar + contact action | Profile or vCard download |
| **Operator card** | Organization + offer + verification badge | Operator page or booking |
| **Activation link** | Personalized onboarding entry | Activation flow |
| **Verification page** | Proof surface + certificate | Verification detail |
| **Payment page** | Amount + purpose + trust cues | Payment/join flow |
| **Contact card** | vCard-ready contact info | Native contact import |
| **Proof page** | Certificate, receipt, or audit | Read-only proof surface |

Every share object renders as a **clean branded share card** — a preview that looks premium in any messaging app's link preview (Open Graph / Twitter Card meta tags).

```html
<!-- Open Graph for share previews -->
<meta property="og:title" content="[Brand] — [Action]">
<meta property="og:description" content="[One-sentence promise]">
<meta property="og:image" content="[Branded card image — 1200×630]">
<meta property="og:url" content="[Clean short URL]">
```

---

## Part 6 — Commercial Clarity

Every share or conversion surface must answer 5 questions — visible or implied in the design:

| # | Question | How It's Answered |
|---|----------|-------------------|
| 1 | **What is being shared?** | Title + one-line description on the share card |
| 2 | **Why should someone click or scan?** | Trust cue (proof strip, verification badge, member count) |
| 3 | **What happens next?** | Clear CTA label ("Join," not "Submit") |
| 4 | **Why can they trust it?** | Visible proof surface on the landing page |
| 5 | **What is the one action after arrival?** | Single primary CTA above the fold |

If any of these 5 are unclear, the surface is not ready to ship.

---

## Part 7 — The Dock Panel

The shell gains a lightweight commerce dock — a minimal action rail that provides access to distribution channels without cluttering the interface.

### Dock Architecture

```html
<nav class="sv-dock sv-dock--commerce" aria-label="Quick Actions">
  <button class="sv-dock__action" data-action="share" aria-label="Share">
    <!-- Share icon -->
  </button>
  <button class="sv-dock__action" data-action="text" aria-label="Text">
    <!-- Message icon -->
  </button>
  <button class="sv-dock__action" data-action="qr" aria-label="QR Code">
    <!-- QR icon -->
  </button>
  <button class="sv-dock__action" data-action="vcard" aria-label="Save Contact">
    <!-- Contact icon -->
  </button>
  <button class="sv-dock__action" data-action="invite" aria-label="Invite">
    <!-- Invite icon -->
  </button>
</nav>
```

### Dock Rules

- Not all actions visible at once — show only what's relevant to the current view
- Maximum 4 visible dock actions on any screen
- Dock appears as a floating minimal bar or integrates into the existing `.sv-dock` component
- Mobile: bottom-anchored, above the safe area
- Desktop: contextual — appears near relevant content or in a rail
- Dock actions open a minimal modal/sheet, never a full page
- All dock actions follow the liquid-glass visual language

---

## Part 8 — The Money Rule (Extended)

Only build commercial flows that:

| ✅ Build | ❌ Do Not Build |
|----------|----------------|
| Shorten the path to revenue | Gimmicky sharing mechanics |
| Increase onboarding conversion | Excessive social chrome |
| Increase referrals or propagation | Noisy referral systems with leaderboards |
| Strengthen trust | Complex growth loops that confuse the product |
| Support real user action | Multiple competing conversion paths |
| Scale across brands | Brand-specific distribution hacks |

---

## Part 9 — Builder Integration

Whenever the Builder (03) generates a feature, page, or flow, it must also define:

| # | Commerce Requirement | Example |
|---|---------------------|---------|
| 1 | **Primary conversion action** | "Join Now" button above the fold |
| 2 | **Share path** | Text link share via native share sheet |
| 3 | **QR path** | QR code on the page leading to the same page |
| 4 | **vCard/contact path** (if relevant) | "Save Contact" for member/operator pages |
| 5 | **Trust cue** | Proof strip showing live node count and last verified block |
| 6 | **What should be reduced or removed** | Remove decorative animation, reduce hero height, cut secondary nav |

If a feature cannot define items 1-3, it is not commerce-ready.

---

## Best Sales-Ready Flow

For a user landing on any system:

```
1. Sees one premium core (the living signal — calm, gravitational)
2. Understands the one main offer (headline + one sentence)
3. Sees proof/trust (proof strip, verification badge, live data)
4. Gets one primary CTA (Join / Activate / Verify / Start)
5. Can share by text / QR / vCard (dock actions or contextual share)
6. Can invite others or distribute to a group (invite flow)
```

That is the whole engine. Six steps. Nothing more.

---

## Best Commercial Pattern Per Brand

| Brand | Primary CTA | Secondary CTA | Key Trust Cue |
|-------|-------------|---------------|---------------|
| **Helios** | Join the Helios Club — $99.95 | Share Invitation | Reserve visibility + insured custody + founding membership |
| **FTH** | Get Access | Save Contact | Trading performance + audit trail |
| **UnyKorn** | Start Building | Invite | Ecosystem growth + founding certificates |
| **xxxiii** | Enter Studio | Share | Creative provenance + co-signs |
| **NIL33** | Get Verified | Save Contact | Identity verification + protection status |
| **Y3K** | Join Impact | Share | Carbon offset proof + impact metrics |

---

## Commerce Checklist

Before shipping any page or flow:

- [ ] All 5 gears present (understand, trust, act, share, convert)
- [ ] Forward Doctrine 5-point check passes
- [ ] One primary CTA — clear, above the fold
- [ ] One secondary CTA maximum — subordinate visual weight
- [ ] At least 2 distribution channels available (text + QR minimum)
- [ ] Share preview renders correctly (Open Graph meta tags set)
- [ ] QR leads to one clear destination with one clear action
- [ ] vCard downloads cleanly into native contacts (if applicable)
- [ ] Token/core is present but calm — slow spin, subtle glow, intentional
- [ ] No more than 4 dock actions visible
- [ ] Landing page from shared link passes the 5-Gear test independently
- [ ] Commercial flow feels native to the liquid-glass system — not bolted on
- [ ] Trust cue is visible without scrolling

---

## The Tollgate Sentence

> **If the system cannot be understood, trusted, shared, and converted in a few steps, it is not ready to sell.**

And the permanent companion:

> **Everything forward must simplify the experience, sharpen the offer, and strengthen the money path.**

---

*Commerce & Distribution v1 — The system that sells itself.*
