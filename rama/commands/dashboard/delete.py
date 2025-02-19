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

from flask_babel import lazy_gettext as _

from rama import security_manager
from rama.commands.base import BaseCommand
from rama.commands.dashboard.exceptions import (
    DashboardDeleteEmbeddedFailedError,
    DashboardDeleteFailedError,
    DashboardDeleteFailedReportsExistError,
    DashboardForbiddenError,
    DashboardNotFoundError,
)
from rama.daos.dashboard import DashboardDAO, EmbeddedDashboardDAO
from rama.daos.report import ReportScheduleDAO
from rama.exceptions import RamaSecurityException
from rama.models.dashboard import Dashboard
from rama.utils.decorators import on_error, transaction

logger = logging.getLogger(__name__)


class DeleteEmbeddedDashboardCommand(BaseCommand):
    def __init__(self, dashboard: Dashboard):
        self._dashboard = dashboard

    @transaction(on_error=partial(on_error, reraise=DashboardDeleteEmbeddedFailedError))
    def run(self) -> None:
        self.validate()
        return EmbeddedDashboardDAO.delete(self._dashboard.embedded)

    def validate(self) -> None:
        pass


class DeleteDashboardCommand(BaseCommand):
    def __init__(self, model_ids: list[int]):
        self._model_ids = model_ids
        self._models: Optional[list[Dashboard]] = None

    @transaction(on_error=partial(on_error, reraise=DashboardDeleteFailedError))
    def run(self) -> None:
        self.validate()
        assert self._models
        DashboardDAO.delete(self._models)

    def validate(self) -> None:
        # Validate/populate model exists
        self._models = DashboardDAO.find_by_ids(self._model_ids)
        if not self._models or len(self._models) != len(self._model_ids):
            raise DashboardNotFoundError()
        # Check there are no associated ReportSchedules
        if reports := ReportScheduleDAO.find_by_dashboard_ids(self._model_ids):
            report_names = [report.name for report in reports]
            raise DashboardDeleteFailedReportsExistError(
                _(
                    "There are associated alerts or reports: %(report_names)s",
                    report_names=",".join(report_names),
                )
            )
        # Check ownership
        for model in self._models:
            try:
                security_manager.raise_for_ownership(model)
            except RamaSecurityException as ex:
                raise DashboardForbiddenError() from ex
