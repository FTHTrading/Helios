# XRPL SURFACE MAP — Helios

Generated: 2026-03-18

Complete map of every XRPL touchpoint in the codebase — modules, transaction types, wallet surfaces, signing flows, and hybrid/production mode boundaries.

---

## XRPL Modules

| Module | Class | Role |
|---|---|---|
| `core/xrpl_bridge.py` | `XRPLBridge` | Core adapter — all XRPL transaction construction and submission |
| `core/xaman.py` | `XamanService` | Xaman/XUMM signing payload creation and resolution |
| `core/atomic_wallet.py` | `AtomicWallet` | XRPL + Stellar dual-chain wallet provisioning |
| `core/web3_issuance.py` | `TokenIssuance`, `NFTIssuance` | Token delivery and NFT certificate minting |
| `core/treasury.py` | `TreasuryEngine` | MVR anchoring via XRPL 0-drop self-payment |
| `core/ipfs.py` | `IpfsBundleService` | Evidence bundle hashing + Pinata upload (used with XRPL anchoring) |
| `core/integrations.py` | `IntegrationReadiness` | Provider readiness snapshot including XRPL |

---

## XRPL Transaction Types Used

| Tx Type | Where | Purpose |
|---|---|---|
| `TrustSet` | `XRPLBridge.submit_trustset()` | Set HLS trustline on member wallet |
| `Payment` (IOU) | `XRPLBridge.issue_token_payment()` | Issue HLS tokens to member |
| `Payment` (0-drop to self) | `XRPLBridge.anchor_receipt()` | Anchor MVR evidence hash in ledger memo |
| `NFTokenMint` | `XRPLBridge.mint_nft()` | Mint HC-NFT certificate on-chain |

---

## XRPL Configuration Keys (`.env`)

| Env Var | Maps to `HeliosConfig` attr | Required for |
|---|---|---|
| `HELIOS_XRPL_NETWORK` | `XRPL_NETWORK` | Determines testnet / mainnet |
| `HELIOS_XRPL_NODE` | `XRPL_NODE_URL` | JSON-RPC endpoint |
| `HELIOS_XRPL_ENABLE_SUBMIT` | `XRPL_ENABLE_SUBMIT` | Must be `true` to submit real txs |
| `HELIOS_XRPL_ISSUER_WALLET` | `XRPL_ISSUER_ADDRESS` | Token issuer classic address |
| `HELIOS_XRPL_ISSUER_SECRET` | `XRPL_ISSUER_SECRET` | Token issuer seed — controls all HLS issuance |
| `HELIOS_XRPL_TREASURY_WALLET` | `XRPL_TREASURY_ADDRESS` | Treasury classic address |
| `HELIOS_XRPL_TREASURY_SECRET` | `XRPL_TREASURY_SECRET` | Treasury seed — controls anchoring txs |

Defaults: `XRPL_NETWORK=testnet`, `XRPL_NODE=https://s.altnet.rippletest.net:51234`, `XRPL_ENABLE_SUBMIT=false`.

---

## Readiness Check

`IntegrationReadiness.snapshot()` evaluates XRPL as **ready** only when ALL of:

```python
xrpl_configured = bool(
    HeliosConfig.XRPL_NODE_URL and
    HeliosConfig.XRPL_ISSUER_ADDRESS and
    HeliosConfig.XRPL_ISSUER_SECRET
)
xrpl_package = importlib.util.find_spec("xrpl") is not None
xrpl_ready = xrpl_configured and xrpl_package and HeliosConfig.XRPL_ENABLE_SUBMIT
```

Verified at: `GET /api/infra/launch-readiness`

---

## Hybrid vs Production Mode (per transaction)

Every XRPL operation checks `XRPLBridge.is_ready()` before submitting. If not ready, returns a deterministic dry-run result containing:

```json
{
  "action": "TrustSet",
  "simulation": true,
  "submitted": false,
  "network": "testnet",
  "tx_hash": "<SHA256 of serialized payload — deterministic>",
  "timestamp": "..."
}
```

If ready, submits via `xrpl-py` and returns real ledger result with `"simulation": false`.

---

## `XRPLBridge` — Method Surface

