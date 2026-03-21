# SYSTEM MAP — Helios

Generated: 2026-03-18

Full architecture map of the Helios Neural Field Protocol codebase.

---

## System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│          PRESENTATION LAYER (templates/ + static/)              │
│  25 Jinja2 pages · D3 force graph · 3D CSS coin · lattice BG   │
├─────────────────────────────────────────────────────────────────┤
│          API LAYER (api/routes.py)                              │
│  15 Flask blueprints · 80+ REST endpoints · handle_errors()    │
├─────────────────────────────────────────────────────────────────┤
│          APPLICATION FACTORY (app.py)                           │
│  create_app() · Flask-Limiter · Sentry · Security headers       │
│  HeliosConfig.validate() on boot                                │
├─────────────────────────────────────────────────────────────────┤
│          PROTOCOL ENGINES (core/)                               │
│  FieldEngine · EnergyExchange · PropagationEngine               │
│  CertificateEngine · TreasuryEngine · MetricsEngine             │
│  TokenEngine · AtomicWallet · WebIssuance · AntifraudEngine     │
├─────────────────────────────────────────────────────────────────┤
│          DATA LAYER (models/ + data/)                           │
│  14 SQLAlchemy models · SQLite (dev) / PostgreSQL (prod)        │
├─────────────────────────────────────────────────────────────────┤
│          EXTERNAL INTEGRATIONS                                  │
│  XRPL · Xaman · Stripe · Pinata/IPFS · Cloudflare              │
│  ElevenLabs · Telnyx · OpenAI · Sentry · Redis                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Flow

```
HTTP Request
    │
    ▼
app.py — security_headers() [before_request]
    │        rate limiter check (Flask-Limiter)
    │        db session open (g.db_session)
    ▼
api/routes.py — Blueprint route handler
    │        @handle_errors decorator
    │        validate_payload()
    ▼
core/*.py — Engine method
    │        anti-fraud check (antifraud.py) for write ops
    │        business logic
    │        model create/update
    ▼
models/*.py — SQLAlchemy ORM
    │        db.add() / db.commit()
    ▼
data/helios.db (SQLite) or PostgreSQL
    │
    ▼
api_response(data, status) → JSON
    │
    ▼
security_headers() [after_request]
    │
    ▼
HTTP Response
```

---

## Protocol Engine Dependency Graph

```
config.py (HeliosConfig)
    ├── core/network.py (FieldEngine)
    │       └── models/member.py, models/link.py
    │
    ├── core/energy_exchange.py (EnergyExchange)
    │       └── core/rewards.py (PropagationEngine)
    │           └── models/energy_event.py, models/reward.py
    │
    ├── core/certificates.py (CertificateEngine)
    │       ├── core/metrics.py (MetricsEngine) ← RRR covenant check
    │       └── models/certificate.py
    │
    ├── core/treasury.py (TreasuryEngine)
    │       ├── core/ipfs.py (IpfsBundleService)
    │       ├── core/xrpl_bridge.py (XRPLBridge)
    │       └── models/vault_receipt.py
    │
    ├── core/metrics.py (MetricsEngine)
    │       └── models/energy_event.py, models/member.py, models/certificate.py
    │
    ├── core/token.py (TokenEngine)
    │       └── models/token_pool.py
    │
    ├── core/identity.py (HeliosIdentity)
    │       └── models/member.py
    │
    ├── core/atomic_wallet.py (AtomicWallet)
    │       └── core/xrpl_bridge.py
    │
    ├── core/web3_issuance.py (TokenIssuance, NFTIssuance)
    │       └── core/xrpl_bridge.py
    │
    ├── core/funding.py (FundingEngine)
    │       └── core/integrations.py (IntegrationReadiness)
    │
    ├── core/xaman.py (XamanService)
    │       └── config.XAMAN_API_KEY / XAMAN_API_SECRET
    │
    ├── core/antifraud.py (AntifraudEngine)
    │       └── models/node_event.py
    │
    └── core/integrations.py (IntegrationReadiness)
            └── HeliosConfig — all provider keys
```

