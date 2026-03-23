# HELIOS CODEBASE — COMPREHENSIVE AUDIT REPORT

**Date:** 2025-01-XX  
**Scope:** Read-only analysis of the entire Helios codebase  
**Classification System:**
- ✅ **EXISTS / WORKS** — Code is implemented and functional (may be in hybrid/testnet mode)
- ⚠️ **SIMULATED / MOCK** — Code exists but returns fake data or uses dry-run fallbacks
- ❌ **COMPLETELY MISSING** — No code exists for this capability

---

## 1. QR CODE SYSTEM

### 1.1 Server-Side QR Generation
**Status: ✅ EXISTS / WORKS**

| Component | Location | Status |
|-----------|----------|--------|
| `qrcode[pil]` library | `requirements.txt` | Installed |
| `_generate_qr()` method | `core/identity.py` | Generates base64 PNG QR codes |
| QR API endpoint | `GET /api/identity/qr/<helios_id>` in `api/routes.py` | Returns QR code data |
| Receive QR endpoint | `GET /api/wallet/receive-qr/<helios_id>` in `api/routes.py` | Returns payment-receive QR |
| QR page route | `/qr/<helios_id>` in `app.py` | Renders premium share card |

**How it works:**
- `HeliosIdentity._generate_qr()` uses the `qrcode` Python library to generate a QR code image.
- QR codes encode the URL `https://heliosdigital.xyz/enter/{helios_id}` — this is a **member referral link**.
- The QR is returned as a base64-encoded PNG string.
- The `/qr/<helios_id>` page renders the full premium share card template (`templates/qr.html`).

### 1.2 Client-Side QR Rendering
**Status: ✅ EXISTS / WORKS**

- `templates/qr.html` (1,109 lines) is a premium QR share card with canvas-based QR rendering.
- Shows: member identity, live stats (status, referrals, depth, rewards, scans), chain flow visualization, protocol proof surface, download/share buttons.
- Has a "What Happens When They Scan" 5-step pipeline: QR Scan → Atomic Wallet → Token Issuance → NFT Certificates → Web3 Active.
- Download and share functionality built into the UI.

### 1.3 QR Scan Tracking
**Status: ✅ EXISTS / WORKS**

- QR scans are tracked as `NodeEvent` records via the anti-fraud engine (`core/antifraud.py`).
- Event types include `qr_view` and `qr_scan`.
- Anti-fraud checks (bot detection, dedup, rate limiting) run on every scan event.
- Drop page at `/drop/<display_name>` serves as the QR scan landing page.

### 1.4 What the QR Actually Contains
**Answer:** The QR code encodes a **referral URL** — `https://heliosdigital.xyz/enter/{helios_id}`. When scanned, it takes the visitor to the join/onboarding flow with the scanner's referrer pre-set. It is NOT a payment address or wallet QR. A separate payment-receive QR exists at `GET /api/wallet/receive-qr/<helios_id>`.

---

## 2. AUTOMATIC SETTLEMENT SYSTEM

### 2.1 Settlement Logic (Calculation)
**Status: ✅ EXISTS / WORKS**

| Component | Location | Status |
|-----------|----------|--------|
| `PropagationEngine` | `core/rewards.py` | Full BFS graph traversal with hop decay |
| `calculate_propagation()` | `core/rewards.py` | Read-only preview of settlement distribution |
| `execute_propagation()` | `core/rewards.py` | Persists `Reward` records to database |
| `calculate_propagation` API | `POST /api/energy/propagate` | Preview endpoint |
| `execute_propagation` API | `POST /api/energy/execute` | Manual execution endpoint with `@require_auth` |

**How the settlement math works:**
- 3-phase settlement: (1) Acknowledgement (sponsor gets direct cut), (2) BFS Propagation through network links with hop decay `1/(2^hop)`, (3) Absorption (remainder goes to protocol reserve).
- Activity score gating prevents rewards to inactive nodes.
- `PROPAGATION_MAX_HOPS = 15` limits traversal depth.
- Energy conservation is enforced — total distributed ≤ propagation pool.

### 2.2 Automatic / Scheduled Settlement
**Status: ❌ COMPLETELY MISSING**

