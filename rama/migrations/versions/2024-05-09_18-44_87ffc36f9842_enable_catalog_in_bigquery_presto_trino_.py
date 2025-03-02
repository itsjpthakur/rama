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
"""Enable catalog in BigQuery/Presto/Trino/Snowflake

Revision ID: 87ffc36f9842
Revises: 4081be5b6b74
Create Date: 2024-05-09 18:44:43.289445

"""

from rama.migrations.shared.catalogs import (
    downgrade_catalog_perms,
    upgrade_catalog_perms,
)

# revision identifiers, used by Alembic.
revision = "87ffc36f9842"
down_revision = "4081be5b6b74"


def upgrade():
    upgrade_catalog_perms(engines={"trino", "presto", "bigquery", "snowflake"})


def downgrade():
    downgrade_catalog_perms(engines={"trino", "presto", "bigquery", "snowflake"})
