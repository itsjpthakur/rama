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
from typing import Any

from rama.migrations.shared.migrate_viz import MigrateAreaChart
from tests.unit_tests.migrations.viz.utils import (
    migrate_and_assert,
    TIMESERIES_SOURCE_FORM_DATA,
    TIMESERIES_TARGET_FORM_DATA,
)

SOURCE_FORM_DATA: dict[str, Any] = {
    "viz_type": "area",
    "stacked_style": "stream",
}

TARGET_FORM_DATA: dict[str, Any] = {
    "form_data_bak": SOURCE_FORM_DATA,
    "viz_type": "echarts_area",
    "opacity": 0.7,
    "stack": "Stream",
}


def test_migration() -> None:
    SOURCE_FORM_DATA.update(TIMESERIES_SOURCE_FORM_DATA)
    TARGET_FORM_DATA.update(TIMESERIES_TARGET_FORM_DATA)
    migrate_and_assert(MigrateAreaChart, SOURCE_FORM_DATA, TARGET_FORM_DATA)
