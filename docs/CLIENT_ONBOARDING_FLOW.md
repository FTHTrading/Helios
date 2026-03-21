# Helios — Client Onboarding Flow

> Exact API sequence to onboard a new client from zero to activated.
> All endpoints verified working as of March 20, 2026.

---

## Prerequisites

- Server running: `python app.py` (default port 5050)
- `.env` configured with at minimum XRPL testnet keys (already done)
- For real payments: Stripe test keys added to `.env`

---

## Step 1 — Create Identity

The client picks a name. System creates `name.helios`.

```
POST /api/identity/create
Content-Type: application/json

{
  "name": "firstname",
  "referrer": "existingmember.helios"   // optional
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "helios_id": "firstname.helios",
    "display_name": "firstname",
    "node_state": "instantiated",
    "_key": "...",
    "recovery_phrase": ["word1", "word2", "...12 words"],
    "qr_code": "data:image/png;base64,..."
  }
}
```

**Client must save:**
- `_key` — stored locally, used for authenticated actions
- `recovery_phrase` — 12 words, write down, never stored server-side

---

## Step 2 — Form Link

Client connects with an existing member. Both must have active identities.

```
POST /api/field/link
Content-Type: application/json

{
  "initiator_id": "firstname.helios",
  "peer_id": "existingmember.helios"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "linked": true,
    "link_id": 1,
    "nodes": ["existingmember.helios", "firstname.helios"],
    "initiator_state": "connected",
    "peer_state": "connected",
    "message": "Link formed between firstname.helios and existingmember.helios."
  }
}
```

**Rules:**
- Max 5 links per node
- 24-hour cooldown between new links
- Duplicate links rejected with clear error
- Link is undirected — no hierarchy

---

## Step 3 — Select Activation Tier

Show the client the funding catalog.

```
GET /api/funding/catalog
```

**Activation tiers:**

| Code | Name | Price | HLS Received |
|------|------|-------|-------------|
| `entry` | Atomic Entry | $100 | 2,000 HLS |
| `builder` | Builder Activation | $250 | 5,000 HLS |
| `protocol` | Protocol Contract | $500 | 10,000 HLS |
| `accelerator` | Accelerator | $1,000 | 20,000 HLS |
| `architect` | Protocol Architect | $5,000 | 100,000 HLS |

**Subscriptions (optional, post-activation):**

| Code | Name | Price |
|------|------|-------|
| `plus` | Plus Membership | $20/mo |
| `pro` | Pro Membership | $99/mo |
| `operator` | Operator Membership | $499/mo |

---

## Step 4 — Process Payment

Create a Stripe checkout session for the selected tier.

```
POST /api/funding/checkout
Content-Type: application/json

{
  "offer_code": "entry",
  "member_id": "firstname.helios",
  "customer_email": "client@example.com"
}
```

**Response (201) when Stripe is configured:**
```json
{
  "success": true,
  "data": {
    "status": "created",
    "checkout_url": "https://checkout.stripe.com/...",
    "session_id": "cs_test_...",
    "offer": "Atomic Entry",
    "amount_usd": 100
  }
}
```

Client opens `checkout_url` → pays with card → redirected to success page.

**Test card:** `4242 4242 4242 4242` (any future expiry, any CVC)

**Without Stripe keys:** Response returns `status: "not_configured"` — payment step is skipped but the rest of the flow remains functional.

---

## Step 5 — Energy Injection

After payment confirms (via Stripe webhook, or manually triggered):

```
POST /api/energy/inject
Content-Type: application/json

{
  "member_id": "firstname.helios"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "member_id": "firstname.helios",
    "total_injected_usd": 100,
    "allocation": {
      "propagation": 45.0,
      "liquidity": 20.0,
      "treasury_surplus": 15.0,
      "infrastructure": 10.0,
      "buffer": 10.0
    },
    "conservation_check": true,
    "reference_id": "ENTRY-..."
  }
}
```

Every dollar is routed. No slush funds.

---

## Step 6 — Check Wallet

```
GET /api/wallet/balance/firstname.helios
```

**Response:**
```json
{
  "success": true,
  "data": {
    "helios_id": "firstname.helios",
    "balance": 2000.0,
    "pending": 0.0,
    "currency": "HLS"
  }
}
```

---

## Step 7 — XRPL Wallet (Testnet)

The XRPL bridge creates a real testnet wallet for the member:

```
POST /api/wallet/xaman/payload
Content-Type: application/json

{
  "action": "signin",
  "member_id": "firstname.helios"
}
```

If Xaman credentials are configured, this returns a signing payload URL.
If not, the backend XRPL bridge can still create wallets programmatically — the member just won't have the mobile signing UX.

---

## Step 8 — Verify Everything

**Energy conservation:**
```
GET /api/energy/conservation
→ { "balanced": true }
```

**Token integrity:**
```
GET /api/token/verify
→ { "integrity": "PASS", "expected_supply": 100000000.0 }
```

**Node stats:**
```
GET /api/field/stats/firstname.helios
→ { link_count, node_state, field_reach }
```

**Network health:**
```
GET /api/metrics/all
→ { reserve_ratio, flow_efficiency, churn_pressure, energy_velocity }
```

---

## Complete Flow Summary

```
Client arrives
  → POST /api/identity/create          (get helios_id + recovery phrase)
  → POST /api/field/link               (connect to referrer)
  → GET  /api/funding/catalog           (see activation tiers)
  → POST /api/funding/checkout          (pay via Stripe)
  → [Stripe webhook auto-fulfills]
  → POST /api/energy/inject             (energy enters the field)
  → GET  /api/wallet/balance            (confirm HLS received)
  → GET  /api/energy/conservation       (verify system integrity)
  
Client is now:
  - An active node in the Helios field
  - Linked to at least one peer
  - Holding HLS tokens
  - Energy routed through the protocol
  - Verifiable on XRPL testnet
```

---

## Error Handling

All errors return structured JSON:

```json
{
  "success": false,
  "error": "Human-readable error message"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Validation error — wrong/missing fields |
| 404 | Resource not found |
| 409 | Duplicate — identity or link already exists |
| 429 | Rate limited or cooldown active |
| 500 | Server error (should not happen — report if seen) |
