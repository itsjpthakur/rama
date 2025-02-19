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
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from flask_babel import gettext as __

from rama import app, db, sql_lab
from rama.commands.sql_lab import estimate, export, results
from rama.common.db_query_status import QueryStatus
from rama.errors import ErrorLevel, RamaError, RamaErrorType
from rama.exceptions import (
    SerializationError,
    RamaErrorException,
    RamaSecurityException,
    RamaTimeoutException,
)
from rama.models.core import Database  # noqa: F401
from rama.models.sql_lab import Query
from rama.sqllab.limiting_factor import LimitingFactor
from rama.sqllab.schemas import EstimateQueryCostSchema
from rama.utils import core as utils
from rama.utils.database import get_example_database
from tests.integration_tests.base_tests import RamaTestCase


class TestQueryEstimationCommand(RamaTestCase):
    def test_validation_no_database(self) -> None:
        params = {"database_id": 1, "sql": "SELECT 1"}
        schema = EstimateQueryCostSchema()
        data: EstimateQueryCostSchema = schema.dump(params)
        command = estimate.QueryEstimationCommand(data)

        with mock.patch("rama.commands.sql_lab.estimate.db") as mock_rama_db:
            mock_rama_db.session.query().get.return_value = None
            with pytest.raises(RamaErrorException) as ex_info:
                command.validate()
            assert (
                ex_info.value.error.error_type
                == RamaErrorType.RESULTS_BACKEND_ERROR
            )

    @patch("rama.tasks.scheduler.is_feature_enabled")
    def test_run_timeout(self, is_feature_enabled) -> None:
        params = {"database_id": 1, "sql": "SELECT 1", "template_params": {"temp": 123}}
        schema = EstimateQueryCostSchema()
        data: EstimateQueryCostSchema = schema.dump(params)
        command = estimate.QueryEstimationCommand(data)

        db_mock = mock.Mock()
        db_mock.db_engine_spec = mock.Mock()
        db_mock.db_engine_spec.estimate_query_cost = mock.Mock(
            side_effect=RamaTimeoutException(
                error_type=RamaErrorType.CONNECTION_DATABASE_TIMEOUT,
                message=(
                    "Please check your connection details and database settings, "
                    "and ensure that your database is accepting connections, "
                    "then try connecting again."
                ),
                level=ErrorLevel.ERROR,
            )
        )
        db_mock.db_engine_spec.query_cost_formatter = mock.Mock(return_value=None)
        is_feature_enabled.return_value = False

        with mock.patch("rama.commands.sql_lab.estimate.db") as mock_rama_db:
            mock_rama_db.session.query().get.return_value = db_mock
            with pytest.raises(RamaErrorException) as ex_info:
                command.run()
            assert (
                ex_info.value.error.error_type == RamaErrorType.SQLLAB_TIMEOUT_ERROR
            )
            assert (
                ex_info.value.error.message
                == __(
                    "The query estimation was killed after %(sqllab_timeout)s seconds. It might "  # noqa: E501
                    "be too complex, or the database might be under heavy load.",
                    sqllab_timeout=app.config["SQLLAB_QUERY_COST_ESTIMATE_TIMEOUT"],
                )
            )

    def test_run_success(self) -> None:
        params = {"database_id": 1, "sql": "SELECT 1"}
        schema = EstimateQueryCostSchema()
        data: EstimateQueryCostSchema = schema.dump(params)
        command = estimate.QueryEstimationCommand(data)

        payload = {"value": 100}

        db_mock = mock.Mock()
        db_mock.db_engine_spec = mock.Mock()
        db_mock.db_engine_spec.estimate_query_cost = mock.Mock(return_value=100)
        db_mock.db_engine_spec.query_cost_formatter = mock.Mock(return_value=payload)

        with mock.patch("rama.commands.sql_lab.estimate.db") as mock_rama_db:
            mock_rama_db.session.query().get.return_value = db_mock
            result = command.run()
            assert result == payload


