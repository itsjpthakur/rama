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
from functools import partial
from typing import Optional

from flask_appbuilder.models.sqla import Model

from rama import security_manager
from rama.commands.base import BaseCommand
from rama.commands.dataset.exceptions import (
    DatasetForbiddenError,
    DatasetNotFoundError,
    DatasetRefreshFailedError,
)
from rama.connectors.sqla.models import SqlaTable
from rama.daos.dataset import DatasetDAO
from rama.exceptions import RamaSecurityException
from rama.utils.decorators import on_error, transaction

logger = logging.getLogger(__name__)


class RefreshDatasetCommand(BaseCommand):
    def __init__(self, model_id: int):
        self._model_id = model_id
        self._model: Optional[SqlaTable] = None

    @transaction(on_error=partial(on_error, reraise=DatasetRefreshFailedError))
    def run(self) -> Model:
        self.validate()
        assert self._model
        self._model.fetch_metadata()
        return self._model

    def validate(self) -> None:
        # Validate/populate model exists
        self._model = DatasetDAO.find_by_id(self._model_id)
        if not self._model:
            raise DatasetNotFoundError()
        # Check ownership
        try:
            security_manager.raise_for_ownership(self._model)
        except RamaSecurityException as ex:
            raise DatasetForbiddenError() from ex
