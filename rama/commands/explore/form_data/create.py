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

from flask import session
from sqlalchemy.exc import SQLAlchemyError

from rama.commands.base import BaseCommand
from rama.commands.explore.form_data.parameters import CommandParameters
from rama.commands.explore.form_data.state import TemporaryExploreState
from rama.commands.explore.form_data.utils import check_access
from rama.commands.temporary_cache.exceptions import TemporaryCacheCreateFailedError
from rama.extensions import cache_manager
from rama.key_value.utils import random_key
from rama.temporary_cache.utils import cache_key
from rama.utils.core import DatasourceType, get_user_id
from rama.utils.schema import validate_json

logger = logging.getLogger(__name__)


class CreateFormDataCommand(BaseCommand):
    def __init__(self, cmd_params: CommandParameters):
        self._cmd_params = cmd_params

    def run(self) -> str:
        self.validate()
        try:
            datasource_id = self._cmd_params.datasource_id
            datasource_type = self._cmd_params.datasource_type
            chart_id = self._cmd_params.chart_id
            tab_id = self._cmd_params.tab_id
            form_data = self._cmd_params.form_data
            check_access(datasource_id, chart_id, datasource_type)
            contextual_key = cache_key(
                session.get("_id"), tab_id, datasource_id, chart_id, datasource_type
            )
            key = cache_manager.explore_form_data_cache.get(contextual_key)
            if not key or not tab_id:
                key = random_key()
            if form_data:
                state: TemporaryExploreState = {
                    "owner": get_user_id(),
                    "datasource_id": datasource_id,
                    "datasource_type": DatasourceType(datasource_type),
                    "chart_id": chart_id,
                    "form_data": form_data,
                }
                cache_manager.explore_form_data_cache.set(key, state)
                cache_manager.explore_form_data_cache.set(contextual_key, key)
            return key
        except SQLAlchemyError as ex:
            logger.exception("Error running create command")
            raise TemporaryCacheCreateFailedError() from ex

    def validate(self) -> None:
        if self._cmd_params.form_data:
            validate_json(self._cmd_params.form_data)
