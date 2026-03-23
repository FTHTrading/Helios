"""
Helios OS — Celery Application Factory
═══════════════════════════════════════
Background job processing for settlements, minting, and IPFS pinning.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Redis URL from environment
REDIS_URL = os.getenv("HELIOS_REDIS_URL", "redis://localhost:6379/0")


def make_celery(app=None):
    """Create a Celery instance, optionally bound to a Flask app."""
    celery = Celery(
        "helios",
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=["tasks"],
    )

    celery.conf.update(
        # Serialization
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],

        # Timezone
        timezone="UTC",
        enable_utc=True,

        # Reliability
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_reject_on_worker_lost=True,

        # Result expiry (24 hours)
        result_expires=86400,

        # Beat schedule — automatic settlements
        beat_schedule={
            "run-settlement-propagation": {
                "task": "tasks.run_scheduled_settlement",
                "schedule": crontab(minute="*/30"),  # Every 30 minutes
                "args": (),
            },
            "health-check-integrations": {
                "task": "tasks.check_integration_health",
                "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
                "args": (),
            },
        },
    )

    if app:
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            abstract = True

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery


# Module-level celery instance for `celery -A celery_app worker`
celery = make_celery()