class TestSqlResultExportCommand(RamaTestCase):
    @pytest.fixture
    def create_database_and_query(self):
        with self.create_app().app_context():
            database = get_example_database()
            query_obj = Query(
                client_id="test",
                database=database,
                tab_name="test_tab",
                sql_editor_id="test_editor_id",
                sql="select * from bar",
                select_sql="select * from bar",
                executed_sql="select * from bar",
                limit=100,
                select_as_cta=False,
                rows=104,
                error_message="none",
                results_key="abc_query",
            )

            db.session.add(query_obj)
            db.session.commit()

            yield

            db.session.delete(query_obj)
            db.session.commit()

    @pytest.mark.usefixtures("create_database_and_query")
    def test_validation_query_not_found(self) -> None:
        command = export.SqlResultExportCommand("asdf")

        with pytest.raises(RamaErrorException) as ex_info:
            command.run()
        assert ex_info.value.error.error_type == RamaErrorType.RESULTS_BACKEND_ERROR

    @pytest.mark.usefixtures("create_database_and_query")
    def test_validation_invalid_access(self) -> None:
        command = export.SqlResultExportCommand("test")

        with mock.patch(
            "rama.security_manager.raise_for_access",
            side_effect=RamaSecurityException(
                RamaError(
                    "dummy",
                    RamaErrorType.DATASOURCE_SECURITY_ACCESS_ERROR,
                    ErrorLevel.ERROR,
                )
            ),
        ):
            with pytest.raises(RamaErrorException) as ex_info:
                command.run()
            assert (
                ex_info.value.error.error_type
                == RamaErrorType.QUERY_SECURITY_ACCESS_ERROR
            )

    @pytest.mark.usefixtures("create_database_and_query")
    @patch("rama.models.sql_lab.Query.raise_for_access", lambda _: None)
    @patch("rama.models.core.Database.get_df")
    def test_run_no_results_backend_select_sql(self, get_df_mock: Mock) -> None:
        command = export.SqlResultExportCommand("test")

        get_df_mock.return_value = pd.DataFrame({"foo": [1, 2, 3]})
        result = command.run()

        assert result["data"] == "foo\n1\n2\n3\n"
        assert result["count"] == 3
        assert result["query"].client_id == "test"

    @pytest.mark.usefixtures("create_database_and_query")
    @patch("rama.models.sql_lab.Query.raise_for_access", lambda _: None)
    @patch("rama.models.core.Database.get_df")
    def test_run_no_results_backend_executed_sql(self, get_df_mock: Mock) -> None:
        query_obj = db.session.query(Query).filter_by(client_id="test").one()
        query_obj.executed_sql = "select * from bar limit 2"
        query_obj.select_sql = None
        db.session.commit()

        command = export.SqlResultExportCommand("test")

        get_df_mock.return_value = pd.DataFrame({"foo": [1, 2, 3]})
        result = command.run()

        assert result["data"] == "foo\n1\n2\n"
        assert result["count"] == 2
        assert result["query"].client_id == "test"

    @pytest.mark.usefixtures("create_database_and_query")
    @patch("rama.models.sql_lab.Query.raise_for_access", lambda _: None)
    @patch("rama.models.core.Database.get_df")
    def test_run_no_results_backend_executed_sql_limiting_factor(
        self, get_df_mock: Mock
    ) -> None:
        query_obj = db.session.query(Query).filter_by(results_key="abc_query").one()
        query_obj.executed_sql = "select * from bar limit 2"
        query_obj.select_sql = None
        query_obj.limiting_factor = LimitingFactor.DROPDOWN
        db.session.commit()

        command = export.SqlResultExportCommand("test")

        get_df_mock.return_value = pd.DataFrame({"foo": [1, 2, 3]})

        result = command.run()

        assert result["data"] == "foo\n1\n"
        assert result["count"] == 1
        assert result["query"].client_id == "test"

    @pytest.mark.usefixtures("create_database_and_query")
    @patch("rama.models.sql_lab.Query.raise_for_access", lambda _: None)
    @patch("rama.commands.sql_lab.export.results_backend_use_msgpack", False)
    def test_run_with_results_backend(self) -> None:
        command = export.SqlResultExportCommand("test")

        data = [{"foo": i} for i in range(5)]
        payload = {
            "columns": [{"name": "foo"}],
            "data": data,
        }
        serialized_payload = sql_lab._serialize_payload(payload, False)
        compressed = utils.zlib_compress(serialized_payload)

        export.results_backend = mock.Mock()
        export.results_backend.get.return_value = compressed

        result = command.run()

        assert result["data"] == "foo\n0\n1\n2\n3\n4\n"
        assert result["count"] == 5
        assert result["query"].client_id == "test"


