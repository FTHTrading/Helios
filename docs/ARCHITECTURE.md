# Helios v3.0.0 — Architecture Summary

## System Overview

Helios is a **Neural Field Protocol** — an energy exchange network where human
connections inject energy and the protocol distributes it according to physics,
not position. It is **not** an MLM. It uses links, not downlines.

### Core Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Web | Flask 3.1 + Jinja2 | Page routes, API, admin UI |
| Database | SQLAlchemy 2.x (SQLite dev / PostgreSQL prod) | All persistent state |
| Primary Chain | XRPL (xrpl-py 4.x) | HLS token, XLS-20 NFTs, treasury anchoring |
| Secondary Chain | EVM/ERC-20 (web3.py + Solidity) | Optional HLS minting on Ethereum/L2 |
| Background Jobs | Celery 5.4 + Redis | Auto-settlement, IPFS pinning, health checks |
| IPFS | Pinata API | NFT metadata, treasury evidence bundles |
| Payments | Stripe | Fiat on-ramp for contract funding |
| Monitoring | Sentry | Error tracking, performance traces |
| Static Export | Frozen-Flask → Netlify | heliosdigital.xyz public pages |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     heliosdigital.xyz                            │
│                 (Netlify — static pages)                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │ freeze.py (38 pages)
┌──────────────────────────┴──────────────────────────────────────┐
│                    Flask App (app.py)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Page Routes  │  │  API Routes  │  │  EVM API Routes      │  │
│  │  (27 pages)   │  │  (55+ endpts)│  │  (/api/evm/*)        │  │
│  └──────────────┘  └──────┬───────┘  └──────────┬───────────┘  │
│                           │                      │              │
│  ┌────────────────────────┴──────────────────────┴────────┐    │
│  │                     Core Engine                         │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │    │
│  │  │ TokenEngine  │  │ PropagationE │  │ TreasuryEngine│  │    │
│  │  │ (token.py)   │  │ (rewards.py) │  │ (treasury.py) │  │    │
│  │  └─────────────┘  └──────────────┘  └───────────────┘  │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │    │
│  │  │ XRPLBridge   │  │ EVMBridge    │  │ IPFS Service  │  │    │
│  │  │ (Primary)    │  │ (Secondary)  │  │ (Pinata)      │  │    │
│  │  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘  │    │
│  └─────────┼────────────────┼───────────────────┼──────────┘    │
└────────────┼────────────────┼───────────────────┼───────────────┘
             │                │                   │
    ┌────────▼───────┐ ┌─────▼──────┐  ┌─────────▼────────┐
    │  XRPL Testnet  │ │  EVM Chain │  │  Pinata / IPFS   │
    │  (XLS-20 NFTs) │ │  (ERC-20)  │  │                  │
    └────────────────┘ └────────────┘  └──────────────────┘
```

### Dual-Rail Token Architecture

**XRPL is the PRIMARY rail.** ERC-20 is a SECONDARY rail layered beside it.

| Feature | XRPL Rail | EVM Rail |
|---------|-----------|----------|
| HLS Token | Issued Currency (Payment tx) | ERC-20 (`HeliosToken.sol`) |
| NFT Certificates | XLS-20 (NFTokenMint) | — (XRPL only) |
| Ceremonial NFTs | XLS-20 (soulbound) | — (XRPL only) |
| Treasury Anchoring | Self-payment with memo | — (XRPL only) |
| Settlement | On XRPL | — (XRPL only) |
| Token Minting | Via XRPLBridge | Via EVMBridge |

Members can choose their **token rail** (XRPL or EVM) via `Web3Preferences`.
NFTs and settlement always happen on XRPL.

### Database Models

| Model | Table | Purpose |
|-------|-------|---------|
| Member | members | Identity, .helios domain, wallet addresses |
| Certificate | certificates | Gold-backed HC-NFT certificates |
| EnergyEvent | energy_events | ENERGY_IN / ENERGY_OUT events |
| Reward | rewards | Settlement distribution records |
| TokenPool | token_pools | Token allocation pools (7 pools) |
| Transaction | transactions | Financial transaction log |
| VaultReceipt | vault_receipts | Gold vault receipts |
| Bond | bonds | Energy bonds |
| Link | links | Network graph edges |
| AuditLog | audit_log | Immutable audit trail |

### Background Jobs (Celery Beat)

| Task | Schedule | Purpose |
|------|----------|---------|
| `run_scheduled_settlement` | Every 30 minutes | Find & propagate unsettled energy events |
| `check_integration_health` | Every 6 hours | Verify XRPL, Stripe, Pinata connectivity |
| `pin_nft_metadata` | On-demand | Pin NFT metadata to IPFS before minting |
| `pin_treasury_evidence` | On-demand | Pin MVR bundles + XRPL anchor |
| `execute_single_settlement` | On-demand | Immediate settlement for new joins |

### Security Model

- **SECRET_KEY**: Random per-environment, required in production
- **API_KEY**: Bearer token for mutating API endpoints
- **XRPL secrets**: Env vars only, never in code
- **EVM private key**: Env var only, used for MINTER_ROLE operations
- **Audit logging**: All mint/settlement/certificate ops logged to `audit_log` table
- **Idempotency keys**: Prevent duplicate settlements and audit entries
- **Rate limiting**: Flask-Limiter on all API endpoints
- **HTTPS**: ProxyFix middleware for production behind nginx/ALB

---

## File Structure

```
helios final/
├── app.py                    # Flask app factory + page routes
├── config.py                 # All configuration (env vars)
├── config_env.py             # Environment validation (fail-fast)
├── wsgi.py                   # Production WSGI entrypoint
├── celery_app.py             # Celery factory + beat schedule
├── tasks.py                  # Background Celery tasks
├── extensions.py             # Flask-Limiter setup
├── api/
│   ├── routes.py             # 55+ API endpoints (19 blueprints)
│   └── evm_routes.py         # EVM/ERC-20 API endpoints
├── core/
│   ├── token.py              # TokenEngine — pool management
│   ├── rewards.py            # PropagationEngine — BFS settlement
│   ├── treasury.py           # TreasuryEngine — MVR, gold vault
│   ├── xrpl_bridge.py        # XRPL adapter (primary rail)
│   ├── evm_bridge.py         # EVM adapter (secondary rail)
│   ├── web3_issuance.py      # Issuance pipeline + preferences
│   ├── ipfs.py               # Pinata/IPFS service
│   ├── audit.py              # Audit trail + replay protection
│   ├── integrations.py       # Integration readiness checks
│   └── validation.py         # Payload validation schemas
├── models/
│   ├── member.py             # Base + Member model
│   ├── certificate.py        # Gold-backed certificates
│   ├── energy_event.py       # Energy events
│   ├── reward.py             # Reward distributions
│   ├── token_pool.py         # Token allocation pools
│   └── ...                   # 15 models total
├── contracts/
│   └── HeliosToken.sol       # ERC-20 Solidity contract
├── scripts/
│   └── deploy.js             # Hardhat deployment script
├── migrations/
│   ├── env.py                # Alembic environment
│   └── versions/             # Migration scripts
├── tests/
│   ├── conftest.py           # Shared fixtures
│   ├── test_config.py        # Config safety tests
│   ├── test_routes.py        # Route + API tests
│   ├── test_core.py          # Domain logic tests
│   └── test_audit.py         # Audit system tests
├── test/contracts/
│   └── HeliosToken.test.js   # Solidity contract tests
├── templates/                # 38 Jinja2 page templates
├── static/                   # CSS, JS, images
├── Dockerfile                # Production Docker image
├── docker-compose.prod.yml   # 4-service production stack
├── hardhat.config.js         # Solidity compilation + networks
├── package.json              # Node.js deps for Hardhat
├── alembic.ini               # Database migration config
├── requirements.txt          # Python dependencies
└── .github/workflows/ci.yml  # CI pipeline
```