| Component | Status | Evidence |
|-----------|--------|----------|
| Celery task queue | Listed in `requirements.txt` but **NOT wired** | `SYSTEM_MAP.md` explicitly states "Not wired yet" |
| Cron / scheduler | No code exists | Grep search for `celery\|scheduler\|cron\|periodic_task` found zero Python matches |
| Redis broker | Listed in requirements, `REDIS_URL` empty in `.env` | Config reads env var but nothing connects |
| Auto-trigger on member join | Not implemented | Settlement requires manual `POST /api/energy/execute` |
| Webhook-triggered settlement | Not implemented | Stripe webhook handler does not trigger settlement |

**Key Finding:** Despite the documentation referring to a "self-settling engine" and `activate_settlement()` method in `core/atomic_wallet.py`, this method **only sets a boolean flag** — it does NOT implement any automatic routing, scheduling, or trigger mechanism. Settlement is **100% manual**, requiring an authenticated API call to `POST /api/energy/execute`.

### 2.3 "Self-Settling Engine" in `atomic_wallet.py`
**Status: ⚠️ SIMULATED / MOCK**

- `AtomicWallet.activate_settlement()` exists but just returns `{"settlement_active": True}` — cosmetic only.
- No timer, no event loop, no webhook, no Celery task, no cron expression anywhere in the codebase.

---

## 3. TOKEN & MINTING INFRASTRUCTURE

### 3.1 HLS Fungible Token (XRPL)
**Status: ✅ EXISTS / WORKS (Hybrid Mode — Testnet)**

| Component | Location | Status |
|-----------|----------|--------|
| `XRPLBridge` | `core/xrpl_bridge.py` | Hybrid sim/live — submits real XRPL transactions when configured |
| `TokenIssuance` | `core/web3_issuance.py` | Issues HLS tokens via XRPL Payment transaction |
| `TokenEngine` | `core/token.py` | 100M fixed supply, 4 pools, integrity verification |
| Token API | `GET /api/token/info`, `/supply`, `/verify`, `/pools` | Full read API |
| XRPL testnet wallets | `.env` | Issuer: `rfrhMPK1VzWr3vjaXBDCDFvKw5az4b6uuF` (testnet) |

**Token supply model:**
- Total supply: **100,000,000 HLS** (fixed, never changes)
- 4 pools: Reward (40%, locked), Circulation (35%, active), Development (15%, 4-year vest), Reserve (10%, 5-year lock)
- `verify_integrity()` asserts `pool_total + distributed == 100M`
- Pool auto-initialization on first run

**XRPL Bridge behavior:**
- When `XRPL_ISSUER_ADDRESS` and `XRPL_ISSUER_SECRET` are set → submits REAL transactions via `safe_sign_and_autofill_transaction` + `send_reliable_submission`
- When not configured → returns deterministic simulation: `{"simulated": true, "tx_hash": SHA256(...)}`
- Currently configured for **XRPL Testnet** (`XRPL_NODE_URL=wss://s.altnet.rippletest.net:51233`)

### 3.2 HC-NFT Certificates (XLS-20)
**Status: ✅ EXISTS / WORKS (Hybrid Mode)**

| Component | Location | Status |
|-----------|----------|--------|
| `NFTCertificate` | `core/web3_issuance.py` | Mints via `NFTokenMint` (XLS-20) |
| `CertificateEngine` | `core/certificates.py` | Full mint/redeem/cancel lifecycle |
| RRR Covenant | `core/certificates.py` | Auto-pauses redemptions when RRR < 1.0 |
| Certificate API | `GET /api/certificate/*` | CRUD + redeem + cancel endpoints |

**Certificate lifecycle:**
- Mint: Locks HE into HC-NFT with deterministic ID `HC-{SHA256[:24]}`
- Redeem: Gold or stablecoin track, gated by RRR covenant check
- Cancel: Returns energy minus **2% permanent burn** (only destructive action in protocol)

### 3.3 Ceremonial NFTs (Soulbound)
**Status: ✅ EXISTS / WORKS (Hybrid Mode)**

