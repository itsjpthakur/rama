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
"""security converge saved queries

Revision ID: e38177dbf641
Revises: a8173232b786
Create Date: 2020-11-20 14:24:03.643031

"""

# revision identifiers, used by Alembic.
revision = "e38177dbf641"
down_revision = "a8173232b786"


from alembic import op  # noqa: E402
from sqlalchemy.exc import SQLAlchemyError  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from rama.migrations.shared.security_converge import (  # noqa: E402
    add_pvms,
    get_reversed_new_pvms,
    get_reversed_pvm_map,
    migrate_roles,
    Pvm,
)

NEW_PVMS = {
    "SavedQuery": (
        "can_read",
        "can_write",
    )
}
PVM_MAP = {
    Pvm("SavedQueryView", "can_list"): (Pvm("SavedQuery", "can_read"),),
    Pvm("SavedQueryView", "can_show"): (Pvm("SavedQuery", "can_read"),),
    Pvm(
        "SavedQueryView",
        "can_add",
    ): (Pvm("SavedQuery", "can_write"),),
    Pvm(
        "SavedQueryView",
        "can_edit",
    ): (Pvm("SavedQuery", "can_write"),),
    Pvm(
        "SavedQueryView",
        "can_delete",
    ): (Pvm("SavedQuery", "can_write"),),
    Pvm(
        "SavedQueryView",
        "muldelete",
    ): (Pvm("SavedQuery", "can_write"),),
    Pvm(
        "SavedQueryView",
        "can_mulexport",
    ): (Pvm("SavedQuery", "can_read"),),
    Pvm(
        "SavedQueryViewApi",
        "can_show",
    ): (Pvm("SavedQuery", "can_read"),),
    Pvm(
        "SavedQueryViewApi",
        "can_edit",
    ): (Pvm("SavedQuery", "can_write"),),
    Pvm(
        "SavedQueryViewApi",
        "can_list",
    ): (Pvm("SavedQuery", "can_read"),),
    Pvm(
        "SavedQueryViewApi",
        "can_add",
    ): (Pvm("SavedQuery", "can_write"),),
    Pvm(
        "SavedQueryViewApi",
        "muldelete",
    ): (Pvm("SavedQuery", "can_write"),),
}


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    # Add the new permissions on the migration itself
    add_pvms(session, NEW_PVMS)
    migrate_roles(session, PVM_MAP)
    try:
        session.commit()
    except SQLAlchemyError as ex:
        print(f"An error occurred while upgrading permissions: {ex}")
        session.rollback()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    # Add the old permissions on the migration itself
    add_pvms(session, get_reversed_new_pvms(PVM_MAP))
    migrate_roles(session, get_reversed_pvm_map(PVM_MAP))
    try:
        session.commit()
    except SQLAlchemyError as ex:
        print(f"An error occurred while downgrading permissions: {ex}")
        session.rollback()
    pass
