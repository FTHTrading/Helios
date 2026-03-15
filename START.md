# START

If you are the incoming Helios build-and-launch team, start here.

## Use this route

- **Route B — Simplified launch route**

Do not start with the full architecture unless there is a clear operational reason.

## Read in this exact order

1. [docs/FINAL_RECOMMENDATION.md](docs/FINAL_RECOMMENDATION.md)
2. [docs/MOVE_FORWARD_RUNBOOK.md](docs/MOVE_FORWARD_RUNBOOK.md)
3. [docs/TAKEOVER_START_HERE.md](docs/TAKEOVER_START_HERE.md)
4. [docs/OPERATOR_HANDOFF_CHECKLIST.md](docs/OPERATOR_HANDOFF_CHECKLIST.md)
5. [docs/GITHUB_HANDOFF_CHECKLIST.md](docs/GITHUB_HANDOFF_CHECKLIST.md)

## Default settings

- `HELIOS_WATERMARK_MODE=hidden`
- deployment route: `simplified`
- source of truth: repository docs, not older marketing pages

## The stack to launch first

- Flask
- Postgres
- Stripe
- Xaman
- XRPL
- Cloudflare

## Do not block launch on these

Unless truly required, defer:

- Redis/Celery
- Coinbase Commerce
- WalletConnect
- Prometheus/Grafana
- advanced operator tooling

## Success condition

Before public launch, prove:

- `/api/infra/build` works
- `/api/infra/readiness` matches expected state
- `/api/infra/launch-readiness` shows status "ready" with optional enhancements listed
- `/api/handoff/manifest` exposes the mirrored docs and GitHub refs
- `/ask` returns build-aware answers with references
- checkout works
- wallet connect works
- trustline works
- activation flow completes end to end

## Quick validation command

- run `python verify_launch.py`

## One-line instruction

> Launch the simplified route first, keep protection hidden, align public claims to verified deployment truth, and expand only after the first stable launch path is working.