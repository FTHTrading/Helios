# Helios White Paper

## Executive summary

Helios is an XRPL-first launch system for activation, wallet orchestration, treasury evidence, and certificate-ready issuance.

It should be understood as a senior-engineered launch repository rather than a speculative concept document. The repository already contains working application structure, operator documentation, build fingerprinting, readiness reporting, a site-based handoff portal, and a source-grounded AI advisory layer.

The correct current posture is:

> a launch-structured, hybrid-capable repository with real provider rails present, but with live provider activation and infrastructure promotion still required for full production confidence

This distinction matters. Helios is no longer only describing a system. It is implementing one.

## Document scope

This white paper covers:

- what Helios is in its current build state
- the intended launch architecture
- the token, certificate, treasury, and operator model
- the route to production
- the difference between implemented rails and live-provider completion
- the governance and documentation posture required for responsible rollout

This document does not claim that every provider is already live in production. It describes the system truthfully as built and as intended for staged launch.

## System objective

Helios is designed to provide a controlled launch environment for:

- onboarding and activation
- checkout and payment orchestration
- wallet identity and trustline preparation
- XRPL-issued token operations
- certificate and treasury evidence pathways
- public build verification and operator handoff

The system goal is operational clarity.

That means:

- a bounded launch route
- explicit provider responsibilities
- verifiable build state
- no dependency on hidden administrative storytelling
- public claims that follow the actual deployment truth

## What Helios is

Helios combines four operating layers.

### 1. Activation and onboarding layer

This layer handles:

- visitor onboarding
- offer selection
- checkout creation
- continuation through activation
- handoff from a pre-activation state into a wallet-aware launch flow

### 2. Wallet and token layer

This layer handles:

- Xaman sign-in and payload generation
- XRPL trustline preparation
- issued-token launch posture for `HLS`
- certificate alignment toward XRPL `XLS-20`

### 3. Treasury and evidence layer

This layer handles:

- reserve receipt capture
- treasury evidence persistence
- optional IPFS compatibility
- anchoring posture
- public readiness and verification surfaces

### 4. Operations and governance layer

This layer handles:

- build fingerprinting
- hidden watermark controls
- deployment route labeling
- mirrored handoff documents
- GitHub references
- operator checklists and rebuttal materials
- AI-assisted question handling from the actual build truth

## Current launch posture

Helios should be launched using the simplified route first.

That means the recommended starting stack is:

- Flask application layer
- Postgres production database
- Stripe for payment orchestration
- Xaman for wallet payload signing
- XRPL for token and certificate rails
- Cloudflare for edge, DNS, and front-door controls

Optional at initial launch:

- Pinata/IPFS for evidence pinning
- Sentry for error capture

Explicitly deferred unless justified by real load or commercial need:

- Redis/Celery
- WalletConnect
- Coinbase Commerce
- advanced operator tooling
- expanded observability stacks beyond immediate launch need

## Architecture

```text
User
  ↓
Cloudflare
  ↓
Flask / Gunicorn
  ├─ Pages and activation UX
  ├─ API routes
  ├─ Funding orchestration
  ├─ Wallet payload creation
  ├─ XRPL issuance / trustline / anchoring rails
  ├─ Handoff portal and mirrored docs
  └─ Readiness and build manifest reporting
  ↓
Postgres
  ↓
Provider integrations
  ├─ Stripe
  ├─ Xaman
  ├─ XRPL
  ├─ Cloudflare
  └─ Pinata/IPFS (optional)
```

## Deployment modes

Helios should be understood in three states.

### 1. Documentation-complete

The repository contains the intended architecture, route guidance, operator steps, and launch posture.

### 2. Hybrid-capable

The repository includes real provider integration points and launch rails, but some production providers may not yet be activated.

### 3. Production-promoted

Live credentials, funded wallets, production infrastructure, and validated operational paths have been promoted and verified.

The current repository fits state two more than state three.

## Core system surfaces

### Public product routes

- `/`
- `/join`
- `/activate`
- `/web3`
- `/dashboard`
- `/status`
- `/launch`
- `/tokenomics`
- `/treasury`
- `/certificates`
- `/ask`

### Build and readiness routes

- `/health`
- `/api/infra/build`
- `/api/infra/readiness`
- `/api/funding/catalog`

### Handoff and retrieval routes

- `/handoff`
- `/start`
- `/handoff/docs/<slug>`
- `/handoff/docs/<slug>/raw`
- `/handoff/docs/<slug>/download`
- `/api/handoff/manifest`
- `/api/handoff/docs`
- `/api/handoff/docs/<slug>`

## Product flow

The intended user path is:

1. visitor lands on the site
2. visitor selects an activation path
3. system creates checkout intent
4. payment path is created through Stripe
5. wallet payload path is created through Xaman
6. user establishes trustline readiness on XRPL
7. operator and system evidence surfaces are available for downstream treasury and certificate operations

