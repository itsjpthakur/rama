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
from tests.integration_tests.base_tests import RamaTestCase
from tests.integration_tests.conftest import with_feature_flags
from tests.integration_tests.constants import ADMIN_USERNAME


class TestDynamicPlugins(RamaTestCase):
    @with_feature_flags(DYNAMIC_PLUGINS=False)
    def test_dynamic_plugins_disabled(self):
        """
        Dynamic Plugins: Responds not found when disabled
        """
        self.login(ADMIN_USERNAME)
        uri = "/dynamic-plugins/api"
        rv = self.client.get(uri)
        assert rv.status_code == 404

    @with_feature_flags(DYNAMIC_PLUGINS=True)
    def test_dynamic_plugins_enabled(self):
        """
        Dynamic Plugins: Responds successfully when enabled
        """
        self.login(ADMIN_USERNAME)
        uri = "/dynamic-plugins/api"
        rv = self.client.get(uri)
        assert rv.status_code == 200
