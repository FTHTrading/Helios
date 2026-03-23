# Helios v3.0.0 — Deployment Guide

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Application runtime |
| Node.js | 18+ | Hardhat / Solidity tooling |
| Docker + Compose | 24+ | Production containers |
| PostgreSQL | 16 | Production database |
| Redis | 7 | Celery broker + cache |
| Git | 2.40+ | Source control |

---

## 1. Local Development

```bash
# Clone
git clone git@github.com:FTHTrading/Helios.git && cd helios\ final

# Python venv
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install deps
pip install -r requirements.txt

# Copy env template
cp .env.production.example .env   # edit values

# Run locally (SQLite, debug mode)
set HELIOS_ENV=development        # PowerShell: $env:HELIOS_ENV="development"
python app.py
# → http://127.0.0.1:5000
```

### Running Tests

```bash
# Python test suite
pip install pytest pytest-cov ruff
pytest tests/ -v --tb=short

# Lint
ruff check .

# Solidity tests (requires Node.js)
npm install
npx hardhat test
```

---

## 2. Environment Variables

Copy `.env.production.example` and fill in real values.

### Required (production will refuse to start without these)

| Variable | Example | Notes |
|----------|---------|-------|
| `SECRET_KEY` | `openssl rand -hex 32` | Flask session signing |
| `API_KEY` | `openssl rand -hex 24` | Bearer token for mutating APIs |
| `DATABASE_URL` | `postgresql://helios:pass@db:5432/helios` | PostgreSQL connection |
| `XRPL_SEED_SECRET` | (private) | XRPL issuer wallet seed |

### Recommended

| Variable | Default | Notes |
|----------|---------|-------|
| `HELIOS_ENV` | `development` | Set `production` or `staging` |
| `SENTRY_DSN` | (none) | Error monitoring |
| `REDIS_URL` | `redis://localhost:6379/0` | Celery broker |
| `PINATA_API_KEY` / `PINATA_SECRET_KEY` | (none) | IPFS metadata pinning |
| `STRIPE_SECRET_KEY` | (none) | Fiat payments |

### EVM (optional — secondary rail)

| Variable | Default | Notes |
|----------|---------|-------|
| `EVM_ENABLED` | `false` | Set `true` to activate EVM rail |
| `EVM_RPC_URL` | (none) | JSON-RPC endpoint (Alchemy/Infura) |
| `EVM_CHAIN_ID` | `11155111` | Network chain ID |
| `EVM_PRIVATE_KEY` | (none) | Deployer/minter key |
| `EVM_CONTRACT_ADDRESS` | (none) | Deployed HeliosToken address |
| `EVM_EXPLORER_URL` | (none) | Block explorer base URL |

---

## 3. Database Migrations (Alembic)

```bash
# Generate a new migration after model changes
alembic revision --autogenerate -m "describe change"

# Apply all pending migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Show current state
alembic current
```

The first time on a new DB, run `alembic upgrade head` to apply all migrations.
Alembic reads `DATABASE_URL` from `config.py`.

---

## 4. Deploy ERC-20 Contract (Hardhat)

Only needed if enabling the EVM secondary rail.

```bash
# Install Node deps
npm install

# Compile
npx hardhat compile

# Deploy to testnet (e.g., Sepolia)
npx hardhat run scripts/deploy.js --network sepolia

# Save the printed contract address to .env as EVM_CONTRACT_ADDRESS
# Set EVM_ENABLED=true

# Verify on Etherscan (optional)
npx hardhat verify --network sepolia <CONTRACT_ADDRESS>
```

Deployment artifacts are saved to `deployments/<network>-<timestamp>.json`.

---

## 5. Docker Production Deployment

### Quick Start

```bash
# Build and start all services
docker compose -f docker-compose.prod.yml up -d --build

# Check health
curl http://localhost:5000/health        # liveness
curl http://localhost:5000/api/health/ready  # readiness (DB, Redis, XRPL)

# Run migrations inside container
docker compose -f docker-compose.prod.yml exec web alembic upgrade head

# View logs
docker compose -f docker-compose.prod.yml logs -f web
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| `web` | 5000 | Gunicorn (4 workers) serving Flask |
| `worker` | — | Celery worker (settlement, IPFS) |
| `beat` | — | Celery Beat scheduler |
| `db` | 5432 | PostgreSQL 16 (internal only) |
| `redis` | 6379 | Redis 7 (internal only) |

### Scaling

```bash
# Scale workers for higher throughput
docker compose -f docker-compose.prod.yml up -d --scale worker=3
```

### SSL / Reverse Proxy

Place nginx or Caddy in front with HTTPS termination.
The app uses `ProxyFix` middleware — set `X-Forwarded-For`, `X-Forwarded-Proto`.

```nginx
server {
    listen 443 ssl;
    server_name heliosdigital.xyz;

    ssl_certificate     /etc/ssl/helios.crt;
    ssl_certificate_key /etc/ssl/helios.key;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 6. Static Site Deployment (Netlify)

The public marketing pages are exported via Frozen-Flask:

```bash
# Generate static HTML
python freeze.py

# Output goes to build/
# Deploy via Netlify CLI or Git push to heliosdigital.xyz
```

---

## 7. Monitoring & Operations

### Health Endpoints

| Endpoint | Type | Checks |
|----------|------|--------|
| `GET /health` | Liveness | App responding, version, env |
| `GET /api/health/ready` | Readiness | DB (SELECT 1), Redis (PING), XRPL connectivity |

### Celery Monitoring

```bash
# Watch active tasks
docker compose -f docker-compose.prod.yml exec worker celery -A celery_app.celery inspect active

# Check beat schedule
docker compose -f docker-compose.prod.yml exec beat celery -A celery_app.celery inspect scheduled
```

### Sentry

Set `SENTRY_DSN` in `.env`. Structured breadcrumbs are automatically attached to
audit events, settlements, and blockchain operations.

### Audit Trail

All critical operations are logged to the `audit_log` table:

```sql
SELECT action, actor_id, chain, tx_hash, amount, created_at
FROM audit_log
ORDER BY created_at DESC
LIMIT 50;
```

---

## 8. Backup & Recovery

### Database

```bash
# Backup
docker compose -f docker-compose.prod.yml exec db pg_dump -U helios helios > backup.sql

# Restore
docker compose -f docker-compose.prod.yml exec -T db psql -U helios helios < backup.sql
```

### XRPL Wallets

Wallet seeds are **not** stored in the database. Keep secure backups of:
- `XRPL_SEED_SECRET` (issuer wallet)
- `XRPL_TREASURY_SECRET` (treasury wallet, if separate)

### EVM Keys

Keep secure backup of `EVM_PRIVATE_KEY`. The deployer address holds MINTER_ROLE
on the HeliosToken contract.
