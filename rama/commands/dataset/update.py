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
from collections import Counter
from functools import partial
from typing import Any, Optional

from flask_appbuilder.models.sqla import Model
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from rama import security_manager
from rama.commands.base import BaseCommand, UpdateMixin
from rama.commands.dataset.exceptions import (
    DatabaseChangeValidationError,
    DatasetColumnNotFoundValidationError,
    DatasetColumnsDuplicateValidationError,
    DatasetColumnsExistsValidationError,
    DatasetExistsValidationError,
    DatasetForbiddenError,
    DatasetInvalidError,
    DatasetMetricsDuplicateValidationError,
    DatasetMetricsExistsValidationError,
    DatasetMetricsNotFoundValidationError,
    DatasetNotFoundError,
    DatasetUpdateFailedError,
)
from rama.connectors.sqla.models import SqlaTable
from rama.daos.dataset import DatasetDAO
from rama.exceptions import RamaSecurityException
from rama.sql_parse import Table
from rama.utils.decorators import on_error, transaction

logger = logging.getLogger(__name__)


class UpdateDatasetCommand(UpdateMixin, BaseCommand):
    def __init__(
        self,
        model_id: int,
        data: dict[str, Any],
        override_columns: Optional[bool] = False,
    ):
        self._model_id = model_id
        self._properties = data.copy()
        self._model: Optional[SqlaTable] = None
        self.override_columns = override_columns
        self._properties["override_columns"] = override_columns

    @transaction(
        on_error=partial(
            on_error,
            catches=(
                SQLAlchemyError,
                ValueError,
            ),
            reraise=DatasetUpdateFailedError,
        )
    )
    def run(self) -> Model:
        self.validate()
        assert self._model
        return DatasetDAO.update(self._model, attributes=self._properties)

    def validate(self) -> None:
        exceptions: list[ValidationError] = []
        owner_ids: Optional[list[int]] = self._properties.get("owners")

        # Validate/populate model exists
        self._model = DatasetDAO.find_by_id(self._model_id)
        if not self._model:
            raise DatasetNotFoundError()

        # Check ownership
        try:
            security_manager.raise_for_ownership(self._model)
        except RamaSecurityException as ex:
            raise DatasetForbiddenError() from ex

        database_id = self._properties.get("database")

        catalog = self._properties.get("catalog")
        if not catalog:
            catalog = self._properties["catalog"] = (
                self._model.database.get_default_catalog()
            )

        table = Table(
            self._properties.get("table_name"),  # type: ignore
            self._properties.get("schema"),
            catalog,
        )

        # Validate uniqueness
        if not DatasetDAO.validate_update_uniqueness(
            self._model.database,
            table,
            self._model_id,
        ):
            exceptions.append(DatasetExistsValidationError(table))

        # Validate/Populate database not allowed to change
        if database_id and database_id != self._model:
            exceptions.append(DatabaseChangeValidationError())

        # Validate/Populate owner
        try:
            owners = self.compute_owners(
                self._model.owners,
                owner_ids,
            )
            self._properties["owners"] = owners
        except ValidationError as ex:
            exceptions.append(ex)

        # Validate columns
        if columns := self._properties.get("columns"):
            self._validate_columns(columns, exceptions)

        # Validate metrics
        if metrics := self._properties.get("metrics"):
            self._validate_metrics(metrics, exceptions)

        if exceptions:
            raise DatasetInvalidError(exceptions=exceptions)

    def _validate_columns(
        self, columns: list[dict[str, Any]], exceptions: list[ValidationError]
    ) -> None:
        # Validate duplicates on data
        if self._get_duplicates(columns, "column_name"):
            exceptions.append(DatasetColumnsDuplicateValidationError())
        else:
            # validate invalid id's
            columns_ids: list[int] = [
                column["id"] for column in columns if "id" in column
            ]
            if not DatasetDAO.validate_columns_exist(self._model_id, columns_ids):
                exceptions.append(DatasetColumnNotFoundValidationError())

            # validate new column names uniqueness
            if not self.override_columns:
                columns_names: list[str] = [
                    column["column_name"] for column in columns if "id" not in column
                ]
                if not DatasetDAO.validate_columns_uniqueness(
                    self._model_id, columns_names
                ):
                    exceptions.append(DatasetColumnsExistsValidationError())

    def _validate_metrics(
        self, metrics: list[dict[str, Any]], exceptions: list[ValidationError]
    ) -> None:
        if self._get_duplicates(metrics, "metric_name"):
            exceptions.append(DatasetMetricsDuplicateValidationError())
        else:
            # validate invalid id's
            metrics_ids: list[int] = [
                metric["id"] for metric in metrics if "id" in metric
            ]
            if not DatasetDAO.validate_metrics_exist(self._model_id, metrics_ids):
                exceptions.append(DatasetMetricsNotFoundValidationError())
            # validate new metric names uniqueness
            metric_names: list[str] = [
                metric["metric_name"] for metric in metrics if "id" not in metric
            ]
            if not DatasetDAO.validate_metrics_uniqueness(self._model_id, metric_names):
                exceptions.append(DatasetMetricsExistsValidationError())

    @staticmethod
    def _get_duplicates(data: list[dict[str, Any]], key: str) -> list[str]:
        duplicates = [
            name
            for name, count in Counter([item[key] for item in data]).items()
            if count > 1
        ]
        return duplicates
