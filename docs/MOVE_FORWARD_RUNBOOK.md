# Move Forward Runbook

This runbook is the full execution path for taking Helios from repository handoff to active launch readiness.

## Phase 0 — Establish source of truth

Read in this order:

1. [docs/FINAL_RECOMMENDATION.md](docs/FINAL_RECOMMENDATION.md)
2. [docs/TAKEOVER_START_HERE.md](docs/TAKEOVER_START_HERE.md)
3. [docs/GITHUB_HANDOFF_CHECKLIST.md](docs/GITHUB_HANDOFF_CHECKLIST.md)
4. [docs/BUILD_ROUTE_OPTIONS.md](docs/BUILD_ROUTE_OPTIONS.md)
5. [docs/OPERATOR_HANDOFF_CHECKLIST.md](docs/OPERATOR_HANDOFF_CHECKLIST.md)

## Phase 1 — GitHub setup

Apply the repository settings exactly:

- set About description
- set website
- set topics
- verify README / MIT / Contributing / Code of Conduct / Security Policy are visible
- enable branch protection for `main`
- require CI checks
- enable secret scanning and push protection

Reference:
- [docs/GITHUB_HANDOFF_CHECKLIST.md](docs/GITHUB_HANDOFF_CHECKLIST.md)
- [docs/REPOSITORY_PROTECTIONS.md](docs/REPOSITORY_PROTECTIONS.md)

## Phase 2 — Route decision

Default route:

- Route B — Simplified launch route

Reference:
- [docs/BUILD_ROUTE_OPTIONS.md](docs/BUILD_ROUTE_OPTIONS.md)
- [docs/HELIOS_SIMPLIFIED_OPTION.md](docs/HELIOS_SIMPLIFIED_OPTION.md)

## Phase 3 — Protection and attribution

Set build protection values:

- `HELIOS_WATERMARK_MODE=hidden`
- `HELIOS_BUILD_ID`
- `HELIOS_BUILD_WATERMARK`
- `HELIOS_LAUNCH_KEY`
- `HELIOS_DEPLOYMENT_ROUTE=simplified`
- `HELIOS_BUILD_OWNER`

Verify:

- `/api/infra/build`

## Phase 4 — Environment and infrastructure

Required environment group:

- Postgres database URL
- Stripe secret key
- Stripe publishable key
- Stripe webhook secret
- Xaman API key
- Xaman API secret
- XRPL issuer wallet
- XRPL issuer secret
- XRPL treasury wallet
- XRPL treasury secret
- `HELIOS_XRPL_ENABLE_SUBMIT=true`

Optional at launch:

- Pinata credentials
- Sentry DSN

## Phase 5 — Product validation

The team must validate:

- `/health`
- `/api/infra/build`
- `/api/infra/readiness`
- `/api/funding/catalog`
- `/activate`
- `/web3`

Then validate real flows:

- Stripe checkout creation
- Stripe webhook fulfillment
- Xaman sign-in payload
- XRPL trustline flow
- full onboarding continuation to dashboard

## Phase 6 — Public messaging alignment

Before launch, normalize public messaging.

Reference:
- [docs/PAGE_ALIGNMENT_MEMO.md](docs/PAGE_ALIGNMENT_MEMO.md)

Rules:

- keep institutional tone
- remove unsupported live metrics
- avoid absolute claims about deterministic infrastructure unless verified
- avoid claiming active dual-chain production unless actually deployed

## Phase 7 — Launch go/no-go checklist

Go only when these are true:

- GitHub protections active
- hidden watermark mode active
- production env vars set
- Postgres configured
- checkout succeeds
- wallet connect succeeds
- trustline succeeds
- readiness output matches expected launch state
- public copy has been aligned to verified capabilities

## Phase 8 — Phase 2 after launch

After launch, the next items are:

- Redis/Celery
- refund workflow
- encryption hardening
- security audit
- deployment automation
- expanded operator tooling

## Exact default instruction to the team

> Use Route B, keep watermark mode hidden, align the public page to verified repo truth, move to Postgres, connect Stripe/Xaman/XRPL, validate the full activation journey, and only then move toward the larger architecture.