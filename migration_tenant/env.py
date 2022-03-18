from __future__ import with_statement

import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context
from sqlalchemy import engine_from_config, pool, MetaData, Table, ForeignKeyConstraint
from app import db
from app.models import User

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option(
    'sqlalchemy.url',
    str(current_app.extensions['migrate'].db.get_engine().url).replace(
        '%', '%%'))
target_metadata = current_app.extensions['migrate'].db.metadata
domains = []

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()

def include_schemas(names):
    # produce an include object function that filters on the given schemas
    def include_object(object, name, type_, reflected, compare_to):
        if type_ == "table":
            return object.schema in names
        return True
    return include_object

def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        return object.schema in [None]
    return True

def include_name(name, type_, parent_names):
    if type_ == "table":
        return name in ['doctors']
    else:
        return True

def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html

    engine = engine_from_config(
                config.get_section(config.config_ini_section),
                prefix='sqlalchemy.',
                poolclass=pool.NullPool)

    # schemas = set([prototype_schema,None])

    connection = engine.connect()

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True, #schemas,
        # include_object=include_schemas([None,prototype_schema])
        include_object=include_object,
        include_name = include_name,
    )

    try:
        # get the schema names
        # tenant_schemas = [row[0] for row in connection.execute(get_schemas_query)]
        users = User.query.all()
        for user in users:
            domains.append(user.username)
        # domains.append('public')
        for domain in domains:
            print('migrating Users -> '+ domain)
            connection.execute('set search_path to "{}"'.format(domain))
            with context.begin_transaction():
                context.run_migrations()

    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
