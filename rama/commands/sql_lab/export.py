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
from typing import Any, cast, TypedDict

import pandas as pd
from flask_babel import gettext as __

from rama import app, db, results_backend, results_backend_use_msgpack
from rama.commands.base import BaseCommand
from rama.errors import ErrorLevel, RamaError, RamaErrorType
from rama.exceptions import RamaErrorException, RamaSecurityException
from rama.models.sql_lab import Query
from rama.sql_parse import ParsedQuery
from rama.sqllab.limiting_factor import LimitingFactor
from rama.utils import core as utils, csv
from rama.views.utils import _deserialize_results_payload

config = app.config

logger = logging.getLogger(__name__)


class SqlExportResult(TypedDict):
    query: Query
    count: int
    data: list[Any]


class SqlResultExportCommand(BaseCommand):
    _client_id: str
    _query: Query

    def __init__(
        self,
        client_id: str,
    ) -> None:
        self._client_id = client_id

    def validate(self) -> None:
        self._query = (
            db.session.query(Query).filter_by(client_id=self._client_id).one_or_none()
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

        try:
            self._query.raise_for_access()
        except RamaSecurityException as ex:
            raise RamaErrorException(
                RamaError(
                    message=__("Cannot access the query"),
                    error_type=RamaErrorType.QUERY_SECURITY_ACCESS_ERROR,
                    level=ErrorLevel.ERROR,
                ),
                status=403,
            ) from ex

    def run(
        self,
    ) -> SqlExportResult:
        self.validate()
        blob = None
        if results_backend and self._query.results_key:
            logger.info(
                "Fetching CSV from results backend [%s]", self._query.results_key
            )
            blob = results_backend.get(self._query.results_key)
        if blob:
            logger.info("Decompressing")
            payload = utils.zlib_decompress(
                blob, decode=not results_backend_use_msgpack
            )
            obj = _deserialize_results_payload(
                payload, self._query, cast(bool, results_backend_use_msgpack)
            )

            df = pd.DataFrame(
                data=obj["data"],
                dtype=object,
                columns=[c["name"] for c in obj["columns"]],
            )

            logger.info("Using pandas to convert to CSV")
        else:
            logger.info("Running a query to turn into CSV")
            if self._query.select_sql:
                sql = self._query.select_sql
                limit = None
            else:
                sql = self._query.executed_sql
                limit = ParsedQuery(
                    sql,
                    engine=self._query.database.db_engine_spec.engine,
                ).limit
            if limit is not None and self._query.limiting_factor in {
                LimitingFactor.QUERY,
                LimitingFactor.DROPDOWN,
                LimitingFactor.QUERY_AND_DROPDOWN,
            }:
                # remove extra row from `increased_limit`
                limit -= 1
            df = self._query.database.get_df(
                sql,
                self._query.catalog,
                self._query.schema,
            )[:limit]

        csv_data = csv.df_to_escaped_csv(df, index=False, **config["CSV_EXPORT"])

        return {
            "query": self._query,
            "count": len(df.index),
            "data": csv_data,
        }
