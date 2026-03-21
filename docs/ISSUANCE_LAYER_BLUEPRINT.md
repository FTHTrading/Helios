# ISSUANCE LAYER BLUEPRINT

**Version:** 1.0  
**Date:** 2025-07-15  
**Status:** DESIGN — Not yet operational  
**Author:** Helios Architecture Team

---

## 1. Purpose

This document defines what a **real issuance layer** looks like for Helios
and draws the line between what exists today and what must be built before
any token, certificate, or NFT can be offered to the public.

> **Core Principle:** Identity and Network Relationships are operational.
> Issuance is scaffolded but NOT live. No token has been minted. No security
> has been issued. No public offering has occurred.

---

## 2. Current State — What Exists

| Component | File | Status | What It Actually Does |
|-----------|------|--------|----------------------|
| Token Engine | `core/token.py` | Scaffolded | Fixed-supply accounting (100M HLS). No minting function. Pool math only. |
| Web3 Issuance | `core/web3_issuance.py` | Simulation | `TokenIssuance`, `CertificateNFT`, `CeremonialNFT` classes. All return simulation/dry-run responses when XRPL SDK not configured. |
| Certificates | `core/certificates.py` | DB-only | HC-NFT lifecycle with SHA-256 deterministic IDs. Mints to database. Not on-chain. |
| XRPL Bridge | `core/xrpl_bridge.py` | Testnet-ready | Wallet creation, TrustLine, Payment, NFTokenMint. Falls back to deterministic dry-run when SDK absent. |
| Treasury | `core/treasury.py` | Accounting | Metal-backed reserve ratio tracking. APMEX integration scaffolded. |

**Bottom line:** All issuance code runs in simulation mode. The database
records issuance events, but nothing touches a real ledger.

---

## 3. Three Modules — Clean Separation

Helios has three distinct operational layers. They must remain independent.

```
┌─────────────────────────────────────────────────────────────────┐
│  MODULE 1 — IDENTITY                         ✅ OPERATIONAL    │
│  Register .helios names, verify phone, create keys             │
│  Files: core/identity.py, core/sms.py, models/member.py       │
├─────────────────────────────────────────────────────────────────┤
│  MODULE 2 — NETWORK RELATIONSHIPS            ✅ OPERATIONAL    │
│  Form links (max 5), dissolve links, propagate energy          │
│  Files: core/network.py, models/link.py, core/energy_exchange  │
├─────────────────────────────────────────────────────────────────┤
│  MODULE 3 — ISSUANCE                         ⬜ SCAFFOLDED     │
│  Token minting, NFT certificates, ceremonial NFTs              │
│  Files: core/token.py, core/web3_issuance.py,                  │
│         core/certificates.py, core/xrpl_bridge.py              │
└─────────────────────────────────────────────────────────────────┘
```

**Module 3 MUST NOT go live until every prerequisite below is met.**

---

## 4. Issuance Prerequisites — Gate Checklist

### 4.1 Legal & Compliance

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| L1 | Legal opinion: Is HLS a security? | ⬜ Not started | Must obtain formal opinion from securities counsel |
| L2 | Regulatory classification (Howey analysis) | ⬜ Not started | Utility token vs. security token determination |
| L3 | KYC/AML provider integration | ⬜ Not started | Candidates: Jumio, Onfido, Sumsub |
| L4 | Terms of Service — token-specific addendum | ⬜ Not started | Must cover redemption, cancellation, risks |
| L5 | Jurisdiction whitelist/blacklist | ⬜ Not started | OFAC, sanctioned countries, state-level restrictions |
| L6 | Money transmitter license assessment | ⬜ Not started | State-by-state analysis (US) or e-money license (EU) |

### 4.2 Technical Infrastructure

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| T1 | XRPL mainnet issuer wallet (cold + hot) | ⬜ Not started | Currently using testnet placeholder address |
| T2 | TrustLine setup automation | Scaffolded | `xrpl_bridge.py` has `set_trustline()` — needs mainnet testing |
| T3 | NFTokenMint with real IPFS metadata | Scaffolded | `web3_issuance.py` references IPFS URIs — not pinned |
| T4 | IPFS pinning service | ⬜ Not started | Pin certificate metadata (Pinata, Infura, or self-hosted) |
| T5 | Multi-sig treasury wallet | ⬜ Not started | Single-key issuer is unacceptable for production |
| T6 | Transaction signing service | ⬜ Not started | HSM or managed signing (AWS KMS, Azure Key Vault) |
| T7 | On-chain audit trail | Scaffolded | Memo fields in XRPL transactions — needs formal schema |

### 4.3 Treasury & Reserve

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| R1 | APMEX API integration (live) | Scaffolded | `treasury.py` has metal price fetching — needs API key |
| R2 | Reserve proof automation | ⬜ Not started | Periodic SHA-256 anchoring of reserve balances to XRPL |
| R3 | Reserve Ratio covenant enforcement | Scaffolded | `certificates.py` checks RRR but uses mock data |
| R4 | Third-party audit engagement | ⬜ Not started | Annual attestation of metal holdings vs. certificate face value |

### 4.4 Operational Readiness

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| O1 | Production database (PostgreSQL) | ⬜ Not started | Currently SQLite |
| O2 | Rate limiting on issuance endpoints | ⬜ Not started | Prevent batch-minting abuse |
| O3 | Issuance event monitoring & alerting | ⬜ Not started | Every mint, every transfer, every redemption |
| O4 | Rollback / pause mechanism | ⬜ Not started | Circuit breaker for issuance if anomaly detected |
| O5 | Load testing at scale | ⬜ Not started | Simulate 10K concurrent joins with issuance |

---

## 5. Issuance Flow — Target Architecture

