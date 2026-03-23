# Helios v3.0.0 — Launch Checklist

Use this checklist before every deployment. Items marked **[CRITICAL]** are
hard blockers — the system will not function correctly without them.

---

## 1. Environment & Secrets

- [ ] **[CRITICAL]** `HELIOS_ENV` set to `production`
- [ ] **[CRITICAL]** `SECRET_KEY` generated (`openssl rand -hex 32`), unique per environment
- [ ] **[CRITICAL]** `API_KEY` generated and distributed to authorized clients
- [ ] **[CRITICAL]** `DATABASE_URL` points to production PostgreSQL (not SQLite)
- [ ] `REDIS_URL` set (required for Celery)
- [ ] `SENTRY_DSN` configured for error tracking
- [ ] `PINATA_API_KEY` + `PINATA_SECRET_KEY` set for IPFS pinning
- [ ] `STRIPE_SECRET_KEY` set for fiat payments
- [ ] All secrets stored in secure vault (not plain text files)

## 2. XRPL (Primary Rail)

- [ ] **[CRITICAL]** `XRPL_SEED_SECRET` set to a funded issuer wallet
- [ ] **[CRITICAL]** Issuer wallet has sufficient XRP for operations (≥ 50 XRP)
- [ ] `XRPL_NETWORK_URL` points to correct network (mainnet or testnet)
- [ ] NFT minting tested: gold certificates (taxon 1) and ceremonial (taxon 100)
- [ ] Treasury anchoring tested: self-payment with memo
- [ ] Trust lines configured for HLS token
- [ ] Verify `/api/health/ready` shows `"xrpl": true`

## 3. EVM (Secondary Rail — Optional)

- [ ] `EVM_ENABLED` set to `true` (skip this section entirely if `false`)
- [ ] `EVM_RPC_URL` set to reliable RPC (Alchemy / Infura)
- [ ] `EVM_CHAIN_ID` matches the target network
- [ ] `EVM_PRIVATE_KEY` set (deployer address with MINTER_ROLE)
- [ ] `EVM_CONTRACT_ADDRESS` set to deployed HeliosToken address
- [ ] Contract verified on block explorer
- [ ] Test mint executed successfully via `/api/evm/mint`
- [ ] `/api/evm/status` returns `"connected": true`

## 4. Database

- [ ] **[CRITICAL]** PostgreSQL 16 running and accessible
- [ ] **[CRITICAL]** `alembic upgrade head` executed (all migrations applied)
- [ ] Connection pooling verified (pool_size=10, max_overflow=20)
- [ ] Backup schedule configured (daily pg_dump minimum)
- [ ] `SELECT 1` works via `/api/health/ready`

## 5. Background Jobs

- [ ] Redis running and accessible
- [ ] Celery worker started and processing tasks
- [ ] Celery Beat started and scheduling tasks
- [ ] Settlement task running every 30 minutes (verify in logs)
- [ ] Health check task running every 6 hours
- [ ] IPFS pinning task working on-demand

## 6. Networking & Security

- [ ] HTTPS/TLS termination configured (nginx/Caddy/ALB)
- [ ] `ProxyFix` middleware active for correct IP forwarding
- [ ] CORS policy reviewed (production domains only)
- [ ] Rate limiting active on API endpoints
- [ ] `DEBUG = False` verified in production config
- [ ] No secrets in source code or git history
- [ ] `.env` files in `.gitignore`

## 7. Application Health

- [ ] `GET /health` returns 200 with `"status": "healthy"`
- [ ] `GET /api/health/ready` returns 200 with all services `true`
- [ ] All 27 page routes render without 500 errors
- [ ] All 55+ API endpoints respond (authenticated endpoints return 401 without key)
- [ ] EVM endpoints respond at `/api/evm/*`
- [ ] Static assets loading (CSS, JS, images)

## 8. Functional Verification

- [ ] Member creation flow works end-to-end
- [ ] Token issuance calculates correctly (Phase 1: $0.05/HLS)
- [ ] Energy propagation (BFS settlement) completes without error
- [ ] NFT certificate minting succeeds (IPFS pin + XRPL mint)
- [ ] Ceremonial NFT minting succeeds for each tier
- [ ] Treasury anchor creates valid XRPL memo transaction
- [ ] `.helios` domain registration works
- [ ] Bond creation and maturity work
- [ ] Audit log captures all critical operations

## 9. Monitoring

- [ ] Sentry receiving error events
- [ ] Sentry performance tracing enabled (`traces_sample_rate`)
- [ ] Structured logging outputs JSON in production
- [ ] Log aggregation configured (CloudWatch / ELK / similar)
- [ ] Uptime monitoring on `/health` (Pingdom / UptimeRobot / similar)
- [ ] Alert channels configured (email / Slack / PagerDuty)

## 10. Documentation

- [ ] `ARCHITECTURE.md` up to date
- [ ] `DEPLOYMENT.md` reviewed by team
- [ ] `.env.production.example` has all required variables listed
- [ ] API documentation current (endpoint list, auth requirements)
- [ ] Runbook exists for common operational tasks

---

## Rollback Plan

If a deployment fails:

1. **Docker**: `docker compose -f docker-compose.prod.yml down && git checkout <last-good-tag> && docker compose -f docker-compose.prod.yml up -d --build`
2. **Database**: `alembic downgrade -1` (or restore from pg_dump backup)
3. **EVM contract**: Contracts are immutable — pause via `pause()` if needed, deploy new version and update `EVM_CONTRACT_ADDRESS`
4. **Static site**: Netlify instant rollback via deploy history

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| XRPL wallet drained | Low | Critical | Monitor balance, alert at < 10 XRP |
| EVM private key leaked | Low | High | Rotate key, revoke MINTER_ROLE, redeploy |
| Database corruption | Low | Critical | Daily backups, WAL archiving |
| IPFS pin failure | Medium | Low | Graceful fallback to hash URI, retry queue |
| Celery worker crash | Medium | Medium | Docker restart policy, health monitoring |
| Stripe webhook replay | Low | Low | Idempotency keys on all payment handlers |
| Rate limit bypass | Low | Medium | WAF rules, API key rotation |