---

## Data Model Relationships

```
Member (node)
  ├── has many Links (node_a / node_b — undirected, unique pair)
  ├── has many Certificates (HC-NFTs)
  ├── has many EnergyEvents (immutable ledger entries)
  ├── has many Rewards (settlement records)
  ├── has many Transactions
  ├── has many WalletTx
  ├── has many NodeEvents (anti-fraud log)
  └── has one Subscription (Plus / Pro / Operator)

VaultReceipt (MVR)
  └── linked to EnergyEvent (ENERGY_POOL → treasury)

TokenPool
  └── tracks pool balances (reward, stability, liquidity, intelligence, compliance)

Credential
  └── operator / vendor / host access records

Space
  └── rooms + events (paid hosted content)
```

---

## 4 Finite State Machines

### 1. Node (Member) FSM
```
INSTANTIATED → ACKNOWLEDGED → CONNECTED → PROPAGATING → STABLE
    (created)    (initiator       (≥1 link)    (≥3 links)   (5 links)
                  paid)
```
Transition triggered automatically by `member.update_node_state()` on every link change.

### 2. Link FSM
```
PENDING → ACTIVE → INACTIVE
              └──→ DISPUTED
```
Undirected. `ordered_pair(a, b)` normalisation + `UniqueConstraint` prevents duplicates and hierarchy.

### 3. Certificate (HC-NFT) FSM
```
ACTIVE → REDEEMED   (gold or stablecoin exit — gated by RRR covenant)
       → CANCELLED  (2% energy burned permanently, rest returned)
```
ID is deterministic: `HC-{SHA256(holder+amount+epoch+rate)[:24]}`

### 4. MVR Custody FSM
```
ORDERED → IN_TRANSIT → IN_TREASURY → REDEEMED
```
Each state change anchored to XRPL via 0-drop self-payment memo.

---

## 7 Energy Event Types (Immutable Ledger)

| Type | Direction | Trigger |
|---|---|---|
| `ENERGY_IN` | External → system | $100 entry payment received |
| `ENERGY_ROUTE` | Hop-by-hop | Propagation through a link |
| `ENERGY_STORE` | → Certificate | Energy locked into HC-NFT |
| `ENERGY_POOL` | → Protocol pool | Post-hop-15 absorption |
| `ENERGY_BURN` | → Destroyed | Cancel friction (2%), compliance |
| `ENERGY_REDEEM` | Certificate → exit | Gold or stablecoin redemption |
| `ENERGY_CANCEL` | Certificate → partial burn | Certificate cancelled |

Conservation law verified at every call: `∑IN = ROUTE + STORE + POOL + BURN`

---

## $100 Atomic Entry Split

| Destination | % | Amount |
|---|---|---|
| Propagation (links, 15 hops) | 45% | $45.00 |
| Treasury (metal spine) | 20% | $20.00 |
| Protocol stability pool | 15% | $15.00 |
| Network liquidity | 10% | $10.00 |
| Compliance / compliance buffer | 10% | $10.00 |

Every dollar has a declared destination. Verified by `GET /api/energy/conservation`.

---

## Token Allocation (100,000,000 HLS — hard cap, no mint)

| Pool | % | Amount | Lock |
|---|---|---|---|
| Reward Pool | 40% | 40,000,000 HLS | Smart contract lock |
| Circulation | 35% | 35,000,000 HLS | — |
| Development | 15% | 15,000,000 HLS | 4-year vest |
| Reserve | 10% | 10,000,000 HLS | 5-year lock |
| **Total** | **100%** | **100,000,000 HLS** | |

Founder lock: 3 years. `can_mint: False`. Verifiable: `GET /api/token/verify`.

---

## Propagation Decay (hop weight)

```
weight(hop) = 1 / (2^hop)

Hop  Weight     % of $45
─────────────────────────
 1   50.000%    $22.50
 2   25.000%    $11.25
 3   12.500%     $5.63
 4    6.250%     $2.81
 5    3.125%     $1.41
 6    1.563%     $0.70
 7    0.781%     $0.35
...
15    0.003%     $0.001  → absorbed into protocol pools
```

