# Helios Launch Blueprint

## 1. What this repository is

Helios is now structured as an XRPL-first membership platform with these system rails:

- onboarding and activation pages
- funding catalog and checkout orchestration
- Xaman wallet sign-in and trustline flows
- XRPL issuance bridge
- IPFS evidence path for treasury records
- operational readiness reporting

## 2. Production architecture

```text
User
  ↓
Cloudflare
  ↓
Flask / Gunicorn
  ├─ onboarding pages
  ├─ API routes
  ├─ Stripe webhook handling
  ├─ Xaman payload generation
  ├─ XRPL issuance orchestration
  └─ treasury/IPFS evidence operations
  ↓
Postgres
  ↓
Redis / Celery
  ↓
Stripe + XRPL + Xaman + Pinata
```

## 3. Build answer for stakeholders

### Green
- frontend onboarding journey exists
- backend funding and wallet APIs exist
- readiness reporting exists
- payment event persistence exists
- repo can be open, forkable, and MIT-licensed

### Yellow
- Stripe requires live keys
- XRPL requires funded issuer/treasury wallets
- Xaman requires live API credentials
- IPFS requires Pinata credentials

### Red
- SQLite should not be used for production
- async workers are not fully wired yet
- no full production deployment automation yet

## 4. Recommended launch stack

- Cloudflare
- Flask + Gunicorn
- Postgres
- Redis
- Stripe
- XRPL
- Xaman
- Pinata/IPFS
- Sentry

## 5. One-to-two day production sequence

### Day 1
- provision Postgres
- provision Redis
- set `.env` from `.env.example`
- install Stripe live keys and webhook secret
- install Xaman credentials
- install Pinata credentials
- set XRPL issuer and treasury wallets

### Day 2
- deploy app
- verify `/api/infra/readiness`
- run checkout test
- run Xaman sign-in test
- run trustline test
- run webhook fulfillment test
- turn on Cloudflare protections

## 6. Required environment groups

### Core
- `HELIOS_SECRET_KEY`
- `HELIOS_DATABASE_URL`
- `HELIOS_DEBUG=false`

### XRPL
- `HELIOS_XRPL_NETWORK`
- `HELIOS_XRPL_ENABLE_SUBMIT=true`
- `HELIOS_XRPL_ISSUER_WALLET`
- `HELIOS_XRPL_ISSUER_SECRET`
- `HELIOS_XRPL_TREASURY_WALLET`
- `HELIOS_XRPL_TREASURY_SECRET`

### Stripe
- `HELIOS_STRIPE_SECRET_KEY`
- `HELIOS_STRIPE_PUBLISHABLE_KEY`
- `HELIOS_STRIPE_WEBHOOK_SECRET`

### Wallet
- `HELIOS_XAMAN_API_KEY`
- `HELIOS_XAMAN_API_SECRET`

### Ops
- `HELIOS_REDIS_URL`
- `HELIOS_SENTRY_DSN`

## 7. Forkability and repo maturity

This repo is now prepared to be a public engineering repo by including:
- MIT license
- contributing guide
- security policy
- code of conduct
- CODEOWNERS
- PR/issue templates
- CI workflow
- Dependabot config
- documented protections

## 8. Final engineering position

This is no longer just a demo repo.

It is a senior-engineered launch repository with:
- product lifecycle wiring
- provider readiness surfacing
- production documentation
- governance/community repo controls

The remaining work is primarily **credential activation and infrastructure promotion**, not a ground-up rebuild.
