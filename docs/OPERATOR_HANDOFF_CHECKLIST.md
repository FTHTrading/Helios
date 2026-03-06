# Operator Handoff Checklist

This is the exact first-run checklist for the incoming operators.

## GitHub setup

- [ ] set repository description
- [ ] set repository website
- [ ] set repository topics
- [ ] confirm README is visible
- [ ] confirm MIT license is visible
- [ ] confirm Code of Conduct is visible
- [ ] confirm Contributing is visible
- [ ] confirm Security policy is visible
- [ ] enable branch protection on `main`
- [ ] enable secret scanning and push protection
- [ ] require CI to pass before merge

## Build protection

- [ ] set `HELIOS_WATERMARK_MODE=hidden`
- [ ] set `HELIOS_BUILD_ID`
- [ ] set `HELIOS_BUILD_WATERMARK`
- [ ] set `HELIOS_LAUNCH_KEY`
- [ ] set `HELIOS_DEPLOYMENT_ROUTE=simplified`

## Environment setup

- [ ] set `HELIOS_DATABASE_URL` to Postgres
- [ ] set `HELIOS_STRIPE_SECRET_KEY`
- [ ] set `HELIOS_STRIPE_PUBLISHABLE_KEY`
- [ ] set `HELIOS_STRIPE_WEBHOOK_SECRET`
- [ ] set `HELIOS_XAMAN_API_KEY`
- [ ] set `HELIOS_XAMAN_API_SECRET`
- [ ] set `HELIOS_XRPL_ISSUER_WALLET`
- [ ] set `HELIOS_XRPL_ISSUER_SECRET`
- [ ] set `HELIOS_XRPL_TREASURY_WALLET`
- [ ] set `HELIOS_XRPL_TREASURY_SECRET`
- [ ] set `HELIOS_XRPL_ENABLE_SUBMIT=true`

## Validation

- [ ] `/health` returns `200`
- [ ] `/api/infra/build` returns build fingerprint
- [ ] `/api/infra/readiness` reflects configured providers
- [ ] `/api/funding/catalog` returns expected offers
- [ ] `/activate` loads correctly
- [ ] `/web3` loads correctly
- [ ] Stripe checkout creation succeeds
- [ ] Xaman payload creation succeeds
- [ ] trustline flow succeeds on testnet

## Launch decision

- [ ] confirm Route B is the chosen default
- [ ] document any reason for using Route C instead
- [ ] defer Redis/Celery unless transaction load requires it immediately

## Before public launch

- [ ] test complete user activation journey
- [ ] test webhook fulfillment path
- [ ] verify hidden watermark mode is active
- [ ] verify secret values are not committed
- [ ] verify branch protections are live
- [ ] verify CI is required on pull requests

## After launch

- [ ] monitor readiness and error surfaces
- [ ] review failed checkouts and payload issues
- [ ] schedule phase-2 hardening items
- [ ] plan Redis/Celery, refunds, and security audit work