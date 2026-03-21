# REPO OVERVIEW — Helios

Generated: 2026-03-18  
Working tree: **clean**

---

## Identity

| Field | Value |
|---|---|
| **Repo path** | `C:\Users\Kevan\OneDrive - FTH Trading\03-Helios\helios final` |
| **Repo name** | Helios-launch |
| **Active branch** | `main` |
| **Latest commit** | `c86df21` — feat: 3D spinning gold token in homepage hero |
| **Remote: launch** | https://github.com/FTHTrading/Helios-launch.git |
| **Remote: origin** | https://github.com/FTHTrading/Helios.git |
| **Domain** | heliosdigital.xyz |
| **Version** | 3.0.0 |
| **License** | MIT |

---

## Entry Points

| File | Purpose |
|---|---|
| `app.py` | Flask application factory (`create_app()`) — registers blueprints, security headers, rate limiting, Sentry |
| `wsgi.py` | Production WSGI via Waitress |
| `config.py` | `HeliosConfig` — all 349 lines of protocol parameters + structural `assert` checks on boot |
| `freeze.py` | Static site generator (FrozenFlask) → `/build` for Netlify |
| `audit.py` | 12-category system audit |
| `verify_launch.py` | Launch verification — checks contracts, metrics, and readiness |

---

## Key Folders

| Folder | What it does |
|---|---|
| `core/` | 24 Python engine modules — the protocol layer |
| `api/` | Single `routes.py` — 15 blueprints, 80+ REST endpoints |
| `models/` | 14 SQLAlchemy ORM models |
| `templates/` | 25 Jinja2 HTML pages |
| `static/` | CSS (`helios.css` ~1100 lines), JS (D3 lattice, fallback), images |
| `docs/` | 26 Markdown documentation files |
| `prompts/` | 7 governance/builder/compliance prompt files |
| `data/` | SQLite database (`helios.db`) — dev/hybrid mode |
| `ai/` | Ask Helios GPT-4 integration + knowledge builder |
| `.github/` | CODEOWNERS, dependabot, issue templates, PR template, CI workflows |

---

## Core Engine Modules (`core/`)

| Module | Class / Role |
|---|---|
| `network.py` | `FieldEngine` — Power of 5, BFS field traversal, bond creation |
| `energy_exchange.py` | `EnergyExchange` — conservation law, $100 atomic split |
| `rewards.py` | `PropagationEngine` — 3-phase settlement, hop decay |
| `certificates.py` | `CertificateEngine` — HC-NFT mint/redeem/cancel, RRR covenant |
| `treasury.py` | `TreasuryEngine` — MVR lifecycle, APMEX metals, XRPL anchoring |
| `metrics.py` | `MetricsEngine` — RRR, η, CP, V health metrics |
| `token.py` | `TokenEngine` — fixed 100M HLS supply, anti-rug guarantees |
| `identity.py` | `HeliosIdentity` — name.helios system, 12-word recovery |
| `wallet.py` | Wallet balance, send, receive |
| `atomic_wallet.py` | `AtomicWallet` — dual-chain (XRPL + Stellar) self-settling wallets |
| `web3_issuance.py` | `TokenIssuance` / `NFTIssuance` — XRPL NFTokenMint, HLS delivery |
| `xrpl_bridge.py` | `XRPLBridge` — XRPL adapter, hybrid sim/live mode |
| `xaman.py` | `XamanService` — Xaman/XUMM signing payloads |
| `treasury.py` | `TreasuryEngine` — MVR IPFS evidence + XRPL 0-drop memo anchoring |
| `ipfs.py` | `IpfsBundleService` — Pinata uploads and SHA-256 bundle hashing |
| `funding.py` | `FundingEngine` — Stripe checkout, monetization catalog |
| `integrations.py` | `IntegrationReadiness` — provider readiness snapshot (XRPL, Stripe, Xaman, Pinata) |
| `antifraud.py` | `AntifraudEngine` — rate limits, dedup, bot detection, reward guardrails |
| `infrastructure.py` | Cloudflare DNS/SSL ops |
| `sms.py` | Telnyx SMS verification |
| `voice.py` | ElevenLabs voice AI |
| `spaces.py` | Rooms and hosted events |
| `validation.py` | Request payload validation |
| `build_manifest.py` | Build watermark, fingerprint, deployment route |
| `node_telemetry.py` | Node activity and telemetry tracking |
| `distribution.py` | Reward distribution logic |
| `handoff.py` | Site handoff manifest for docs portal |
| `vcard.py` | Virtual card generation |

