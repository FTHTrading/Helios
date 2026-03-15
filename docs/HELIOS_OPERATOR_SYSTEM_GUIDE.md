# Helios Operator System Guide

## Purpose

This document is the operator-grade explanation of what exists, what must be configured, and what the incoming launch team is responsible for proving before public rollout.

## System responsibility map

### Product layer

The application currently owns:

- onboarding
- activation journey
- wallet setup flow
- payment orchestration
- readiness display
- handoff and documentation access

### Provider layer

The operator team is responsible for live activation of:

- Stripe
- Xaman
- XRPL
- Cloudflare
- Postgres
- optional Pinata/IPFS

### Governance layer

The operator team is also responsible for:

- repository protections
- secret handling
- release gating
- public messaging accuracy
- go/no-go decision discipline

## Required production environment

### Core

- `HELIOS_SECRET_KEY`
- `HELIOS_DATABASE_URL`
- `HELIOS_DEBUG=false`

### Stripe

- `HELIOS_STRIPE_SECRET_KEY`
- `HELIOS_STRIPE_PUBLISHABLE_KEY`
- `HELIOS_STRIPE_WEBHOOK_SECRET`

### Xaman

- `HELIOS_XAMAN_API_KEY`
- `HELIOS_XAMAN_API_SECRET`

### XRPL

- `HELIOS_XRPL_NETWORK`
- `HELIOS_XRPL_ENABLE_SUBMIT=true`
- `HELIOS_XRPL_ISSUER_WALLET`
- `HELIOS_XRPL_ISSUER_SECRET`
- `HELIOS_XRPL_TREASURY_WALLET`
- `HELIOS_XRPL_TREASURY_SECRET`

### Build protection

- `HELIOS_WATERMARK_MODE=hidden`
- `HELIOS_BUILD_ID`
- `HELIOS_BUILD_WATERMARK`
- `HELIOS_LAUNCH_KEY`
- `HELIOS_DEPLOYMENT_ROUTE=simplified`
- `HELIOS_BUILD_OWNER`

### AI knowledge layer

- `HELIOS_AI_API_KEY`
- `HELIOS_AI_MODEL`

Do not commit any of these values.

## Production route

Use Route B unless there is an explicit reason not to.

That means the operators should launch:

- Flask
- Postgres
- Stripe
- Xaman
- XRPL
- Cloudflare

And explicitly defer:

- Redis/Celery unless load requires it
- secondary payment rails unless commercially required
- secondary wallet rails unless strategically required

## Validation checklist

Operators should not call the system launch-ready until all of the following are true:

### Platform

- `/health` returns `200`
- `/api/infra/build` returns fingerprint and route
- `/api/infra/readiness` returns expected provider state

### Funding

- `/api/funding/catalog` returns expected offers
- checkout session creation succeeds
- Stripe webhook fulfillment succeeds
- payment events persist as expected

### Wallet and XRPL

- `/web3` loads successfully
- Xaman sign-in payload creation succeeds
- trustline flow succeeds
- issuer and treasury addresses are validated in the intended environment

### Documentation and handoff

- `/handoff` loads successfully
- mirrored docs render successfully
- review rebuttal is visible
- operator guide is visible
- tokenomics guide is visible
- GitHub reference links are visible

### AI knowledge system

- Ask Helios answers from build-aware context
- answers can reference mirrored docs
- answers can reference review rebuttal material
- answers can reference GitHub resources

## Messaging rules

Public messaging must follow repository truth.

Operators should:

- keep institutional tone
- avoid unsupported certainty
- avoid dual-chain production claims unless actually deployed
- avoid reserve proof claims beyond what has been activated and verified
- avoid implying that hidden implementation work is already live

## Future questions handling

When stakeholders ask future questions, the operator answer path should be:

1. repository docs
2. handoff portal docs
3. review rebuttal docs
4. code-level references
5. AI-assisted synthesis only after source context is loaded

## Release discipline

No public release should occur unless:

- secrets are stored safely
- CI is active
- push protection is enabled
- branch protection is enabled
- launch route is documented
- operators know exactly what is live vs hybrid vs deferred

## Final instruction

Operate Helios like a controlled production rollout, not a concept demo. The job is to make every public claim match a verified system path.
