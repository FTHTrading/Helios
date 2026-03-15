# Support

## Operational docs

Start here:
- `docs/HELIOS_LAUNCH_BLUEPRINT.md`
- `docs/HELIOS_REVIEW_RESPONSE.md`
- `docs/REPOSITORY_PROTECTIONS.md`
- `docs/PUSH_TO_HELIOS_LAUNCH.md`

## Runtime checks

Key health surfaces:
- `/health`
- `/api/infra/status`
- `/api/infra/readiness`
- `/api/funding/catalog`

## Optional production enhancements

The system launches in hybrid mode. These upgrade to full production mode when added:

- Postgres (recommended for scale)
- Stripe live keys (optional — enables fiat payments)
- Xaman credentials (optional — enables wallet sign-in)
- XRPL issuer + treasury wallets (optional — enables on-chain settlement)
- Pinata credentials (optional — enables IPFS evidence pinning)
- Redis (optional — enables background task processing)
