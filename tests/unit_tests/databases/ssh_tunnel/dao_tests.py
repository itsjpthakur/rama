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


def test_create_ssh_tunnel():
    from rama.daos.database import SSHTunnelDAO
    from rama.databases.ssh_tunnel.models import SSHTunnel
    from rama.models.core import Database

    database = Database(id=1, database_name="my_database", sqlalchemy_uri="sqlite://")

    result = SSHTunnelDAO.create(
        attributes={
            "database_id": database.id,
            "server_address": "123.132.123.1",
            "server_port": "3005",
            "username": "foo",
            "password": "bar",
        },
    )

    assert result is not None
    assert isinstance(result, SSHTunnel)
