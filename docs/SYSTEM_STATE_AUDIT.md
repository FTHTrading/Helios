# Helios v3.0.0 — System State Audit

> Audited: 2026-03-20
> Scope: Full codebase — 26 core modules, 14 models, 1 API router, 1 config
> Auditor: Automated layer analysis

---

## Executive Summary

Helios is a **Flask/SQLAlchemy web application** implementing a bounded peer-to-peer identity network with internal energy accounting, physical precious metal tracking, Stripe payment processing, and optional XRPL blockchain anchoring.

**It is not** a securities issuance platform, token minting engine, or financial bond processor.

The term "bond" in this codebase **always means an undirected peer-to-peer social connection** (max 5 per node). It never refers to a financial debt instrument, fixed-income security, or investment product.

---

## Layer Classification

Every file in the Helios codebase falls into one of five layers:

| Layer | Purpose | File Count |
|-------|---------|------------|
| **IDENTITY** | Who is in the system | 1 core + 1 model |
| **RELATIONSHIP** | Who is connected to whom | 1 core + 1 model |
| **ISSUANCE** | Internal accounting, energy, certificates, treasury | 8 core + 7 models |
| **COMPLIANCE** | Fraud prevention, metrics, validation | 3 core |
| **INFRASTRUCTURE** | External APIs, hosting, telemetry, distribution | 13 core + 5 models |

---

## Layer 1: IDENTITY

### What exists today

| File | Purpose |
|------|---------|
| `core/identity.py` | `HeliosIdentity` — creates `name.helios` IDs, 12-word recovery phrases, QR codes |
| `models/member.py` | `Member` table — helios_id, display_name, key_hash, recovery_hash, node_state, bond_count |

### What it does

- Generates deterministic `<name>.helios` identifiers
- Creates SHA256-hashed internal keypairs (hidden from user)
- Generates 12-word BIP39-style recovery phrases
- Produces enrollment QR codes
- Name validation: 3–24 chars, alphanumeric + hyphens, no reserved words

### What it does NOT do

- No password/login system
- No session management or JWT tokens
- No multi-factor authentication
- No KYC/AML verification
- No identity document collection

---

## Layer 2: RELATIONSHIP (currently called "bonds")

### What exists today

| File | Purpose |
|------|---------|
| `core/network.py` | `FieldEngine` — form/dissolve/query undirected peer connections, BFS field traversal |
| `models/bond.py` | `Bond` table — node_a, node_b (ordered pair), state, initiated_by, timestamps |
| `core/rewards.py` | `PropagationEngine` — BFS through connections for energy distribution |

### What it does

- Creates undirected edges between two `Member` nodes
- Enforces max 5 connections per node ("saturation")
- Normalizes pairs lexicographically (A < B always)
- State machine: ACTIVE ↔ INACTIVE
- Updates node state based on connection count:
  - 0 = instantiated/acknowledged
  - 1–2 = connected
  - 3–4 = propagating
  - 5 = stable
- BFS traversal up to 15 hops for energy propagation
- Distance-based attenuation: `weight = 1/(2^hop)`

### What it does NOT do

- No financial bond issuance
- No debt instruments
- No investment units
- No securities of any kind
- No tokenized relationships

### Current naming confusion

The word "bond" appears in 9 files across the codebase. In every instance, it means "peer-to-peer social connection." This creates risk of confusion with financial bond instruments. **Recommendation: rename to `link`.**

---

## Layer 3: ISSUANCE (internal accounting — NOT financial instrument issuance)

### What exists today

| File | Purpose | Issues Real Assets? |
|------|---------|---------------------|
| `core/token.py` | Fixed 100M HLS pool tracker | **No.** Explicitly says "No minting function exists." |
| `core/energy_exchange.py` | Entry fee splitting + energy ledger | **No.** Internal accounting only. |
| `core/certificates.py` | HC-NFT stored energy records | **No.** DB records with state machine, not real NFTs. |
| `core/treasury.py` | Metal Vault Receipts (physical bullion tracking) | **No.** Records purchases, doesn't create securities. |
| `core/funding.py` | Stripe checkout + webhook processing | **No.** Standard payment processing only. |
| `core/web3_issuance.py` | XRPL token + NFT issuance | **SIMULATION ONLY.** Falls back to fake hashes. |
| `core/wallet.py` | Internal HLS balance tracking | **No.** Balance = sum(rewards) − sent + received. |
| `core/atomic_wallet.py` | Dual-chain wallet provisioning | **SIMULATION ONLY.** XRPL simulation, Stellar incomplete. |

### Critical findings

1. **`token.py` does NOT mint tokens.** It tracks 4 fixed pool allocations for a hard-capped 100M HLS supply. There is no `mint()` function.

2. **`certificates.py` creates DB records, not real NFTs.** Certificates have SHA256 IDs and a state machine (ACTIVE → REDEEMED/CANCELLED), but they are internal records, not on-chain assets.

