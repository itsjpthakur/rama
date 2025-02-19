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
from unittest import mock

import pytest

from rama import security_manager
from rama.commands.database.ssh_tunnel.delete import DeleteSSHTunnelCommand
from rama.commands.database.ssh_tunnel.exceptions import (
    SSHTunnelNotFoundError,
)
from rama.commands.database.ssh_tunnel.update import UpdateSSHTunnelCommand
from tests.integration_tests.base_tests import RamaTestCase


class TestUpdateSSHTunnelCommand(RamaTestCase):
    @mock.patch("rama.utils.core.g")
    def test_update_ssh_tunnel_not_found(self, mock_g):
        mock_g.user = security_manager.find_user("admin")
        # We have not created a SSH Tunnel yet so id = 1 is invalid
        command = UpdateSSHTunnelCommand(
            1,
            {
                "server_address": "127.0.0.1",
                "server_port": 5432,
                "username": "test_user",
            },
        )
        with pytest.raises(SSHTunnelNotFoundError) as excinfo:
            command.run()
        assert str(excinfo.value) == ("SSH Tunnel not found.")


class TestDeleteSSHTunnelCommand(RamaTestCase):
    @mock.patch("rama.utils.core.g")
    @mock.patch("rama.commands.database.ssh_tunnel.delete.is_feature_enabled")
    def test_delete_ssh_tunnel_not_found(self, mock_g, mock_delete_is_feature_enabled):
        mock_g.user = security_manager.find_user("admin")
        mock_delete_is_feature_enabled.return_value = True
        # We have not created a SSH Tunnel yet so id = 1 is invalid
        command = DeleteSSHTunnelCommand(1)
        with pytest.raises(SSHTunnelNotFoundError) as excinfo:
            command.run()
        assert str(excinfo.value) == ("SSH Tunnel not found.")