---

## Models (`models/`)

| Model | State Machine | Role |
|---|---|---|
| `member.py` | 5 states (instantiated → stable) | Node in the field |
| `bond.py` | 4 states | Undirected peer bond (ordered pair, unique constraint) |
| `certificate.py` | 3 states (active → redeemed / cancelled) | HC-NFT stored energy battery |
| `vault_receipt.py` | 4 states (MVR custody FSM) | Physical metal receipt |
| `energy_event.py` | — | Immutable ledger (7 event types) |
| `reward.py` | — | Settlement records |
| `transaction.py` | — | Activity tracking |
| `token_pool.py` | — | Pool balances |
| `credential.py` | — | Operator/vendor credentials |
| `space.py` | — | Rooms and events |
| `subscription.py` | — | Plus/Pro/Operator tiers |
| `wallet_tx.py` | — | Wallet history |
| `node_event.py` | — | Anti-fraud event log |
| `payment_event.py` | — | Payment tracking |

---

## API Blueprints (`api/routes.py`)

| Blueprint | Prefix | Key endpoints |
|---|---|---|
| `identity_bp` | `/api/identity` | create, verify, recover, QR |
| `field_bp` | `/api/field` | bond, dissolve, graph, status |
| `network_bp` | `/api/network` | field traversal, BFS graph |
| `energy_bp` | `/api/energy` | inject, propagate, conservation |
| `wallet_bp` | `/api/wallet` | balance, send, xaman payload |
| `token_bp` | `/api/token` | verify (100M supply, anti-rug) |
| `chat_bp` | `/api/chat` | Ask Helios GPT-4 |
| `treasury_bp` | `/api/treasury` | reserves, MVR, proof |
| `certificates_bp` | `/api/certificates` | mint, redeem, cancel, covenant |
| `spaces_bp` | `/api/spaces` | rooms, events |
| `metrics_bp` | `/api/metrics` | RRR, η, CP, V — all public |
| `rewards_bp` | `/api/rewards` | settlement, propagation |
| `funding_bp` | `/api/funding` | catalog, checkout, webhook |
| `handoff_bp` | `/api/handoff` | docs handoff manifest |
| `nodes_bp` | `/api/nodes` | ops node dashboard |

---

## Page Routes (Templates)

| Route | Template | Description |
|---|---|---|
| `/` | `index.html` | 3D spinning coin, neural lattice BG |
| `/dashboard` | `dashboard.html` | Balance, history, bond status |
| `/field` | `network.html` | D3 force-directed neural lattice |
| `/ask` | `ask.html` | GPT-4 chat + ElevenLabs voice |
| `/treasury` | `treasury.html` | Metal reserves, MVR |
| `/vault` | `vault.html` | HC-NFT management |
| `/vault/gold` | `vault_gold.html` | 27 APMEX gold products |
| `/activate` | `activate.html` | $100 allocation breakdown |
| `/metrics` | `metrics.html` | RRR, η, CP, V public dashboard |
| `/web3` | `web3.html` | Xaman wallet connect |
| `/join/<ref>` | `join.html` | 4-step onboarding + referral |
| `/enter/<ref>` | `recruit.html` | Referral entry |
| `/status` | `status.html` | System status |
| `/launch` | `launch.html` | Launch page |
| `/qr` | `qr.html` | QR member node sharing |

---

## Deployment Files

| File | Role |
|---|---|
| `requirements.txt` | Pinned Python dependencies |
| `netlify.toml` | Build config, CDN rewrites, post-processing disable |
| `_headers` | Edge caching headers (1yr immutable for static, 5min HTML) |
| `wsgi.py` | Waitress production WSGI |
| `freeze.py` | FrozenFlask static build pipeline |
| `.env.example` | Dev environment template |
| `.env.production.example` | Production environment template |

---

## Protocol Invariants (asserted at boot in `config.py`)

```python
assert token_allocation == 100%        # 40 + 35 + 15 + 10
assert absorption_pools == 100%        # 40 + 25 + 20 + 15
assert energy_allocation == 100%       # 45 + 20 + 15 + 10 + 10
assert FIELD_MAX_BONDS == 5            # Power of 5
assert PROPAGATION_MAX_HOPS == 15      # Energy horizon
assert ENTRY_FEE_USD == 100            # Atomic entry
assert CERTIFICATE_CANCEL_FRICTION == 0.02   # 2% burn
assert metal_coefficient in [0.05, 0.12]     # Bounded range
```

