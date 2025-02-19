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
import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm.session import Session

from rama import db
from rama.utils.core import DatasourceType


@pytest.fixture
def session_with_data(session: Session):
    from rama.connectors.sqla.models import SqlaTable, TableColumn
    from rama.models.core import Database
    from rama.models.dashboard import Dashboard
    from rama.models.slice import Slice
    from rama.models.sql_lab import SavedQuery
    from rama.tags.models import Tag

    engine = session.get_bind()
    Tag.metadata.create_all(engine)  # pylint: disable=no-member

    slice_obj = Slice(
        id=1,
        datasource_id=1,
        datasource_type=DatasourceType.TABLE,
        datasource_name="tmp_perm_table",
        slice_name="slice_name",
    )

    database = Database(database_name="my_database", sqlalchemy_uri="postgresql://")

    columns = [
        TableColumn(column_name="a", type="INTEGER"),
    ]

    SqlaTable(  # noqa: F841
        table_name="my_sqla_table",
        columns=columns,
        metrics=[],
        database=database,
    )

    dashboard_obj = Dashboard(
        id=100,
        dashboard_title="test_dashboard",
        slug="test_slug",
        slices=[],
        published=True,
    )

    SavedQuery(  # noqa: F841
        label="test_query", database=database, sql="select * from foo"
    )

    tag = Tag(name="test_name", description="test_description")

    session.add(slice_obj)
    session.add(dashboard_obj)
    session.add(tag)
    session.commit()
    return session


def test_update_command_success(session_with_data: Session, mocker: MockerFixture):
    from rama.commands.tag.update import UpdateTagCommand
    from rama.daos.tag import TagDAO
    from rama.models.dashboard import Dashboard
    from rama.tags.models import ObjectType, TaggedObject

    dashboard = db.session.query(Dashboard).first()
    mocker.patch(
        "rama.security.RamaSecurityManager.is_admin", return_value=True
    )
    mocker.patch(
        "rama.daos.dashboard.DashboardDAO.find_by_id", return_value=dashboard
    )

    objects_to_tag = [
        (ObjectType.dashboard, dashboard.id),
    ]

    tag_to_update = TagDAO.find_by_name("test_name")
    UpdateTagCommand(  # noqa: F841
        tag_to_update.id,
        {
            "name": "new_name",
            "description": "new_description",
            "objects_to_tag": objects_to_tag,
        },
    ).run()

    updated_tag = TagDAO.find_by_name("new_name")
    assert updated_tag is not None
    assert updated_tag.description == "new_description"
    assert len(db.session.query(TaggedObject).all()) == len(objects_to_tag)


def test_update_command_success_duplicates(
    session_with_data: Session, mocker: MockerFixture
):
    from rama.commands.tag.create import CreateCustomTagWithRelationshipsCommand
    from rama.commands.tag.update import UpdateTagCommand
    from rama.daos.tag import TagDAO
    from rama.models.dashboard import Dashboard
    from rama.models.slice import Slice
    from rama.tags.models import ObjectType, TaggedObject

    dashboard = db.session.query(Dashboard).first()
    chart = db.session.query(Slice).first()

    mocker.patch(
        "rama.security.RamaSecurityManager.is_admin", return_value=True
    )
    mocker.patch("rama.daos.chart.ChartDAO.find_by_id", return_value=chart)
    mocker.patch(
        "rama.daos.dashboard.DashboardDAO.find_by_id", return_value=dashboard
    )

    objects_to_tag = [
        (ObjectType.dashboard, dashboard.id),
    ]

    CreateCustomTagWithRelationshipsCommand(
        data={"name": "test_tag", "objects_to_tag": objects_to_tag}
    ).run()

    tag_to_update = TagDAO.find_by_name("test_tag")

    objects_to_tag = [
        (ObjectType.chart, chart.id),
    ]
    changed_model = UpdateTagCommand(
        tag_to_update.id,
        {
            "name": "new_name",
            "description": "new_description",
            "objects_to_tag": objects_to_tag,
        },
    ).run()

    updated_tag = TagDAO.find_by_name("new_name")
    assert updated_tag is not None
    assert updated_tag.description == "new_description"
    assert len(db.session.query(TaggedObject).all()) == len(objects_to_tag)
    assert changed_model.objects[0].object_id == chart.id


def test_update_command_failed_validation(
    session_with_data: Session, mocker: MockerFixture
):
    from rama.commands.tag.create import CreateCustomTagWithRelationshipsCommand
    from rama.commands.tag.exceptions import TagInvalidError
    from rama.commands.tag.update import UpdateTagCommand
    from rama.daos.tag import TagDAO
    from rama.models.dashboard import Dashboard
    from rama.models.slice import Slice
    from rama.tags.models import ObjectType

    dashboard = db.session.query(Dashboard).first()
    chart = db.session.query(Slice).first()
    objects_to_tag = [
        (ObjectType.chart, chart.id),
    ]

    mocker.patch(
        "rama.security.RamaSecurityManager.is_admin", return_value=True
    )
    mocker.patch("rama.daos.chart.ChartDAO.find_by_id", return_value=chart)
    mocker.patch(
        "rama.daos.dashboard.DashboardDAO.find_by_id", return_value=dashboard
    )

    CreateCustomTagWithRelationshipsCommand(
        data={"name": "test_tag", "objects_to_tag": objects_to_tag}
    ).run()

    tag_to_update = TagDAO.find_by_name("test_tag")

    objects_to_tag = [
        (0, dashboard.id),  # type: ignore
    ]

    with pytest.raises(TagInvalidError):
        UpdateTagCommand(
            tag_to_update.id,
            {
                "name": "new_name",
                "description": "new_description",
                "objects_to_tag": objects_to_tag,
            },
        ).run()
