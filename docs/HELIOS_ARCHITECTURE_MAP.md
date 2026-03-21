# Helios Architecture Map

> Version: 3.0.0 | Updated: 2026-03-20

---

## Three-Module Architecture

Helios is organized into **three distinct logical modules**. Understanding this separation is essential for avoiding conceptual bleed between social networking features and future financial operations.

```
┌──────────────────────────────────────────────────────────────┐
│                     heliosdigital.xyz                         │
│               (Brand / Domain / Frontend UI)                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │  MODULE 1   │  │    MODULE 2      │  │   MODULE 3     │  │
│  │  IDENTITY   │  │   NETWORK        │  │   ISSUANCE     │  │
│  │             │  │   RELATIONSHIPS   │  │   (future)     │  │
│  │             │  │                  │  │                │  │
│  │ • create_id │  │ • form_link      │  │ • mint_token   │  │
│  │ • verify_id │  │ • dissolve_link  │  │ • issue_cert   │  │
│  │ • recover   │  │ • get_field      │  │ • place_order  │  │
│  │ • QR codes  │  │ • propagation    │  │ • cap_table    │  │
│  │             │  │ • BFS traversal  │  │ • KYC/AML      │  │
│  │             │  │                  │  │ • compliance   │  │
│  └──────┬──────┘  └────────┬─────────┘  └───────┬────────┘  │
│         │                  │                     │           │
│         └──────────────────┼─────────────────────┘           │
│                            │                                 │
│  ┌─────────────────────────┴──────────────────────────────┐  │
│  │              INFRASTRUCTURE LAYER                       │  │
│  │  XRPL · Stripe · Pinata · Cloudflare · Telnyx · IPFS  │  │
│  │  SQLAlchemy · SQLite/PostgreSQL · ElevenLabs · OpenAI  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Module 1: Identity

**Status: BUILT. Functional.**

### What a Helios Identity Is

A Helios identity is a **platform account** identified by a `<name>.helios` string. Each identity has:

- A unique `helios_id` (e.g., `elliot-a.helios`)
- A SHA256-hashed internal keypair (never exposed to user)
- A 12-word recovery phrase (shown once at creation)
- A display name
- A QR code for enrollment/sharing
- A node state (instantiated → acknowledged → connected → propagating → stable)
- An active/inactive status flag

### What a Helios Identity Is NOT

- Not a wallet address (wallets are provisioned separately)
- Not a login credential (no password/session system exists)
- Not a KYC-verified identity (no document collection)
- Not a legal entity registration

### Code Map

```
core/identity.py       → HeliosIdentity class
models/member.py       → Member database model
api/routes.py          → /api/identity/* endpoints
```

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/identity/create` | Register new identity |
| GET | `/api/identity/verify/<id>` | Verify identity exists |
| POST | `/api/identity/recover` | Recover via 12-word phrase |
| GET | `/api/identity/qr/<id>` | Get enrollment QR |

---

## Module 2: Network Relationships (currently called "bonds")

**Status: BUILT. Functional. Terminology needs rename.**

### What a Link Is (currently called "bond")

A link is an **undirected edge in a bounded peer graph**. It represents a verified relationship between two Helios identities. Properties:

- Undirected — no hierarchy, no "upline/downline"
- Bounded — max 5 links per node
- Ordered — stored as `(node_a, node_b)` where `node_a < node_b` lexicographically
- State machine: ACTIVE ↔ INACTIVE (history is permanent)
- Instant — no cooldown period

### What a Link Drives

- **Node state progression**: connected (1–2 links) → propagating (3–4) → stable (5)
- **Energy propagation**: BFS through links, attenuation `1/(2^hop)`, max 15 hops
- **Reward distribution**: `PropagationEngine` walks the link graph to calculate payouts
- **Field topology**: `get_field()` maps reachable nodes from any starting point

### What a Link Is NOT

- Not a financial bond (no debt, no interest, no maturity date)
- Not an investment unit (no share value, no dividend)
- Not a token (not on-chain, not fungible)
- Not a contract (no terms, no obligations beyond connection)

### Code Map

```
core/network.py        → FieldEngine class (form/dissolve/query)
core/rewards.py        → PropagationEngine (BFS through links for rewards)
models/bond.py         → Bond database model (to be renamed to Link)
core/validation.py     → BondCreate/BondDissolve schemas (to be renamed)
config.py              → FIELD_MAX_BONDS, BOND_STATE_* constants
```

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/field/bond` | Form a link (to become `/api/field/link`) |
| POST | `/api/field/bond/dissolve` | Dissolve a link |
| GET | `/api/field/bonds/<id>` | Get all links for a node |
| GET | `/api/field/<id>` | Get full field from a node |
| GET | `/api/field/<id>/propagation` | Get propagation paths |

---

## Module 3: Issuance (FUTURE — scaffolding exists, not operational)

**Status: SCAFFOLDED. Not issuing anything real.**

### What Exists Today (accounting only)

| Component | What It Does Today | What It Could Do |
|-----------|--------------------|------------------|
| `token.py` | Tracks 4 fixed pools (100M HLS) | Could mint/burn tokens on-chain |
| `certificates.py` | Creates DB records with SHA256 IDs | Could issue real on-chain NFTs |
| `treasury.py` | Records physical metal purchases | Could issue vault-backed stablecoins |
| `web3_issuance.py` | Returns simulation hashes | Could execute live XRPL issuance |
| `funding.py` | Processes Stripe payments | Could process investment subscriptions |
| `wallet.py` | Tracks internal HLS balances | Could hold real on-chain tokens |

### What Does NOT Exist Yet

- Token minting/burning logic
- Investor registry / cap table
- Subscription agreements / SAFEs
- KYC/AML verification pipeline
- Transfer restrictions / compliance engine
- Redemption with real asset delivery
- Regulatory classification
- Offering document generation

### Where heliosdigital.xyz Fits

```
heliosdigital.xyz
      │
      ├── Public marketing pages (templates/)
      ├── Member dashboard (templates/)
      ├── API gateway (api/routes.py → port 5050)
      │     ├── /api/identity/*    ← Module 1
      │     ├── /api/field/*       ← Module 2
      │     ├── /api/energy/*      ← Module 3 (accounting)
      │     ├── /api/certificates/* ← Module 3 (accounting)
      │     ├── /api/treasury/*    ← Module 3 (accounting)
      │     ├── /api/token/*       ← Module 3 (accounting)
      │     └── /api/funding/*     ← Stripe payments
      └── Static assets (static/css, js, img)
```

The domain `heliosdigital.xyz` is the **brand entry point**. It serves:

1. The public-facing web interface (Jinja2 templates)
2. The REST API consumed by frontend JS and mobile apps
3. Static assets (CSS, JS, images)

It is **not** a blockchain endpoint, exchange, or token marketplace.

---

## Data Flow Diagram

```
User arrives at heliosdigital.xyz
      │
      ▼
[1] IDENTITY: Create helios_id → Member record in DB
      │
      ▼
[2] FUNDING: Pay $100 activation → Stripe checkout → webhook → energy injection
      │
      ▼
[3] ENERGY: $100 splits → propagation (45%) + liquidity (20%) + treasury (15%)
      │                    + infrastructure (10%) + buffer (10%)
      ▼
[4] NETWORK: Form links with other members → node state progresses
      │
      ▼
[5] PROPAGATION: Energy flows through link graph → rewards calculated via BFS
      │
      ▼
[6] CERTIFICATES: (Optional) Store energy as HC-NFT → redeem later for gold/stablecoin
      │
      ▼
[7] TREASURY: (Optional) Metal allocation based on surplus → vault receipt created
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.10, Flask 3.1.3 |
| Database | SQLAlchemy 2.0, SQLite (dev) / PostgreSQL (prod) |
| Payments | Stripe (hosted checkout + webhooks) |
| Blockchain | XRPL Testnet (simulation mode default) |
| Storage | Pinata/IPFS (evidence bundles) |
| CDN | Cloudflare (DNS, SSL, cache) |
| SMS | Telnyx (phone verification) |
| Voice | ElevenLabs (TTS) |
| AI | OpenAI (advisory chat) |
| Signing | Xaman/XUMM (XRPL transaction signing) |

---

## What Must Be Built for Real Issuance

If Helios wants to move from "platform with internal accounting" to "platform that issues real financial instruments," these modules must be added:

1. **Auth Layer** — JWT/session management, role-based access
2. **KYC/AML Pipeline** — identity document collection, third-party verification
3. **Token Minting** — actual XRPL issuance with supply management
4. **Investor Registry** — cap table, subscription docs, ownership ledger
5. **Transfer Restrictions** — compliance rules on token movement
6. **Redemption Engine** — real asset delivery (gold, stablecoin, fiat)
7. **Regulatory Framework** — offering classification, filing support
8. **Audit Trail** — immutable compliance logging

These are detailed in `ISSUANCE_LAYER_BLUEPRINT.md`.