---

## Security-Critical Items

| Item | Detail |
|---|---|
| `HELIOS_SECRET_KEY` | Flask session key — must be strong random in production |
| `HELIOS_XRPL_ISSUER_SECRET` | XRPL issuer wallet seed — controls all token issuance |
| `HELIOS_XRPL_TREASURY_SECRET` | XRPL treasury wallet seed — controls metal anchoring |
| `HELIOS_STRIPE_WEBHOOK_SECRET` | Stripe webhook signature verification |
| `HELIOS_XAMAN_API_SECRET` | Xaman signing secret |
| Anti-fraud engine | `core/antifraud.py` — every node event gated before persist |
| RRR Covenant | `CertificateEngine.check_rrr_covenant()` — no human override path |
| Rate limiting | Flask-Limiter on all routes via `HeliosConfig.RATE_LIMIT_DEFAULT` |
| Security headers | CSP, X-Frame-Options, Referrer-Policy, XSS-Protection — set on every response |
| `.env.example` | No real secrets — all values are blank or placeholder |

---

## Docs Inventory (`docs/`)

| File | Purpose |
|---|---|
| `HELIOS_LAUNCH_BLUEPRINT.md` | Production architecture and deployment stack |
| `HELIOS_WHITE_PAPER.md` | Full white paper |
| `HELIOS_OPERATOR_SYSTEM_GUIDE.md` | Operator-grade setup and validation |
| `HELIOS_SR_ENGINEERED_TOKENOMICS.md` | Senior-engineered tokenomics framing |
| `HELIOS_AI_SYSTEM.md` | Build-aware AI knowledge overview |
| `HELIOS_EXECUTIVE_ONE_PAGER.md` | Non-technical stakeholder summary |
| `HELIOS_FULL_REBUTTAL.md` | Full rebuttal package for diligence |
| `HELIOS_CLAIMS_COVERAGE_MATRIX.md` | Claim-by-claim coverage and remaining work |
| `HELIOS_REVIEW_RESPONSE.md` | Response to March 5 codebase review |
| `HELIOS_DIRECT_RESPONSE_TO_REVIEW.md` | Direct answer to March 5 report |
| `HELIOS_SIMPLIFIED_OPTION.md` | Simpler recommended launch version |
| `FINAL_LAUNCH_READINESS.md` | Final launch status (hybrid mode, launch-ready) |
| `FINAL_RECOMMENDATION.md` | Authoritative route/stack/messaging recommendation |
| `MOVE_FORWARD_RUNBOOK.md` | Full execution runbook handoff → launch |
| `TAKEOVER_START_HERE.md` | First-read for incoming build team |
| `TAKEOVER_PROMPT_PACK.md` | Recommended prompts for incoming team |
| `OPERATOR_HANDOFF_CHECKLIST.md` | Operator setup and launch checklist |
| `GITHUB_HANDOFF_CHECKLIST.md` | GitHub About values, protections, default route |
| `REPOSITORY_ABOUT_SETTINGS.md` | Recommended GitHub repo settings |
| `REPOSITORY_PROTECTIONS.md` | Recommended GitHub branch protections |
| `PUSH_TO_HELIOS_LAUNCH.md` | Exact push steps for this repository |
| `BUILD_ROUTE_OPTIONS.md` | Layered route options for the takeover team |
| `PAGE_ALIGNMENT_MEMO.md` | What to keep/soften/remove from livepage |
| `HELIOS_GO_NO_GO_MEMO.md` | Go/no-go launch memo |
| `MASTER_DESIGN_SYSTEM_V1.md` | Design system reference |
| `HELIOS_LAUNCH_BLUEPRINT.md` | Production blueprint |

---

## Hybrid vs Production Mode

The system runs in **two modes**:

| Mode | Behaviour |
|---|---|
| **Hybrid (default)** | All external provider calls return deterministic dry-run results. Safe to run with no credentials. |
| **Production** | Real XRPL submissions, Stripe checkouts, Pinata IPFS pins, Xaman signing — activated by setting credentials in `.env`. |

Provider readiness is checked at every call via `IntegrationReadiness.snapshot()` in `core/integrations.py`.