```python
XRPLBridge()
  .status()                           → IntegrationReadiness snapshot for XRPL
  .is_ready()                         → bool

  .create_member_wallet(member_id)    → { classic_address, seed, simulation }
  .submit_trustset(address, secret)   → { tx_hash, simulation, ledger_result }
  .issue_token_payment(dest, value)   → { tx_hash, simulation, ledger_result }
  .mint_nft(metadata_uri, taxon)      → { tx_hash, simulation, ledger_result }
  .anchor_receipt(mvr_id, hash, cid)  → { tx_hash, memo, simulation }

  ._submit_transaction(tx, secret)    → { tx_hash, simulation=False, ledger_result }
  ._simulate_wallet(member_id)        → { classic_address, seed, simulation=True }
  ._simulate_tx(action, payload)      → { tx_hash, simulation=True }
  ._hash_payload(payload)             → SHA256 hex string
```

---

## `XamanService` — Signing Payload Surface

```python
XamanService()
  .is_ready()                         → bool (API key + secret set)

  .create_payload(action, **kwargs)   → {
      payload_uuid, qr_png, always, opened, txjson, simulation
  }

  .get_payload(payload_uuid)          → {
      resolved, signed, expired, account, tx_hash, simulation
  }
```

**Wallet endpoint:** `POST /api/wallet/xaman/payload`  
**Signing flow:** user scans QR in Xaman app → signs TrustSet → `GET /api/wallet/xaman/payload/{uuid}` polls for resolution.

Supported actions from `_build_tx()`:
- `trustset` — set HLS trustline
- `payment` — send HLS
- `signin` — sign-in without tx
- Custom `txjson` passthrough

---

## `AtomicWallet` — Dual-Chain Provisioning

Provisions **XRPL + Stellar** keypairs on every member join:

```python
AtomicWallet(member_id)
  .provision_xrpl()       → calls XRPLBridge.create_member_wallet()
                             then XRPLBridge.submit_trustset()
  .provision_stellar()    → Ed25519 Stellar keypair + ChangeTrust
  .settle(amount, asset)  → auto-routes inbound allocation
  .to_manifest()          → full wallet manifest dict
```

XRPL address is `r{SHA256(member_id)[:33]}` in simulation mode.  
Real mode: `Wallet.create()` from `xrpl-py`.

---

## `web3_issuance.py` — Token + NFT Issuance

Three issuance types triggered on member join:

| Step | Class | Method | XRPL Tx |
|---|---|---|---|
| 1 | `TokenIssuance` | `issue_to_wallet(dest, amount)` | `Payment` (IOU) |
| 2 | `NFTIssuance` | `mint_cert_nft(holder, energy, ...)` | `NFTokenMint` |
| 3 | `NFTIssuance` | `mint_ceremonial_nft(member)` | `NFTokenMint` |

NFT metadata URIs point to IPFS: `ipfs://QmHeliosCertificates/{cert_id}` and `ipfs://QmHeliosCeremonial/{member_id}`.

Phase pricing:
- Phase 1: $0.05/HLS (founding)
- Phase 2: $0.25/HLS
- Phase 3: $0.50/HLS

---

## Treasury XRPL Anchoring

Each Metal Vault Receipt (MVR) state transition can be anchored:

```python
TreasuryEngine.anchor_to_xrpl(mvr_id, evidence_sha256, ipfs_cid)
    → XRPLBridge.anchor_receipt(mvr_id, hash, cid)
        → Payment tx, Amount=0, from treasury_address to treasury_address
        → Memo: "{mvr_id}|{sha256}|{ipfs_cid}"
```

This creates an immutable timestamp on the public XRPL ledger without revealing sensitive data on-chain.

MVR evidence flow:
```
APMEX invoice
    → IpfsBundleService.build_receipt_manifest()
    → IpfsBundleService.hash_bundle() → SHA-256
    → IpfsBundleService.pin_json() → Pinata → IPFS CID
    → XRPLBridge.anchor_receipt(mvr_id, sha256, cid)
    → VaultReceipt.xrpl_tx_hash saved
```

---

## API Endpoints — XRPL/Web3 Surface

