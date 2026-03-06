# Build Route Options

This document gives the takeover team clear route options without forcing one architecture on day 1.

## Route A — Minimal validation route

Use when the team only wants to validate market demand and onboarding motion.

Stack:
- Flask
- Postgres
- Stripe
- Xaman
- XRPL testnet first

Includes:
- identity creation
- activation selection
- checkout
- wallet connection
- trustline flow
- status page

Defers:
- Redis/Celery
- Pinata/IPFS
- expanded operator tooling
- advanced observability

## Route B — Simplified launch route

Use when the team wants a real launch with low operational complexity.

Stack:
- Flask
- Postgres
- Stripe
- Xaman
- XRPL
- Cloudflare
- optional Pinata

Includes:
- real activation flow
- XRPL wallet onboarding
- readiness checks
- treasury evidence path if needed

Best default route.

## Route C — Full launch route

Use when the team is ready for the broader platform architecture.

Stack:
- Flask
- Postgres
- Redis/Celery
- Stripe
- Xaman
- XRPL
- Pinata/IPFS
- Cloudflare
- Sentry

Includes:
- full launch base
- payment event history
- provider readiness reporting
- broader launch operations foundation

## Decision guidance

Choose Route A if:
- speed matters most
- the goal is validation

Choose Route B if:
- the goal is launch
- the team wants lower complexity

Choose Route C if:
- the team wants the full engineering base from the start
- the team can support more infrastructure immediately

## Watermarking for future launches

Use these environment variables for every future launch package:

- `HELIOS_BUILD_ID`
- `HELIOS_BUILD_WATERMARK`
- `HELIOS_LAUNCH_KEY`
- `HELIOS_DEPLOYMENT_ROUTE`
- `HELIOS_BUILD_OWNER`

These values surface in:
- HTML meta tags
- response headers
- footer watermark
- on-screen watermark badge
- build manifest API

This allows every future launch to be attributed, tracked, and differentiated.