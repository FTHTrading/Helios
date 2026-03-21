# Helios v3.0.0 — Production Readiness Checklist

> Everything required to move from working testnet to live clients.
> Hand this to your dev team. Every box must be checked before go-live.

---

## 1. Credentials & Secrets

### Stripe (Payments)
- [ ] Register at [dashboard.stripe.com](https://dashboard.stripe.com)
- [ ] Copy **Publishable key** → `.env` → `STRIPE_PUBLIC_KEY`
- [ ] Copy **Secret key** → `.env` → `STRIPE_SECRET_KEY`
- [ ] Create webhook endpoint pointing to `https://yourdomain.com/api/funding/webhook/stripe`
- [ ] Copy **Webhook signing secret** → `.env` → `STRIPE_WEBHOOK_SECRET`
- [ ] Test with card `4242 4242 4242 4242` (any future date, any CVC)
- [ ] Verify `GET /api/infra/readiness` shows `stripe.ready = true`

### Xaman / XUMM (Mobile Signing)
- [ ] Register at [apps.xumm.dev](https://apps.xumm.dev)
- [ ] Copy **API Key** → `.env` → `XAMAN_API_KEY`
- [ ] Copy **API Secret** → `.env` → `XAMAN_API_SECRET`
- [ ] Verify `GET /api/infra/readiness` shows `xaman.ready = true`

### XRPL (Mainnet)
- [ ] Generate **mainnet** issuer wallet (DO NOT reuse testnet keys)
- [ ] Generate **mainnet** treasury wallet
- [ ] Update `.env`:
  ```
  HELIOS_XRPL_WALLET=<mainnet issuer address>
  HELIOS_XRPL_SECRET=<mainnet issuer seed>
  HELIOS_XRPL_TREASURY_WALLET=<mainnet treasury address>
  HELIOS_XRPL_TREASURY_SECRET=<mainnet treasury seed>
  HELIOS_XRPL_ENABLE_SUBMIT=true
  ```
- [ ] Fund both wallets with minimum 20 XRP reserve + operating buffer
- [ ] Verify `GET /api/infra/readiness` shows `xrpl.ready = true, simulation = false`

### OpenAI (Helios AI / Ask)
- [ ] Get API key from [platform.openai.com](https://platform.openai.com)
- [ ] Set `.env` → `OPENAI_API_KEY`
- [ ] Test: `POST /api/chat/ask` with `{ "question": "What is Helios?" }`

---

## 2. Database

### Current: SQLite (dev only)
- Default path: `data/helios.db`
- Fine for testing, **not for production**

### Target: PostgreSQL
- [ ] Provision PostgreSQL instance (Supabase, Railway, Neon, or managed AWS/Azure)
- [ ] Set `.env` → `HELIOS_DATABASE_URL=postgresql://user:pass@host:5432/helios`
- [ ] Install driver: `pip install psycopg2-binary` (already in requirements.txt)
- [ ] Run app once to auto-create tables (SQLAlchemy `create_all()` runs on startup)
- [ ] Verify all 15 models created: Member, Transaction, TokenPool, WalletTx, Link, Certificate, Credential, EnergyEvent, NodeEvent, PaymentEvent, Reward, Space, Subscription, VaultReceipt
- [ ] Set up automated daily backups

---

## 3. Application Server

### Never use `python app.py` in production.

**Option A — Waitress (Windows-compatible):**
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5050 --threads=8 wsgi:application
```

**Option B — Gunicorn (Linux/macOS):**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5050 wsgi:application
```

- [ ] WSGI entry point: `wsgi.py` (already configured)
- [ ] `HELIOS_SECRET_KEY` set to a strong random value (not default)
- [ ] `FLASK_ENV=production` or omitted (defaults correctly)
- [ ] Rate limiter configured in `app.py` (Flask-Limiter, already wired)

---

## 4. Static Frontend (Netlify)

The frontend is pre-built as static HTML via `freeze.py`.

- [ ] Connect repo to Netlify
- [ ] Build command: `python freeze.py` (set in `netlify.toml`)
- [ ] Publish directory: `build/`
- [ ] Python version: 3.11 (set in `netlify.toml`)
- [ ] API routes redirect to 404 on Netlify (API runs on separate backend)
- [ ] `_headers` file provides security headers + aggressive caching
- [ ] Custom domain configured with HTTPS
- [ ] `skip_processing = true` set (prevents Netlify from breaking bundled assets)

Frozen pages: `/`, `/dashboard`, `/field`, `/network`, `/ask`, `/guide`, `/protocol`, `/status`, `/treasury`

---

## 5. Environment Variables — Complete Reference

| Variable | Required | Purpose |
|----------|----------|---------|
| `HELIOS_SECRET_KEY` | **YES** | Flask session signing. Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `HELIOS_DATABASE_URL` | Production | PostgreSQL connection string. Omit for SQLite dev mode |
| `STRIPE_SECRET_KEY` | For payments | Stripe API secret key |
| `STRIPE_PUBLIC_KEY` | For payments | Stripe publishable key |
| `STRIPE_WEBHOOK_SECRET` | For payments | Stripe webhook signing secret |
| `XAMAN_API_KEY` | For mobile | Xaman/XUMM API key |
| `XAMAN_API_SECRET` | For mobile | Xaman/XUMM API secret |
| `HELIOS_XRPL_WALLET` | For XRPL | Issuer wallet address |
| `HELIOS_XRPL_SECRET` | For XRPL | Issuer wallet seed |
| `HELIOS_XRPL_TREASURY_WALLET` | For XRPL | Treasury wallet address |
| `HELIOS_XRPL_TREASURY_SECRET` | For XRPL | Treasury wallet seed |
| `HELIOS_XRPL_ENABLE_SUBMIT` | For XRPL | `true` to enable live transactions |
| `OPENAI_API_KEY` | For AI | OpenAI API key |
| `TWILIO_SID` | Optional | Twilio account SID for SMS |
| `TWILIO_AUTH_TOKEN` | Optional | Twilio auth token |
| `TWILIO_PHONE` | Optional | Twilio phone number |
| `SENTRY_DSN` | Recommended | Sentry error tracking DSN |
| `REDIS_URL` | Optional | Redis for Celery task queue |

---

## 6. Security Hardening

- [ ] `HELIOS_SECRET_KEY` is a unique 64+ character random string
- [ ] `.env` file is in `.gitignore` (NEVER committed)
- [ ] XRPL wallet seeds stored in secret manager (not plain `.env`) for production
- [ ] Stripe webhook endpoint validates signatures (`STRIPE_WEBHOOK_SECRET`)
- [ ] All API endpoints behind Flask-Limiter (configured in `app.py`)
- [ ] Anti-fraud middleware active on node telemetry routes
- [ ] CORS restricted to frontend domain only
- [ ] `_headers` security headers deployed (X-Frame-Options: DENY, nosniff, XSS protection)
- [ ] Recovery phrases generated server-side but NEVER stored — client responsibility

---

## 7. Monitoring & Observability

- [ ] Sentry SDK: Already in `requirements.txt` (`sentry-sdk[flask]>=2.14`)
- [ ] Set `SENTRY_DSN` in `.env` — captures all unhandled exceptions
- [ ] Health endpoint: `GET /api/infra/health` — use for uptime monitoring
- [ ] Readiness endpoint: `GET /api/infra/readiness` — shows all provider statuses
- [ ] Metrics endpoint: `GET /api/metrics/all` — SR metrics (RRR, flow efficiency, churn, velocity)
- [ ] Set up alerts:
  - RRR < 1.5 (warning) / < 1.0 (critical)
  - Flow efficiency < 0.90
  - Churn > 5%
  - Any 500 errors in Sentry

---

## 8. XRPL Issuance Policy

Before mainnet launch, define and document:

- [ ] Token currency code: `HLS` (3-char, already set in config)
- [ ] Total supply hard cap: 100,000,000 HLS
- [ ] Phase 1 price: $0.05/HLS
- [ ] Issuer wallet is cold storage (signs issuance only, no hot operations)
- [ ] Treasury wallet handles day-to-day operations
- [ ] TrustLine setup automated via `XRPLBridge.submit_trustset()`
- [ ] NFT minting for certificates via `XRPLBridge.mint_nft()`
- [ ] All XRPL transactions logged to `VaultReceipt` model

---

## 9. Pre-Launch Smoke Test

Run the built-in verification script:

```bash
python _verify_client_ready.py
```

All 12 steps must pass:
1. Health check
2. Token verification (100M supply)
3. Energy conservation (balanced)
4. Infrastructure readiness
5. Metrics snapshot
6. Identity creation
7. Duplicate identity rejection
8. Link formation
9. Energy injection
10. Wallet balance check
11. Funding catalog (11 offers)
12. Final field stats

---

## 10. Go-Live Sequence

Execute in this exact order:

```
1. Provision PostgreSQL → set HELIOS_DATABASE_URL
2. Generate mainnet XRPL wallets → update .env
3. Set Stripe live keys → update .env
4. Set Xaman production credentials → update .env
5. Generate strong HELIOS_SECRET_KEY → update .env
6. Deploy backend (waitress/gunicorn behind reverse proxy)
7. Run: python _verify_client_ready.py
8. Deploy frontend: git push → Netlify auto-builds via freeze.py
9. Verify: GET /api/infra/readiness → all providers ready=true
10. Onboard first client using CLIENT_ONBOARDING_FLOW.md
```

---

## Current Status (as of session)

| Component | Status | Action |
|-----------|--------|--------|
| Flask app | Running | No action |
| SQLite DB | Working (dev) | Migrate to PostgreSQL for production |
| XRPL testnet | **LIVE** | Generate mainnet wallets for production |
| Stripe | Package installed, keys missing | Register + add keys |
| Xaman | Code wired, keys missing | Register + add keys |
| Sentry | Package in requirements.txt | Set DSN |
| Link formation | Fixed (was 500, now 201) | No action |
| Validation | 9 schemas active | No action |
| 12-step test | All passing | Re-run after each change |
| Frontend | 9 pages freeze correctly | Deploy to Netlify |

---

## Git Remotes

| Remote | URL | Purpose |
|--------|-----|---------|
| `origin` | FTHTrading/Helios | Main repo |
| `launch` | FTHTrading/Helios-launch | Production deployment |
