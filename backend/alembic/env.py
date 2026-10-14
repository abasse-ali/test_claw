from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from app.core.database import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in the section
# [alembic:config]
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.attributes.get('configure_logger', True):
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be pulled from the context object as follows:
# my_important_option = context.get_x_argument()(name='my_important_option')

# my 'env.py' script is created with 'alembic revision --autogenerate'
# and uses this section of code to get a DB API connection
# when invoked via 'alembic -x connect-url foo' or similar.

def get_url():
    from app.core.config import get_settings
    settings = get_settings()
    return settings.database_url


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is also acceptable
    here alongside a URL, which allows for other forms
    of 'startup' access to the DB, a la 'scripts.py' - scripts.py
    might use e.g. the 'arg' directive to get at the "url" arg
    that was set via 'python -m alembic -x connect-url foo'.
    """
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    engine = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
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