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
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from flask import current_app

from rama.commands.dashboard.permalink.create import CreateDashboardPermalinkCommand
from rama.commands.report.execute import AsyncExecuteReportScheduleCommand
from rama.models.dashboard import Dashboard
from rama.reports.models import ReportSourceFormat
from rama.utils.urls import get_url_path
from tests.integration_tests.fixtures.tabbed_dashboard import (
    tabbed_dashboard,  # noqa: F401
)
from tests.integration_tests.reports.utils import create_dashboard_report


@patch("rama.reports.notifications.email.send_email_smtp")
@patch(
    "rama.commands.report.execute.DashboardScreenshot",
)
@patch.dict(
    "rama.extensions.feature_flag_manager._feature_flags", ALERT_REPORT_TABS=True
)
@pytest.mark.usefixtures("login_as_admin")
def test_report_for_dashboard_with_tabs(
    dashboard_screenshot_mock: MagicMock,
    send_email_smtp_mock: MagicMock,
    tabbed_dashboard: Dashboard,  # noqa: F811
) -> None:
    dashboard_screenshot_mock.get_screenshot.return_value = b"test-image"
    current_app.config["ALERT_REPORTS_NOTIFICATION_DRY_RUN"] = False

    with create_dashboard_report(
        dashboard=tabbed_dashboard,
        extra={"dashboard": {"active_tabs": ["TAB-L1B", "TAB-L2BB"]}},
        name="test report tabbed dashboard",
    ) as report_schedule:
        dashboard: Dashboard = report_schedule.dashboard
        AsyncExecuteReportScheduleCommand(
            str(uuid4()), report_schedule.id, datetime.utcnow()
        ).run()
        dashboard_state = report_schedule.extra.get("dashboard", {})
        permalink_key = CreateDashboardPermalinkCommand(
            str(dashboard.id), dashboard_state
        ).run()

        expected_url = get_url_path("Rama.dashboard_permalink", key=permalink_key)

        assert dashboard_screenshot_mock.call_count == 1
        called_url = dashboard_screenshot_mock.call_args.args[0]

        assert called_url == expected_url
        assert send_email_smtp_mock.call_count == 1
        assert len(send_email_smtp_mock.call_args.kwargs["images"]) == 1


@patch("rama.reports.notifications.email.send_email_smtp")
@patch(
    "rama.commands.report.execute.DashboardScreenshot",
)
@patch.dict(
    "rama.extensions.feature_flag_manager._feature_flags", ALERT_REPORT_TABS=True
)
@pytest.mark.usefixtures("login_as_admin")
def test_report_with_header_data(
    dashboard_screenshot_mock: MagicMock,
    send_email_smtp_mock: MagicMock,
    tabbed_dashboard: Dashboard,  # noqa: F811
) -> None:
    dashboard_screenshot_mock.get_screenshot.return_value = b"test-image"
    current_app.config["ALERT_REPORTS_NOTIFICATION_DRY_RUN"] = False

    with create_dashboard_report(
        dashboard=tabbed_dashboard,
        extra={"dashboard": {"active_tabs": ["TAB-L1B", "TAB-L2BB"]}},
        name="test report tabbed dashboard",
    ) as report_schedule:
        dashboard: Dashboard = report_schedule.dashboard
        AsyncExecuteReportScheduleCommand(
            str(uuid4()), report_schedule.id, datetime.utcnow()
        ).run()
        dashboard_state = report_schedule.extra.get("dashboard", {})
        permalink_key = CreateDashboardPermalinkCommand(
            dashboard.id, dashboard_state
        ).run()

        assert dashboard_screenshot_mock.call_count == 1
        url = dashboard_screenshot_mock.call_args.args[0]

        assert url.endswith(f"/rama/dashboard/p/{permalink_key}/")
        assert send_email_smtp_mock.call_count == 1
        header_data = send_email_smtp_mock.call_args.kwargs["header_data"]
        assert header_data.get("dashboard_id") == dashboard.id
        assert header_data.get("notification_format") == report_schedule.report_format
        assert header_data.get("notification_source") == ReportSourceFormat.DASHBOARD
        assert header_data.get("notification_type") == report_schedule.type
        assert len(send_email_smtp_mock.call_args.kwargs["header_data"]) == 7