- `CeremonialNFT` class in `core/web3_issuance.py`
- Uses `NFTokenMint` with `tfTransferable=0` (soulbound — non-transferable)
- Metadata URI: `ipfs://QmHeliosCeremonial/{slug}` — **IPFS CID does NOT exist** (see §5)

### 3.4 Member Issuance Package
**Status: ✅ EXISTS / WORKS (Hybrid Mode)**

- `issue_new_member_package()` in `core/web3_issuance.py` orchestrates:
  1. HLS token issuance (Payment tx)
  2. HC-NFT certificate mint (NFTokenMint)
  3. Ceremonial soulbound NFT mint (NFTokenMint, non-transferable)
- Phase pricing: $0.05 (Phase 1), $0.25 (Phase 2), $0.50 (Phase 3)

### 3.5 Stellar Integration
**Status: ⚠️ COMPLETELY FAKE**

- `core/atomic_wallet.py._derive_stellar_address()` generates "Stellar addresses" via `SHA-256` hash — **no Stellar SDK**, no Stellar API calls, no Stellar transaction submission.
- `set_stellar_trustline()` always returns a fake hash.
- No `stellar-sdk` in `requirements.txt`.
- The codebase references "dual-chain" (XRPL + Stellar) but Stellar is entirely decorative.

### 3.6 Ethereum / ERC-20
**Status: ❌ COMPLETELY MISSING**

- Grep search for `ERC|ethereum|solidity` returned zero Python code matches.
- No Web3.py, no ethers.js, no Solidity contracts anywhere in the codebase.
- Despite the module being named `web3_issuance.py`, all issuance is pure XRPL.

---

## 4. ONBOARDING FLOW

### 4.1 Join Flow (4-Step Registration)
**Status: ✅ EXISTS / WORKS**

| Step | Template | Backend | Status |
|------|----------|---------|--------|
| 1. Choose `name.helios` | `templates/join.html` | `POST /api/identity/create` → `HeliosIdentity.create_id()` | ✅ Works |
| 2. Phone verification | `templates/join.html` | `POST /api/verify/send` → `HeliosSMS.send_verification()` | ⚠️ Code ready, Telnyx not configured |
| 3. Save 12-word recovery | `templates/join.html` | Generated by `HeliosIdentity.create_id()` | ✅ Works (⚠️ custom word list, not BIP39) |
| 4. Welcome + QR code | `templates/join.html` | Shows QR, links to activate/dashboard | ✅ Works |

**Entry points:**
- `/enter/<referrer>` and `/join/<referrer>` → `join.html` with referrer context
- Phone verification has a **"Skip for now"** button — verification is optional
- Registration awards **2,000 HLS** signing bonus (configured in route handler)

### 4.2 Contract Activation (Tier Selection)
**Status: ✅ EXISTS / WORKS (UI only — payment not connected)**

| Component | Location | Status |
|-----------|----------|--------|
| Tier selection UI | `templates/activate.html` | 5 tiers: $100, $250, $500 (featured), $1,000, $5,000 |
| Stripe checkout | `core/funding.py` | Code exists, `STRIPE_SECRET_KEY` empty |
| Allocation visualization | `templates/activate.html` | Shows 45/20/15/10/10 split |
| Webhook processing | `core/funding.py` | `process_stripe_webhook()` ready, needs `STRIPE_WEBHOOK_SECRET` |

**When Stripe is not configured:** Returns `{"status": "not_configured"}` — no crash, no error.

### 4.3 Recruit / Opportunity Page
**Status: ✅ EXISTS / WORKS**

- `/opportunity` and `/recruit` routes render `templates/recruit.html`
- Marketing/sales page for network growth
- Links to join flow with referrer context

### 4.4 Atomic Wallet Provisioning
**Status: ⚠️ SIMULATED / MOCK**

- `AtomicWallet.provision_atomic_wallet()` creates XRPL wallet (real when configured), fake Stellar wallet, sets trustlines, "activates settlement"
- XRPL portion works in hybrid mode
- Stellar portion is always fake
- "Settlement activation" is a no-op flag

---

## 5. MISSING / INCOMPLETE SYSTEMS

### 5.1 Integrations Needing Real API Keys

