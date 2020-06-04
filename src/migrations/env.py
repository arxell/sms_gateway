import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
config = context.config
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata


def _get_modelbase():
    from app.database.base import ModelBase

    return ModelBase


target_metadata = _get_modelbase().metadata


def _get_url():
    from app.database.base import get_connection_url

    return get_connection_url()


url = _get_url()


def run_migrations_offline():
    # allows to see generated SQL
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
