# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import logging
import time
from logging.config import fileConfig

from alembic import context
from alembic.operations.ops import MigrationScript
from alembic.runtime.migration import MigrationContext
from flask import current_app
from flask_appbuilder import Base
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if not current_app.config["ALEMBIC_SKIP_LOG_CONFIG"]:
    # Skip loading logger config if the user has this config set
    fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

DATABASE_URI = current_app.config["SQLALCHEMY_DATABASE_URI"]
if "sqlite" in DATABASE_URI:
    logger.warning(
        "SQLite Database support for metadata databases will \
        be removed in a future version of Rama."
    )
# Escape % chars in the database URI to avoid interpolation errors in ConfigParser
escaped_uri = DATABASE_URI.replace("%", "%%")
config.set_main_option("sqlalchemy.url", escaped_uri)
target_metadata = Base.metadata  # pylint: disable=no-member


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def print_duration(start_time: float) -> None:
    logger.info(
        "Migration scripts completed. Duration: %s",
        time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)),
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    start_time = time.time()
    logger.info("Starting the migration scripts.")

    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()
    print_duration(start_time)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    start_time = time.time()
    logger.info("Starting the migration scripts.")

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: https://alembic.sqlalchemy.org/en/latest/cookbook.html
    def process_revision_directives(  # pylint: disable=redefined-outer-name, unused-argument
        context: MigrationContext, revision: str, directives: list[MigrationScript]
    ) -> None:
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    connection = engine.connect()
    kwargs = {}
    if engine.name in ("sqlite", "mysql"):
        kwargs = {"transaction_per_migration": True, "transactional_ddl": True}
    if configure_args := current_app.extensions["migrate"].configure_args:
        kwargs.update(configure_args)

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # compare_type=True,
        process_revision_directives=process_revision_directives,
        **kwargs,
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
        print_duration(start_time)
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
