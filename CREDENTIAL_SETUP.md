# Helios — Credential Setup Guide
> Get from zero to accepting real testnet payments in 10 minutes.

## Status After This Session

| Provider | Status | What's Done |
|----------|--------|-------------|
| **XRPL** | **LIVE (testnet)** | Wallets generated, funded, wired into .env |
| **Stripe** | **Needs 5 min** | Package installed, code ready — just need test keys |
| **Xaman** | **Needs 5 min** | Code ready — just need developer credentials |
| Identity | **LIVE** | name.helios creation, QR codes, recovery |
| Energy | **LIVE** | $100 atomic split, conservation law |
| Links | **LIVE** | Power-of-5, validation, cooldown |

---

## 1. Stripe Test Keys (5 minutes)

Stripe lets you accept payments. Test mode uses fake card numbers — no real money.

### Steps:
1. Go to **https://dashboard.stripe.com/register**
2. Create a free account (email + password, no business docs needed for test mode)
3. Once in the dashboard, click **"Developers"** in the left sidebar
4. Click **"API Keys"**
5. Copy:
   - **Publishable key** → starts with `pk_test_`
   - **Secret key** → starts with `sk_test_` (click "Reveal")

### Paste into `.env`:
```
HELIOS_STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
HELIOS_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
```

### Webhook (do this after deploy):
1. In Stripe Dashboard → Developers → Webhooks → Add endpoint
2. URL: `https://heliosdigital.xyz/api/funding/webhook/stripe`
3. Events: `checkout.session.completed`
4. Copy the **Signing secret** → starts with `whsec_`
```
HELIOS_STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE
```

### Test Cards:
- **Success:** `4242 4242 4242 4242` (any future date, any CVC)
- **Decline:** `4000 0000 0000 0002`

---

## 2. Xaman / XUMM Developer App (5 minutes)

Xaman lets users sign XRPL transactions from their phone.

### Steps:
1. Go to **https://apps.xumm.dev/**
2. Sign in with your existing Xaman mobile app (or create one)
3. Click **"Create New Application"**
4. Fill in:
   - App Name: `Helios Digital`
   - Description: `Neural field protocol activation and wallet signing`
   - Return URL: `https://heliosdigital.xyz/activate`
5. Copy:
   - **API Key** (uuid format)
   - **API Secret**

### Paste into `.env`:
```
HELIOS_XAMAN_API_KEY=your-api-key-uuid
HELIOS_XAMAN_API_SECRET=your-api-secret
```

---

## 3. XRPL Wallets (ALREADY DONE)

Your testnet wallets are generated and funded:

| Wallet | Address | Role |
|--------|---------|------|
| Issuer | `rfrhMPK1VzWr3vjaXBDCDFvKw5az4b6uuF` | Issues HLS tokens to members |
| Treasury | `rKZDuUcXrk9K92NacVJKLtWpUeFbja5EjB` | Holds reserve funds |

These are already in your `.env`. When ready for mainnet, generate new wallets and fund with real XRP.

---

## Quick Start: After Adding Stripe Keys

Restart the server:
```bash
python app.py
```

Test the full flow:
```bash
# Check readiness (Stripe should show configured: true)
curl http://localhost:5050/api/infra/readiness

# Create a member
curl -X POST http://localhost:5050/api/identity/create \
  -H "Content-Type: application/json" \
  -d '{"name": "firstclient"}'

# Start a checkout ($100 atomic entry)
curl -X POST http://localhost:5050/api/funding/checkout \
  -H "Content-Type: application/json" \
  -d '{"offer_code": "entry", "member_id": "firstclient.helios"}'
```

The checkout response will include a Stripe URL. Open it, use test card `4242 4242 4242 4242`, and the webhook will auto-fulfill the order.

---

## Optional Providers (enhance but don't block onboarding)

| Provider | Purpose | Setup |
|----------|---------|-------|
| OpenAI | Ask Helios chat | Get key at platform.openai.com |
| ElevenLabs | Voice AI | Get key at elevenlabs.io |
| Telnyx | SMS verification | Get key at telnyx.com |
| Pinata | IPFS evidence storage | Get key at pinata.cloud |
| Cloudflare | DNS/SSL | Get key at cloudflare.com |
| Sentry | Error monitoring | Get DSN at sentry.io |
