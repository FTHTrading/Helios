# Page Alignment Memo

This memo compares the original Helios public page at `helios-institutional-m3qk.bolt.host` with the current launch repository and explains what copy should stay, what should be softened, and what should be removed until production proof exists.

## Source-of-truth rule

For launch operations, the repository is the source of truth.

Use the original page as:
- brand direction
- tone reference
- product vision reference

Do not use it as the final source of truth for live infrastructure claims unless those claims are verified in the active deployment.

## High-level conclusion

The page is **visionally aligned** but **operationally ahead of the current verified repo state**.

That means:
- the page is useful
- the page is not unusable
- the page should be normalized before being treated as official production truth

## Copy categories

### Keep as-is

These claims are directionally aligned with the current build and can remain with little or no change:

- gold-backed certificate concept
- XRPL as the primary chain direction
- custody and verification framing
- activation / treasury / protocol navigation structure
- institutional tone and non-retail positioning

## Soften or qualify

These claims should remain, but with more careful wording.

### 1. On-chain issuance

Current page language implies fully live deterministic production settlement.

Recommended wording:

> Certificates are designed for XRPL-issued settlement and verification. Launch configuration determines whether the environment is operating in staged, testnet, or live production mode.

Reason:
- the repo supports XRPL execution paths, but live mode depends on credentials and infrastructure activation

### 2. Sovereign settlement / live infrastructure

Current page language is too strong if the deployment is not fully verified.

Recommended wording:

> Settlement is routed through the Helios launch infrastructure, with production readiness depending on configured providers, funded wallets, and active deployment settings.

Reason:
- avoids overstating live operational certainty

### 3. Verification, not trust

This can remain, but the proof claims should be tied to active deployment state.

Recommended wording:

> Helios is built to support public verification of issuance, treasury evidence, and settlement records across its configured ledger and evidence systems.

Reason:
- avoids claiming all verification rails are live before they are tested and deployed

## Remove or defer until verified

These claims are the main conflict points.

### 1. “9 funded wallets”

Remove unless operationally proven in the current deployment.

Reason:
- this is a concrete live infrastructure claim
- it must be verifiable if shown publicly

### 2. “97.4% on-chain success rate”

Remove unless backed by a real production reporting source.

Reason:
- this is a performance metric claim
- it can create credibility and disclosure problems if not evidenced

### 3. “XRPL Mainnet · Stellar Public” as active production statement

Do not present both as active production rails unless the actual launch environment is configured and tested that way.

Recommended replacement:

> XRPL-first launch architecture with optional secondary attestation rails as configured by deployment.

### 4. “No human discretion at any settlement layer”

Defer until the actual settlement workflow, access controls, and compliance controls are fully verified.

Reason:
- this is too absolute for the current repo posture

### 5. “Stablecoin held in escrow”

Remove unless an actual escrow and custody implementation is active.

Reason:
- this can imply a regulated or legally significant funds-control arrangement

## Recommended replacement posture

Use this as the public operational stance:

> Helios is an XRPL-first certificate and activation platform with treasury evidence, wallet onboarding, and payment flows designed for staged launch and production promotion as providers are activated.

## Section-by-section guidance

### Hero section

Keep:
- Helios branding
- gold-backed digital certificates
- physically custodied framing

Change:
- replace “settled on sovereign infrastructure” with a softer version such as:
  - `structured for sovereign-style verification and staged launch settlement`

### “What is Helios?”

Keep most of it.

Change any sentence that implies already-proven live production execution if that has not been confirmed in the current deployment.

### “How Issuance Works”

Good structure, but several lines need qualification.

Safer replacements:
- “USD converts to USDC via regulated on-ramp” → only keep if this flow actually exists in the active stack
- “vaulted through certified vault custody network” → keep only if the custody relationship is real and current
- “anchored to XRPL and Stellar” → change to “anchored to configured settlement and evidence rails” unless Stellar is truly active in launch scope

### “Verification, Not Trust”

Keep the theme.

Replace absolute claims with deployment-aware wording.

### “Built on OPTKAS”

This is the highest-risk section if not fully verified.

Recommendation:
- either remove it entirely for launch
- or convert it into a future-state / infrastructure-partner note without hard live metrics

## Final recommendation

### Best operational path

1. Keep the institutional visual tone
2. Keep the certificate / treasury / XRPL narrative
3. remove unsupported live metrics and absolute claims
4. align public messaging to the current repo truth
5. use [docs/HELIOS_SIMPLIFIED_OPTION.md](docs/HELIOS_SIMPLIFIED_OPTION.md) as the day-1 operational posture

### Short answer to the team

> The original page is usable as a brand and structure reference, but it should be edited so the public claims match the launch repository’s real deployment state. Keep the vision, soften the operational claims, and remove any live metrics or dual-chain assertions that are not currently verified.