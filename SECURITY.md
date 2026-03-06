# Security Policy

## Supported branch

- `main` — active branch

## Reporting a vulnerability

Please do not open public issues for security findings.

Send a private report with:
- affected file or endpoint
- reproduction steps
- impact assessment
- suggested fix, if available

Recommended initial SLA:
- acknowledgement: 1 business day
- triage: 3 business days
- remediation target: 14 business days for critical findings

## Current security posture

This repository includes:
- request validation
- rate limiting support
- Sentry hooks
- hybrid-mode safety fallbacks for incomplete provider setup

Before production launch, require:
- Postgres instead of SQLite
- managed secrets
- Stripe webhook secret validation
- funded XRPL issuer/treasury wallets
- Redis-backed queueing
- third-party security review
