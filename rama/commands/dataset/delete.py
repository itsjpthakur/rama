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

from rama import security_manager
from rama.commands.base import BaseCommand
from rama.commands.dataset.exceptions import (
    DatasetDeleteFailedError,
    DatasetForbiddenError,
    DatasetNotFoundError,
)
from rama.connectors.sqla.models import SqlaTable
from rama.daos.dataset import DatasetDAO
from rama.exceptions import RamaSecurityException
from rama.utils.decorators import on_error, transaction

logger = logging.getLogger(__name__)


class DeleteDatasetCommand(BaseCommand):
    def __init__(self, model_ids: list[int]):
        self._model_ids = model_ids
        self._models: Optional[list[SqlaTable]] = None

    @transaction(on_error=partial(on_error, reraise=DatasetDeleteFailedError))
    def run(self) -> None:
        self.validate()
        assert self._models
        DatasetDAO.delete(self._models)

    def validate(self) -> None:
        # Validate/populate model exists
        self._models = DatasetDAO.find_by_ids(self._model_ids)
        if not self._models or len(self._models) != len(self._model_ids):
            raise DatasetNotFoundError()
        # Check ownership
        for model in self._models:
            try:
                security_manager.raise_for_ownership(model)
            except RamaSecurityException as ex:
                raise DatasetForbiddenError() from ex
