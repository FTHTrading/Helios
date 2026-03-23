FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App source
COPY . .

# Create data directory for SQLite fallback (dev only)
RUN mkdir -p /app/data

# Non-root user
RUN useradd -m helios && chown -R helios:helios /app
USER helios

EXPOSE 5050

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5050/health || exit 1

# Production entrypoint
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "--timeout", "120", "--access-logfile", "-", "wsgi:application"]