3. **`web3_issuance.py` is a simulation.** All calls go through `XRPLBridge`, which returns deterministic fake hashes when the xrpl-py SDK or credentials are not configured (which is the current state).

4. **`treasury.py` records metal purchases.** Vault Receipts track physical bullion with IPFS evidence bundles and XRPL memo anchoring. No securitized instruments are created.

5. **`funding.py` processes Stripe payments.** Standard hosted checkout for one-time activation fees ($99.95–$5,000) and subscriptions ($20–$499/mo). No investment instruments.

### What would need to exist for real issuance

- Token minting logic with supply management
- Investor registry and cap table
- Subscription documents / SAFEs / convertible notes
- KYC/AML verification pipeline
- Transfer restrictions and compliance engine
- Redemption and liquidity mechanisms
- Regulatory classification and filing support

**None of these exist today.**

---

## Layer 4: COMPLIANCE

### What exists today

| File | Purpose |
|------|---------|
| `core/antifraud.py` | Bot detection, rate limiting, duplicate suppression |
| `core/metrics.py` | SR-level health metrics: RRR, η, CP, V |
| `core/validation.py` | Marshmallow request payload schemas |

### Gaps

- Anti-fraud only gates node events — not identity creation, wallet sends, or certificate operations
- No authentication/authorization layer on API routes
- No KYC/AML pipeline
- No transaction monitoring
- No regulatory reporting

---

## Layer 5: INFRASTRUCTURE

### What exists today

| File | Purpose |
|------|---------|
| `core/xrpl_bridge.py` | XRPL adapter — simulation fallback |
| `core/xaman.py` | Xaman/XUMM signing payload creation |
| `core/infrastructure.py` | Cloudflare API (DNS, SSL, CDN) |
| `core/integrations.py` | External provider readiness checks |
| `core/sms.py` | Telnyx phone verification |
| `core/voice.py` | ElevenLabs TTS |
| `core/distribution.py` | 5-channel sharing (link, QR, vCard, text, invite) |
| `core/spaces.py` | Community spaces with rooms/events |
| `core/vcard.py` | vCard 3.0 .vcf generation |
| `core/node_telemetry.py` | QR node analytics + event sourcing |
| `core/ipfs.py` | Pinata IPFS pinning |
| `core/build_manifest.py` | Build watermarking |
| `core/handoff.py` | Documentation portal |

---

## Database Schema

### Active Tables (14)

| Table | Records | Layer |
|-------|---------|-------|
| `members` | Helios identities | IDENTITY |
| `bonds` | Peer connections (to be renamed to `links`) | RELATIONSHIP |
| `energy_events` | Immutable energy ledger | ISSUANCE |
| `certificates` | HC-NFT stored energy records | ISSUANCE |
| `token_pools` | Fixed supply pool tracker | ISSUANCE |
| `vault_receipts` | Physical metal custody | ISSUANCE |
| `wallet_transactions` | Internal HLS transfers | ISSUANCE |
| `rewards` | Propagation payout ledger | ISSUANCE |
| `payment_events` | Stripe checkout records | ISSUANCE |
| `credentials` | Annual role certifications | ISSUANCE |
| `subscriptions` | Premium tier management | ISSUANCE |
| `transactions` | General activity log | INFRASTRUCTURE |
| `node_events` | QR telemetry spine | INFRASTRUCTURE |
| `spaces` / `space_events` | Community spaces | INFRASTRUCTURE |

---

## Risk Register

| # | Risk | Severity | Status |
|---|------|----------|--------|
| 1 | No auth/session layer — routes accept helios_id in request body | HIGH | Open |
| 2 | `_internal_key` sent in API response over HTTP | HIGH | Open |
| 3 | Anti-fraud incomplete — only gates node events | MEDIUM | Open |
| 4 | `rewards_total` endpoint references non-existent column `target_id` | LOW | Open |
| 5 | Stellar chain partially implemented — dead code | LOW | Open |
| 6 | `_error_log.txt` writes to working dir in production | LOW | Open |
| 7 | "Bond" terminology creates regulatory/investor confusion | MEDIUM | Fixing now |

---

## Bottom Line

| Question | Answer |
|----------|--------|
| Is Helios issuing financial bonds? | **No.** |
| Is Helios minting tokens? | **No.** Code says "no minting function exists." |
| Is Helios issuing securities? | **No.** |
| Is Helios processing payments? | **Yes** — Stripe activation fees + subscriptions. |
| Is Helios tracking physical metal? | **Yes** — vault receipts with IPFS evidence. |
| Is Helios connected to XRPL? | **In simulation only.** No live issuance. |
| What does "bond" mean? | **Peer-to-peer social connection.** Max 5 per node. |
| What does heliosdigital.xyz represent? | **Brand domain / frontend surface** for the Helios backend. |