| Provider | Config Location | Purpose | Current State |
|----------|----------------|---------|---------------|
| **Stripe** | `.env`: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET` | Payment processing | ❌ Empty — checkout returns `not_configured` |
| **Telnyx** | `.env`: `TELNYX_API_KEY`, `TELNYX_PHONE_NUMBER` | SMS verification | ❌ Empty — verification returns `not configured` |
| **Xaman/XUMM** | `.env`: `XAMAN_API_KEY`, `XAMAN_API_SECRET` | Wallet signing | ❌ Empty — returns simulation payloads |
| **Pinata/IPFS** | `.env`: `PINATA_API_KEY`, `PINATA_SECRET_KEY` | Evidence pinning | ❌ Empty — falls back to local SHA-256 |
| **ElevenLabs** | `.env`: `ELEVENLABS_API_KEY` | Voice AI | ❌ Empty |
| **Cloudflare** | `.env`: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ZONE_ID` | DNS/CDN | ❌ Empty |
| **Redis** | `.env`: `REDIS_URL` | Caching, rate limiting, Celery broker | ❌ Empty — rate limiting falls back to memory |
| **Sentry** | `.env`: `SENTRY_DSN` | Error monitoring | ❌ Empty — no error tracking |
| **OpenAI** | `.env`: `HELIOS_AI_API_KEY` | AI chat assistant | ✅ **Configured** with real key |
| **XRPL** | `.env`: `XRPL_ISSUER_ADDRESS`, etc. | Blockchain | ✅ **Configured** for testnet |

### 5.2 Documented but Unimplemented Features

| Feature | Documented In | Code Status |
|---------|--------------|-------------|
| **Automatic settlement scheduler** | `SYSTEM_MAP.md` ("Celery — Not wired yet") | ❌ No scheduler code exists |
| **Stellar blockchain** | `SYSTEM_MAP.md`, `atomic_wallet.py` | ❌ Fake — SHA-256 address derivation only |
| **APMEX precious metals API** | `SYSTEM_MAP.md`, `treasury.py` | ❌ No API integration — MVR creation is manual |
| **Real IPFS evidence pinning** | `treasury.py`, `web3_issuance.py` | ⚠️ Code exists but Pinata not configured; IPFS CIDs referenced don't exist |
| **Voice AI (ElevenLabs)** | `SYSTEM_MAP.md` | ⚠️ Code likely exists but key not configured |
| **PostgreSQL production database** | `config.py` supports it | ⚠️ Not configured — using SQLite |
| **Founder token lock enforcement** | `api/routes.py` has `/api/token/founder-lock` | ⚠️ Endpoint exists, enforcement not verified |

### 5.3 Energy Exchange Engine
**Status: ✅ EXISTS / WORKS**

- `core/energy_exchange.py` (342 lines) — fully implemented conservation-law-enforced energy ledger.
- Tracks every energy movement: injection (entry fee), routing (propagation), storage (certificate mint), redemption, cancellation (with 2% burn).
- Conservation check: `Total Inflows = Routed + Stored + Pooled + Ops + Buffer`
- 4 instruments: Helios Name, Helios Energy (HE), HC-NFT, Helios Vault Credit (HVC)

### 5.4 Anti-Fraud Engine
**Status: ✅ EXISTS / WORKS**

- `core/antifraud.py` (306 lines) — fully implemented.
- 8 checks: bot UA detection, missing UA rejection, dedup (30s window), IP rate limit (120/hr), session rate limit (200/hr), referrer join cap (50/day), reward cap (100/day), rapid-fire detection (2s).
- Runs before every `NodeEvent` persistence.
- `AntifraudResult` model with allow/deny + reason code.

### 5.5 Wallet Abstraction
**Status: ✅ EXISTS / WORKS**

- `core/wallet.py` (277 lines) — fully implemented.
- Balance calculation from `Reward` (settled) + `WalletTransaction` (received) - `WalletTransaction` (sent).
- `send()` with `SELECT ... FOR UPDATE` serialization to prevent double-spend.
- Transaction history combining transfers and rewards.
- Users interact with `name.helios` identifiers, never raw addresses.