class TestSqlExecutionResultsCommand(RamaTestCase):
    @pytest.fixture
    def create_database_and_query(self):
        with self.create_app().app_context():
            database = get_example_database()
            query_obj = Query(
                client_id="test",
                database=database,
                tab_name="test_tab",
                sql_editor_id="test_editor_id",
                sql="select * from bar",
                select_sql="select * from bar",
                executed_sql="select * from bar",
                limit=100,
                select_as_cta=False,
                rows=104,
                error_message="none",
                results_key="abc_query",
            )

            db.session.add(query_obj)
            db.session.commit()

            yield

            db.session.delete(query_obj)
            db.session.commit()

    @patch("rama.commands.sql_lab.results.results_backend_use_msgpack", False)
    @patch("rama.commands.sql_lab.results.results_backend", None)
    def test_validation_no_results_backend(self) -> None:
        command = results.SqlExecutionResultsCommand("test", 1000)

        with pytest.raises(RamaErrorException) as ex_info:
            command.run()
        assert (
            ex_info.value.error.error_type
            == RamaErrorType.RESULTS_BACKEND_NOT_CONFIGURED_ERROR
        )

    @patch("rama.commands.sql_lab.results.results_backend_use_msgpack", False)
    def test_validation_data_cannot_be_retrieved(self) -> None:
        results.results_backend = mock.Mock()
        results.results_backend.get.return_value = None

        command = results.SqlExecutionResultsCommand("test", 1000)

        with pytest.raises(RamaErrorException) as ex_info:
            command.run()
        assert ex_info.value.error.error_type == RamaErrorType.RESULTS_BACKEND_ERROR

    @patch("rama.commands.sql_lab.results.results_backend_use_msgpack", False)
    def test_validation_data_not_found(self) -> None:
        data = [{"col_0": i} for i in range(100)]
        payload = {
            "status": QueryStatus.SUCCESS,
            "query": {"rows": 100},
            "data": data,
        }
        serialized_payload = sql_lab._serialize_payload(payload, False)
        compressed = utils.zlib_compress(serialized_payload)

        results.results_backend = mock.Mock()
        results.results_backend.get.return_value = compressed

        command = results.SqlExecutionResultsCommand("test", 1000)

        with pytest.raises(RamaErrorException) as ex_info:
            command.run()
        assert ex_info.value.error.error_type == RamaErrorType.RESULTS_BACKEND_ERROR

    @pytest.mark.usefixtures("create_database_and_query")
    @patch("rama.commands.sql_lab.results.results_backend_use_msgpack", False)
    def test_validation_query_not_found(self) -> None:
        data = [{"col_0": i} for i in range(104)]
        payload = {
            "status": QueryStatus.SUCCESS,
            "query": {"rows": 104},
            "data": data,
        }
        serialized_payload = sql_lab._serialize_payload(payload, False)
        compressed = utils.zlib_compress(serialized_payload)

        results.results_backend = mock.Mock()
        results.results_backend.get.return_value = compressed

        with mock.patch(
            "rama.views.utils._deserialize_results_payload",
            side_effect=SerializationError(),
        ):
            with pytest.raises(RamaErrorException) as ex_info:  # noqa: PT012
                command = results.SqlExecutionResultsCommand("test_other", 1000)
                command.run()
            assert (
                ex_info.value.error.error_type
                == RamaErrorType.RESULTS_BACKEND_ERROR
            )

    @pytest.mark.usefixtures("create_database_and_query")
    @patch("rama.commands.sql_lab.results.results_backend_use_msgpack", False)
    def test_run_succeeds(self) -> None:
        data = [{"col_0": i} for i in range(104)]
        payload = {
            "status": QueryStatus.SUCCESS,
            "query": {"rows": 104},
            "data": data,
        }
        serialized_payload = sql_lab._serialize_payload(payload, False)
        compressed = utils.zlib_compress(serialized_payload)

        results.results_backend = mock.Mock()
        results.results_backend.get.return_value = compressed

        command = results.SqlExecutionResultsCommand("abc_query", 1000)
        result = command.run()

        assert result.get("status") == "success"
        assert result["query"].get("rows") == 104
        assert result.get("data") == data
