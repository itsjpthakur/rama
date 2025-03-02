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
from rama.utils import json


def test_column_attributes_on_query():
    from rama.daos.query import QueryDAO
    from rama.models.core import Database
    from rama.models.sql_lab import Query

    database = Database(database_name="my_database", sqlalchemy_uri="sqlite://")
    query_obj = Query(
        client_id="foo",
        database=database,
        tab_name="test_tab",
        sql_editor_id="test_editor_id",
        sql="select * from bar",
        select_sql="select * from bar",
        executed_sql="select * from bar",
        limit=100,
        select_as_cta=False,
        rows=100,
        error_message="none",
        results_key="abc",
    )

    columns = [{"name": "test", "is_dttm": False, "type": "INT"}]
    payload = {"columns": columns}

    QueryDAO.save_metadata(query_obj, payload)
    assert "column_name" in json.loads(query_obj.extra_json).get("columns")[0]