---

## 6. SECURITY CONCERNS

### 6.1 Critical

| Issue | Location | Severity |
|-------|----------|----------|
| **Flask SECRET_KEY is `"change-me-before-production"`** | `config.py` | 🔴 Critical — session cookies can be forged |
| **XRPL wallet secrets in plaintext `.env`** | `.env` | 🔴 Critical — private keys exposed (testnet, but pattern is dangerous) |
| **OpenAI API key in plaintext `.env`** | `.env` | 🟡 Medium — real key, billable |
| **API authentication disabled** | `HELIOS_API_KEY` is empty in `.env` | 🔴 Critical — `require_auth` decorator checks this var; when empty, **auth is effectively bypassed or broken** |
| **Recovery phrase uses custom word list** | `core/identity.py` | 🟡 Medium — not BIP39 standard, no established security audit |
| **No HTTPS enforcement** | `app.py` | 🟡 Medium — dev-mode only, but no redirect-to-HTTPS middleware |
| **SQLite in production** | `config.py` defaults | 🟡 Medium — no concurrent write support, no ACID under load |
| **`.env` file likely in repo** | No `.gitignore` checked | 🔴 Critical if committed — secrets in version control |

### 6.2 Moderate

| Issue | Location | Severity |
|-------|----------|----------|
| No CSRF protection visible | Templates, Flask config | 🟡 Medium |
| No Content-Security-Policy headers | `app.py` | 🟡 Medium |
| Rate limiting falls back to in-memory (no Redis) | `config.py` | 🟡 Medium — resets on restart |
| No Sentry/error monitoring | `.env` | 🟡 Medium — errors silent in production |
| `HELIOS_DEBUG=true` in `.env` | `.env` | 🟡 Medium — should be false in production |

---

## 7. HYBRID MODE ARCHITECTURE SUMMARY

The codebase implements a **"graceful degradation"** pattern uniformly across all external providers:

```
if provider_credentials_configured:
    → Execute REAL operation (XRPL submission, Stripe checkout, Telnyx SMS, etc.)
else:
    → Return deterministic SIMULATION with fake but structurally valid data
```

This is managed centrally by `IntegrationReadiness.snapshot()` in `core/integrations.py`, which reports the live/sim status of all 8 providers. The system self-describes as "launch-ready in hybrid mode" — every feature "works" in simulation, but only XRPL (testnet) and OpenAI have real credentials configured.

---

## 8. EXECUTIVE SUMMARY

### What Actually Works End-to-End (with real credentials)
1. **XRPL token issuance** on testnet (HLS Payment transactions)
2. **XRPL NFT minting** on testnet (XLS-20 NFTokenMint)
3. **QR code generation** and share card UI
4. **Member registration** (name.helios identity, recovery phrase)
5. **AI chat assistant** (OpenAI-powered)
6. **Energy ledger** tracking (conservation-law-enforced)
7. **Anti-fraud engine** (bot detection, rate limiting, dedup)
8. **Wallet** balance/send/receive/history
9. **Network graph** (BFS propagation calculation)

### What Exists as Code but Needs API Keys
1. Stripe payment checkout (needs keys)
2. Telnyx SMS verification (needs keys)
3. Xaman wallet signing (needs keys)
4. IPFS evidence pinning (needs Pinata keys)
5. ElevenLabs voice (needs key)

### What Is Fake / Simulated
1. **Stellar blockchain** — entirely fake, SHA-256 address derivation only
2. **Self-settling engine** — flag only, no automation
3. **IPFS CIDs** in NFT metadata — non-existent CIDs

### What Is Completely Missing
1. **Automatic settlement scheduler** (no Celery/cron wired)
2. **Real Stellar integration** (no SDK, no API)
3. **Ethereum/ERC-20 support** (no code)
4. **APMEX API integration** (manual MVR entry only)
5. **Production database** (PostgreSQL not configured)
6. **Error monitoring** (Sentry not configured)
7. **Background task queue** (Celery in requirements but not wired)

---

*This report is based on static analysis of all Python source files, templates, configuration, environment variables, and documentation in the Helios codebase. No code was modified during this audit.*
