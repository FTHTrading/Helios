"""
Alembic environment configuration for Helios OS.
Reads DATABASE_URL from HeliosConfig and auto-generates migrations
from all SQLAlchemy models.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from config import HeliosConfig

# Import Base so Alembic sees all models
from models.member import Base
# Force-import all models so their tables register with Base.metadata
import models.bond            # noqa: F401
import models.certificate     # noqa: F401
import models.credential      # noqa: F401
import models.energy_event    # noqa: F401
import models.link            # noqa: F401
import models.node_event      # noqa: F401
import models.payment_event   # noqa: F401
import models.phone_verification  # noqa: F401
import models.reward          # noqa: F401
import models.space           # noqa: F401
import models.subscription    # noqa: F401
import models.token_pool      # noqa: F401
import models.transaction     # noqa: F401
import models.vault_receipt   # noqa: F401
import models.wallet_tx       # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (SQL script generation)."""
    url = HeliosConfig.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = HeliosConfig.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
