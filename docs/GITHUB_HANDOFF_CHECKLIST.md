# GitHub Handoff Checklist

This is the exact GitHub repository setup the takeover team should apply so there is no ambiguity about the correct public-facing configuration.

## 1. About section

Do not leave the repository About section empty.

Use:

- **Description**
  - `XRPL-first launch repository for Helios onboarding, wallet activation, funding, and production rollout.`

- **Website**
  - `https://xxxiii.io`

- **Topics**
  - `xrpl`
  - `xaman`
  - `stripe`
  - `flask`
  - `postgresql`
  - `ipfs`
  - `pinata`
  - `membership-platform`
  - `launch-infrastructure`
  - `fintech`

## 2. Resources section

These should remain enabled and visible:

- Readme
- License
- Code of conduct
- Contributing
- Security policy

Current expected state:

- License: MIT
- Code of conduct: enabled
- Contributing: enabled
- Security policy: enabled

## 3. Repository protections

Apply the settings from [docs/REPOSITORY_PROTECTIONS.md](docs/REPOSITORY_PROTECTIONS.md).

Minimum required:

- protect `main`
- require pull requests
- require 1 approval
- require CI to pass
- enable secret scanning
- enable push protection
- enable dependency alerts

## 4. Which route should they choose?

If the team is unsure, the right default is:

- **Route B — Simplified launch route**

That route is documented in [docs/BUILD_ROUTE_OPTIONS.md](docs/BUILD_ROUTE_OPTIONS.md).

Why this is the right default:

- simpler to operate
- easier to explain
- lower launch risk
- still gives them real checkout, wallet flow, and XRPL activation

Only use the full route immediately if the team is ready to support the added infrastructure from day 1.

## 5. Watermark/privacy default

If public branding should stay quiet, use:

- `HELIOS_WATERMARK_MODE=hidden`

That keeps protection embedded without visible public labels.

## 6. Final handoff answer

If the takeover team asks "which one is the right one?", the short answer is:

> Use the simplified route first, apply the About values above exactly, keep the repo protections on, and leave watermark mode hidden unless there is a reason to expose build labeling publicly.