| Method | Endpoint | Function |
|---|---|---|
| `POST` | `/api/wallet/xaman/payload` | Create Xaman signing payload |
| `GET` | `/api/wallet/xaman/payload/<uuid>` | Poll payload resolution |
| `GET` | `/api/infra/launch-readiness` | XRPL + all provider readiness |
| `GET` | `/api/token/verify` | 100M supply, no mint, anti-rug |
| `GET` | `/api/treasury/reserves` | Metal reserves + XRPL anchor hashes |
| `POST` | `/api/certificates/redeem` | HC-NFT redemption (RRR gated) |
| `POST` | `/api/certificates/mint` | Store energy in HC-NFT |
| `GET` | `/api/energy/conservation` | ∑IN = ∑OUT verification |
| `GET` | `/api/certificates/covenant` | RRR covenant auto-check |

---

## Web3 Page Flow (`/web3` → `templates/web3.html`)

```
1. User opens /web3
2. Page calls POST /api/wallet/xaman/payload {action: "trustset"}
3. Xaman QR rendered
4. User scans → signs TrustSet in Xaman app
5. Page polls GET /api/wallet/xaman/payload/{uuid}
6. On resolved + signed → wallet connected, trustline active
7. Member can now receive HLS issuance
```

---

## XRPL Python Package (`xrpl-py`)

Version pinned: `xrpl-py>=4.0,<5.0` (in `requirements.txt`)

Modules used (all via `importlib.import_module` for lazy loading):
- `xrpl.wallet.Wallet` — keypair creation and from_seed
- `xrpl.clients.JsonRpcClient` — JSON-RPC client
- `xrpl.transaction.safe_sign_and_autofill_transaction` — sign + autofill
- `xrpl.transaction.send_reliable_submission` — submit with retry
- `xrpl.models.transactions.TrustSet`
- `xrpl.models.transactions.Payment`
- `xrpl.models.transactions.NFTokenMint`
- `xrpl.models.transactions.Memo`
- `xrpl.models.amounts.IssuedCurrencyAmount`

Lazy import pattern means the app starts and runs correctly even without `xrpl-py` installed — it just falls back to simulation mode.

---

## Security Notes

| Risk | Mitigation |
|---|---|
| Issuer secret exposure | Never in code — env var only (`HELIOS_XRPL_ISSUER_SECRET`) |
| Treasury secret exposure | Never in code — env var only (`HELIOS_XRPL_TREASURY_SECRET`) |
| Testnet vs mainnet | `XRPL_ENABLE_SUBMIT=false` default prevents accidental mainnet submission |
| Simulation leakage | Every response includes `"simulation": true/false` — callers can validate |
| Unsigned Xaman payloads | `get_payload()` checks `signed` and `expired` before acting on resolution |
| Replay attacks | Each tx anchored with timestamp + unique MVR ID or member ID |
| Bot minting | `AntifraudEngine` gates every join/link/reward event before NFT issuance |

---

## Production Activation Checklist (XRPL)

To move from hybrid → production XRPL:

- [ ] Generate issuer XRPL wallet (mainnet) and fund with sufficient XRP for reserves
- [ ] Generate treasury XRPL wallet and fund
- [ ] Set `HELIOS_XRPL_NETWORK=mainnet`
- [ ] Set `HELIOS_XRPL_NODE` to a reliable mainnet JSON-RPC node (e.g. `https://xrplcluster.com`)
- [ ] Set `HELIOS_XRPL_ISSUER_WALLET` (classic address)
- [ ] Set `HELIOS_XRPL_ISSUER_SECRET` (seed — store securely, never in repo)
- [ ] Set `HELIOS_XRPL_TREASURY_WALLET`
- [ ] Set `HELIOS_XRPL_TREASURY_SECRET`
- [ ] Set `HELIOS_XRPL_ENABLE_SUBMIT=true`
- [ ] Set `HELIOS_XAMAN_API_KEY` and `HELIOS_XAMAN_API_SECRET` from xumm.app
- [ ] Verify: `GET /api/infra/launch-readiness` shows `xrpl.ready = true`
- [ ] Test TrustSet on testnet before flipping to mainnet