This flow is intentionally staged so launch complexity stays bounded.

## Token model

Helios uses a fixed-supply token posture centered on `HLS`.

Current code-level configuration establishes:

- token name: `HELIOS`
- token symbol: `HLS`
- total supply: `100,000,000`
- fixed-supply public posture
- founder lock controls
- reserve and pool allocations in configuration

The recommended public framing is not speculative. It is operational:

> HLS is a fixed-supply XRPL-first protocol asset intended for controlled rollout, activation-aligned utility, wallet participation, and future platform functions.

## Certificate model

Certificates are positioned as XRPL `XLS-20` assets linked to treasury and evidence rails.

The repository supports the certificate direction through:

- certificate route structure
- issuance posture in launch documentation
- treasury evidence compatibility
- trustline and XRPL alignment

The truthful production statement is:

- the certificate path exists in the build
- the evidence path exists in the build
- live provider completion is still required for verified production issuance

## Treasury model

The treasury model is based on evidence-first operator discipline.

The repository supports:

- reserve receipt capture
- proof-oriented data structure
- optional IPFS pinning path
- anchoring posture
- public readiness surfaces

The repository does not justify exaggerated claims about live, real-time reserve proof unless the live workflow has been activated and validated in production.

## Data and persistence model

Helios currently uses SQLite locally and should use Postgres in production.

Production posture requires:

- Postgres promotion
- validated migrations and data persistence behavior
- payment event persistence verification
- wallet and funding state continuity

The production database is not optional for a serious launch posture.

## Provider model

### Stripe

Stripe is the recommended primary payment rail for launch.

It is responsible for:

- checkout session creation
- hosted payment path
- webhook completion
- payment event persistence

### Xaman

Xaman is the recommended wallet provider for launch.

It is responsible for:

- sign-in payload flow
- wallet confirmation path
- trustline-related launch interactions

### XRPL

XRPL is the primary chain posture.

It is responsible for:

- issued fungible token path
- trustline model
- certificate positioning
- anchoring posture

### Cloudflare

Cloudflare is the recommended front-door infrastructure posture.

It is responsible for:

- DNS
- SSL
- CDN posture
- basic edge protection

### Pinata/IPFS

Pinata/IPFS remains optional for launch.

It provides:

- externalized evidence pinning
- optional treasury bundle references

## Security and ownership controls

Helios includes build-identity controls:

- `HELIOS_BUILD_ID`
- `HELIOS_BUILD_WATERMARK`
- `HELIOS_LAUNCH_KEY`
- `HELIOS_DEPLOYMENT_ROUTE`
- `HELIOS_BUILD_OWNER`
- `HELIOS_WATERMARK_MODE`

Recommended default:

- `HELIOS_WATERMARK_MODE=hidden`

The purpose of these controls is not marketing. It is launch provenance and operator accountability.

## Documentation and handoff model

Helios includes a mirrored handoff portal so operators can retrieve the essential system material without needing unrestricted repository access.

That handoff model includes:

- white paper
- operator guide
- tokenomics guide
- rebuttal material
- route decision documents
- handoff checklists
- GitHub references

This directly supports takeover, diligence, and future operator continuity.

## AI and knowledge model

Helios includes an Ask Helios layer.

Its intended behavior is:

- answer from repository truth first
- prefer mirrored docs and code-grounded references
- incorporate rebuttal and launch material
- expose references for operator review
- avoid unsupported certainty

This is an operator support layer, not a fictional narrative layer.

## Governance and launch discipline

Helios should be operated as a controlled production rollout.

That means:

- branch protection on `main`
- CI required for merge
- secret scanning and push protection enabled
- production secrets stored outside code
- route choice documented explicitly
- public statements aligned to verified live capability

## What remains before full production confidence

The following items remain necessary for full production confidence:

- production Postgres promotion
- live Stripe credentials and webhook verification
- live Xaman credentials and payload validation
- funded XRPL issuer and treasury wallets
- optional IPFS credentials if evidence pinning is required at launch
- refund and support policy completion
- security hardening
- formal audit and launch runbook sign-off

## What Helios should not claim yet

Helios should not claim, unless verified live:

- that all providers are already activated in production
- that reserve proof is real-time and externally complete
- that dual-chain production is active
- that valuation, demand, or future token price is known
- that launch complexity beyond Route B is justified on day one

## Final launch truth statement

The correct launch truth statement remains:

> Helios is a documented, build-ready, XRPL-first launch system with real implementation rails, mirrored operator materials, and source-grounded support tooling, but with live provider activation and infrastructure promotion still required before full-strength public production claims should be made.

## Final position

Helios is no longer only a concept repository.

It is a launch-oriented system with:

- real application structure
- real provider rails
- real operator documentation
- real handoff retrieval surfaces
- a clear and conservative production path

That is the correct senior-engineered interpretation of the current build.