When all gates are cleared, the issuance flow will work as follows:

```
Member Joins ($100)
       │
       ▼
┌──────────────────┐
│  KYC/AML Check   │  ← Gate: L1, L3, L5
│  (Jumio/Onfido)  │
└────────┬─────────┘
         │ PASS
         ▼
┌──────────────────┐     ┌──────────────────────┐
│  Create Identity │────▶│  Module 1: Identity   │  ✅ EXISTS
│  (.helios name)  │     │  (core/identity.py)   │
└────────┬─────────┘     └──────────────────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────────┐
│  Form Links      │────▶│  Module 2: Network    │  ✅ EXISTS
│  (initiator bond)│     │  (core/network.py)    │
└────────┬─────────┘     └──────────────────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────────┐
│  Token Issuance  │────▶│  Module 3: Issuance   │  ⬜ NOT LIVE
│  HLS + HC-NFT    │     │  (core/web3_issuance) │
└────────┬─────────┘     └──────────────────────┘
         │
         ├─── 1. Calculate HLS tokens (rate × amount)
         ├─── 2. XRPL TrustLine (if first issuance for member)
         ├─── 3. XRPL Payment (HLS to member wallet)
         ├─── 4. Mint HC-NFT certificate (XRPL NFTokenMint)
         ├─── 5. Pin metadata to IPFS
         ├─── 6. Record in DB + audit ledger
         └─── 7. Emit event for energy propagation
```

---

## 6. Token Specification

| Property | Value | Source |
|----------|-------|--------|
| Name | Helios | `config.py → TOKEN_NAME` |
| Symbol | HLS | `config.py → TOKEN_SYMBOL` |
| Total Supply | 100,000,000 | Hard-coded, immutable |
| Decimals | 8 | Standard precision |
| Minting | **Disabled forever** | No mint function in `token.py` |
| Ledger | XRPL | `xrpl_bridge.py` |
| Issuer | TBD (mainnet wallet) | Currently testnet placeholder |

### Token Allocation

| Pool | Percent | Amount | Lock |
|------|---------|--------|------|
| Reward Pool | 45% | 45,000,000 | Smart contract time-lock |
| Circulation | 30% | 30,000,000 | Released via energy propagation |
| Development | 15% | 15,000,000 | 3-year vesting |
| Reserve | 10% | 10,000,000 | Protocol stability buffer |

---

## 7. Certificate Specification (HC-NFT)

| Property | Value |
|----------|-------|
| ID Format | `HC-{SHA256(key + amount + epoch + rate)[:24]}` |
| Backing | Physical metal (gold) via APMEX |
| Redemption | Gold or stablecoin, subject to Reserve Ratio covenant |
| Cancellation | 2% energy burn (irreversible) |
| On-chain | XRPL NFToken (when live) |
| Metadata | IPFS-pinned JSON (when live) |

### Certificate State Machine

```
ACTIVE ──── redeem() ────▶ REDEEMED   (gold/stablecoin exit)
   │                                   Gate: RRR ≥ 1.0
   │
   └─── cancel() ────────▶ CANCELLED  (2% energy burned permanently)
```

---

## 8. What MUST NOT Happen Before Gates Clear

1. **No public token sale.** HLS cannot be sold, traded, or listed until L1–L6 are resolved.
2. **No mainnet minting.** All issuance stays in simulation/testnet until T1–T7 are complete.
3. **No certificate redemption for real assets.** Certificates are DB records until R1–R4 are verified.
4. **No marketing of token value.** No price claims, no ROI projections, no "investment" language.
5. **No third-party exchange listing.** Listing requires legal clearance, market-making plan, and audit.

---

## 9. Activation Sequence

When all gates are GREEN, activation follows this order:

```
Phase 1: Foundation (CURRENT)
  ✅ Identity operational
  ✅ Network links operational
  ✅ Energy propagation operational
  ⬜ Issuance in simulation mode

Phase 2: Infrastructure
  □ PostgreSQL migration
  □ XRPL mainnet wallet setup (multi-sig)
  □ IPFS pinning service
  □ HSM / managed signing
  □ KYC provider integration

Phase 3: Legal Clearance
  □ Securities opinion received
  □ ToS token addendum published
  □ Jurisdiction whitelist finalized
  □ Money transmitter assessment complete

Phase 4: Issuance Go-Live
  □ Testnet end-to-end with real KYC flow
  □ Load test passed
  □ Third-party audit scheduled
  □ Circuit breaker tested
  □ FLIP THE SWITCH: web3_issuance.py → mainnet mode
```

---

## 10. Files to Modify at Go-Live

| File | Change Required |
|------|-----------------|
| `core/web3_issuance.py` | Remove simulation fallbacks, point to mainnet issuer |
| `core/xrpl_bridge.py` | Set `XRPL_NETWORK=mainnet`, configure real secrets |
| `core/certificates.py` | Connect RRR covenant to live reserve data |
| `core/treasury.py` | Enable APMEX API with production key |
| `config.py` | Set `XRPL_ISSUER_ADDRESS` and `XRPL_TREASURY_ADDRESS` to real wallets |
| `.env` | Production secrets: XRPL keys, APMEX key, KYC provider keys |

---

## 11. Summary

The issuance layer is **architecturally complete but operationally dormant**.
Every class, every method, every flow exists in code — but none of it touches
real money, real tokens, or real assets until the gate checklist is fully cleared.

This is by design. Helios launches with identity and relationships first.
Issuance activates only when legal, technical, and operational prerequisites
are met. There is no shortcut.

```
IDENTITY    ████████████████████  100%  LIVE
NETWORK     ████████████████████  100%  LIVE
ISSUANCE    ████░░░░░░░░░░░░░░░░   20%  SCAFFOLDED — gates pending
```
