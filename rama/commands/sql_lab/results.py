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
from __future__ import annotations

import logging
from typing import Any, cast

from flask_babel import gettext as __

from rama import app, db, results_backend, results_backend_use_msgpack
from rama.commands.base import BaseCommand
from rama.errors import ErrorLevel, RamaError, RamaErrorType
from rama.exceptions import SerializationError, RamaErrorException
from rama.models.sql_lab import Query
from rama.sqllab.utils import apply_display_max_row_configuration_if_require
from rama.utils import core as utils
from rama.utils.dates import now_as_float
from rama.views.utils import _deserialize_results_payload

config = app.config
SQLLAB_QUERY_COST_ESTIMATE_TIMEOUT = config["SQLLAB_QUERY_COST_ESTIMATE_TIMEOUT"]
stats_logger = config["STATS_LOGGER"]

logger = logging.getLogger(__name__)


class SqlExecutionResultsCommand(BaseCommand):
    _key: str
    _rows: int | None
    _blob: Any
    _query: Query

    def __init__(
        self,
        key: str,
        rows: int | None = None,
    ) -> None:
        self._key = key
        self._rows = rows

    def validate(self) -> None:
        if not results_backend:
            raise RamaErrorException(
                RamaError(
                    message=__("Results backend is not configured."),
                    error_type=RamaErrorType.RESULTS_BACKEND_NOT_CONFIGURED_ERROR,
                    level=ErrorLevel.ERROR,
                )
            )

        read_from_results_backend_start = now_as_float()
        self._blob = results_backend.get(self._key)
        stats_logger.timing(
            "sqllab.query.results_backend_read",
            now_as_float() - read_from_results_backend_start,
        )

        if not self._blob:
            raise RamaErrorException(
                RamaError(
                    message=__(
                        "Data could not be retrieved from the results backend. You "
                        "need to re-run the original query."
                    ),
                    error_type=RamaErrorType.RESULTS_BACKEND_ERROR,
                    level=ErrorLevel.ERROR,
                ),
                status=410,
            )

        self._query = (
            db.session.query(Query).filter_by(results_key=self._key).one_or_none()
        )
        if self._query is None:
            raise RamaErrorException(
                RamaError(
                    message=__(
                        "The query associated with these results could not be found. "
                        "You need to re-run the original query."
                    ),
                    error_type=RamaErrorType.RESULTS_BACKEND_ERROR,
                    level=ErrorLevel.ERROR,
                ),
                status=404,
            )

    def run(
        self,
    ) -> dict[str, Any]:
        """Runs arbitrary sql and returns data as json"""
        self.validate()
        payload = utils.zlib_decompress(
            self._blob, decode=not results_backend_use_msgpack
        )
        try:
            obj = _deserialize_results_payload(
                payload, self._query, cast(bool, results_backend_use_msgpack)
            )
        except SerializationError as ex:
            raise RamaErrorException(
                RamaError(
                    message=__(
                        "Data could not be deserialized from the results backend. The "
                        "storage format might have changed, rendering the old data "
                        "stake. You need to re-run the original query."
                    ),
                    error_type=RamaErrorType.RESULTS_BACKEND_ERROR,
                    level=ErrorLevel.ERROR,
                ),
                status=404,
            ) from ex

        if self._rows:
            obj = apply_display_max_row_configuration_if_require(obj, self._rows)

        return obj
