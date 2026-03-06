# Contributing

## Branching

- branch from `main`
- use short topic branches: `feat/...`, `fix/...`, `docs/...`
- keep pull requests focused

## Required for pull requests

- explain the problem
- explain the change
- note user impact
- include validation steps
- update docs for new env vars, routes, or workflows

## Engineering rules

- prefer XRPL-first implementations for on-chain features
- preserve hybrid-mode fallbacks when live credentials are missing
- do not hardcode secrets
- add validation for new write endpoints
- keep UI and API states honest; avoid fake "live" claims

## Validation

At minimum, run:
- dependency install
- Flask smoke checks
- changed-route sanity checks

## Documentation

If a change affects launch readiness, also update:
- `README.md`
- `docs/HELIOS_LAUNCH_BLUEPRINT.md`
- `docs/HELIOS_REVIEW_RESPONSE.md`
