# Takeover Start Here

This is the first document the incoming build-and-launch team should read.

## The short answer

If the goal is to get Helios live without carrying unnecessary complexity on day 1, use:

- **Route B — Simplified launch route**

See [docs/BUILD_ROUTE_OPTIONS.md](docs/BUILD_ROUTE_OPTIONS.md).

## The first five things to do

1. Apply the GitHub settings in [docs/GITHUB_HANDOFF_CHECKLIST.md](docs/GITHUB_HANDOFF_CHECKLIST.md)
2. Set `HELIOS_WATERMARK_MODE=hidden`
3. Move to Postgres
4. Add live Stripe + Xaman + XRPL credentials
5. Run readiness checks and smoke tests before public launch

## The right reading order

1. [docs/TAKEOVER_START_HERE.md](docs/TAKEOVER_START_HERE.md)
2. [docs/GITHUB_HANDOFF_CHECKLIST.md](docs/GITHUB_HANDOFF_CHECKLIST.md)
3. [docs/BUILD_ROUTE_OPTIONS.md](docs/BUILD_ROUTE_OPTIONS.md)
4. [docs/HELIOS_SIMPLIFIED_OPTION.md](docs/HELIOS_SIMPLIFIED_OPTION.md)
5. [docs/HELIOS_DIRECT_RESPONSE_TO_REVIEW.md](docs/HELIOS_DIRECT_RESPONSE_TO_REVIEW.md)
6. [docs/HELIOS_LAUNCH_BLUEPRINT.md](docs/HELIOS_LAUNCH_BLUEPRINT.md)

## The default launch recommendation

Use this stack first:

- Postgres
- Stripe
- Xaman
- XRPL
- Flask
- Cloudflare

Defer until phase 2 unless required:

- Redis/Celery
- Coinbase Commerce
- WalletConnect
- Prometheus/Grafana
- advanced operator tooling

## What success looks like

Before launch, the team should be able to prove:

- `/api/infra/readiness` returns the expected provider state
- `/api/infra/build` returns the embedded build fingerprint
- checkout can be created successfully
- Xaman sign-in works
- trustline flow works
- activation flow completes without fallback errors

## Protection default

Keep the protection quiet:

- `HELIOS_WATERMARK_MODE=hidden`

That preserves attribution without visibly exposing build labels on the public interface.

## Final guidance

Do not overbuild day 1.

Launch the simplified route first, validate it, then expand into the fuller architecture only after the launch path is stable.