BFS on undirected graph. `PropagationEngine.calculate_propagation()`.

---

## 4 Protocol Health Metrics (all public)

| Metric | Formula | Target |
|---|---|---|
| **RRR** | LiquidTreasury / 30d_RedeemDemand | ≥ 3.0 |
| **η (Flow)** | (Routed + Stored + Pooled) / In | ≥ 0.95 |
| **CP (Churn)** | CancelRequests / ActiveNodes | < 0.02 |
| **V (Velocity)** | Transfers_7d / StoredEnergy | ~ 0.30 |

RRR < 1.0 = auto-pause on redemptions. No human override. `CertificateEngine.check_rrr_covenant()`.

---

## External Provider Integration Map

| Provider | Module | Purpose | Hybrid fallback |
|---|---|---|---|
| **XRPL** | `core/xrpl_bridge.py` | Token issuance, trustlines, anchoring | Deterministic SHA-256 dry-run tx |
| **Xaman/XUMM** | `core/xaman.py` | Wallet signing payloads | Returns simulated payload |
| **Stripe** | `core/funding.py` | Hosted checkout, webhooks | Returns mock session |
| **Pinata/IPFS** | `core/ipfs.py` | MVR evidence bundles | Returns local SHA-256 hash only |
| **Cloudflare** | `core/infrastructure.py` | DNS/CDN/SSL ops | No-op |
| **OpenAI** | `ai/ask_helios.py` | GPT-4 Ask Helios chat | Returns static fallback |
| **ElevenLabs** | `core/voice.py` | Voice AI for Ask Helios | Silenced |
| **Telnyx** | `core/sms.py` | SMS verification | No-op |
| **PostgreSQL** | `config.py` DATABASE_URL | Production database | Falls back to SQLite |
| **Redis** | `config.py` REDIS_URL | Rate limit storage | In-memory |
| **Sentry** | `app.py` | Error monitoring | Disabled |
| **Celery** | — | Background tasks | Not wired yet |

Provider readiness verified at runtime by `IntegrationReadiness.snapshot()` → `core/integrations.py`.

---

## Monetization Stack

| Offer | Price | Mode |
|---|---|---|
| Atomic Entry | $100 | One-time payment |
| Builder Activation | $250 | One-time payment |
| Protocol Contract | $500 | One-time payment (featured) |
| Accelerator Activation | $1,000 | One-time payment |
| Architect Activation | $2,500 | One-time payment |
| Plus subscription | recurring | Monthly |
| Pro subscription | recurring | Monthly |
| Operator subscription | recurring | Monthly |
| Operator credential | recurring | Monthly |
| Vendor credential | recurring | Monthly |
| Paid Spaces | per-event | Hosted events |

HLS token price: $0.05 Phase 1 · $0.25 Phase 2 · $0.50 Phase 3

---

## Deployment Paths

| Path | Command | Output |
|---|---|---|
| Dev server | `python app.py` | `http://localhost:5050` |
| Production WSGI | `python wsgi.py` | Waitress multi-threaded |
| Static Netlify build | `python freeze.py` | `/build` directory |
| System audit | `python audit.py` | 12-category report |
| Launch verify | `python verify_launch.py` | Readiness check |

---

## Security Architecture

| Control | Implementation |
|---|---|
| Rate limiting | `Flask-Limiter` — configurable per-route and global |
| Security headers | `app.after_request` — CSP, X-Frame-Options, Referrer-Policy |
| Build fingerprint | SHA-256 build ID in every response header |
| Anti-fraud | `AntifraudEngine` — dedup window, IP/session rate limits, bot UA detection |
| RRR circuit breaker | `CertificateEngine.check_rrr_covenant()` — no override path |
| Protocol invariants | `HeliosConfig.validate()` — fails fast at boot if rules broken |
| Secret isolation | All secrets in `.env`, never committed |
| Error masking | `handle_errors()` decorator — internal errors never surfaced to API |
