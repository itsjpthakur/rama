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
import re
from datetime import date, datetime, timedelta
from typing import Optional
from unittest.mock import Mock, patch

import freezegun
import pytest
from dateutil.relativedelta import relativedelta

from rama.commands.chart.exceptions import (
    TimeRangeAmbiguousError,
    TimeRangeParseFailError,
)
from rama.utils.date_parser import (
    DateRangeMigration,
    datetime_eval,
    get_past_or_future,
    get_since_until,
    parse_human_datetime,
    parse_human_timedelta,
    parse_past_timedelta,
)
from tests.unit_tests.conftest import with_feature_flags


def mock_parse_human_datetime(s: str) -> Optional[datetime]:  # noqa: C901
    if s == "now":
        return datetime(2016, 11, 7, 9, 30, 10)
    elif s == "2018":
        return datetime(2018, 1, 1)
    elif s == "2018-9":
        return datetime(2018, 9, 1)
    elif s == "today":
        return datetime(2016, 11, 7)
    elif s == "yesterday":
        return datetime(2016, 11, 6)
    elif s == "tomorrow":
        return datetime(2016, 11, 8)
    elif s == "Last year":
        return datetime(2015, 11, 7)
    elif s == "Last week":
        return datetime(2015, 10, 31)
    elif s == "Last 5 months":
        return datetime(2016, 6, 7)
    elif s == "Next 5 months":
        return datetime(2017, 4, 7)
    elif s in ["5 days", "5 days ago"]:
        return datetime(2016, 11, 2)
    elif s == "2000-01-01T00:00:00":
        return datetime(2000, 1, 1)
    elif s == "2018-01-01T00:00:00":
        return datetime(2018, 1, 1)
    elif s == "2018-01-10T00:00:00":
        return datetime(2018, 1, 10)
    elif s == "2018-12-31T23:59:59":
        return datetime(2018, 12, 31, 23, 59, 59)
    elif s == "2022-01-01T00:00:00":
        return datetime(2022, 1, 1)
    else:
        return None


@patch("rama.utils.date_parser.parse_human_datetime", mock_parse_human_datetime)
def test_get_since_until() -> None:
    result: tuple[Optional[datetime], Optional[datetime]]
    expected: tuple[Optional[datetime], Optional[datetime]]

    result = get_since_until()
    expected = None, datetime(2016, 11, 7)
    assert result == expected

    result = get_since_until(" : now")
    expected = None, datetime(2016, 11, 7, 9, 30, 10)
    assert result == expected

    result = get_since_until("yesterday : tomorrow")
    expected = datetime(2016, 11, 6), datetime(2016, 11, 8)
    assert result == expected

    result = get_since_until(" : now")
    expected = None, datetime(2016, 11, 7, 9, 30, 10)
    assert result == expected

    result = get_since_until(" : last 2 minutes")
    expected = None, datetime(2016, 11, 7, 9, 28, 10)
    assert result == expected

    result = get_since_until(" : prior 2 minutes")
    expected = None, datetime(2016, 11, 7, 9, 28, 10)
    assert result == expected

    result = get_since_until(" : next 2 minutes")
    expected = None, datetime(2016, 11, 7, 9, 32, 10)
    assert result == expected

    result = get_since_until("start of this month : ")
    expected = datetime(2016, 11, 1), None
    assert result == expected

    result = get_since_until("start of next month : ")
    expected = datetime(2016, 12, 1), None
    assert result == expected

    result = get_since_until("end of this month : ")
    expected = datetime(2016, 11, 30), None
    assert result == expected

    result = get_since_until("end of next month : ")
    expected = datetime(2016, 12, 31), None
    assert result == expected

    result = get_since_until("beginning of next year : ")
    expected = datetime(2017, 1, 1), None
    assert result == expected

    result = get_since_until("beginning of last year : ")
    expected = datetime(2015, 1, 1), None
    assert result == expected

    result = get_since_until("2018-01-01T00:00:00 : 2018-12-31T23:59:59")
    expected = datetime(2018, 1, 1), datetime(2018, 12, 31, 23, 59, 59)
    assert result == expected

    result = get_since_until("Last year")
    expected = datetime(2015, 11, 7), datetime(2016, 11, 7)
    assert result == expected

    result = get_since_until("Last quarter")
    expected = datetime(2016, 8, 7), datetime(2016, 11, 7)
    assert result == expected

    result = get_since_until("Last 5 months")
    expected = datetime(2016, 6, 7), datetime(2016, 11, 7)
    assert result == expected

    result = get_since_until("Last 1 month")
    expected = datetime(2016, 10, 7), datetime(2016, 11, 7)
    assert result == expected

    result = get_since_until("Next 5 months")
    expected = datetime(2016, 11, 7), datetime(2017, 4, 7)
    assert result == expected

    result = get_since_until("Next 1 month")
    expected = datetime(2016, 11, 7), datetime(2016, 12, 7)
    assert result == expected

    result = get_since_until(since="5 days")
    expected = datetime(2016, 11, 2), datetime(2016, 11, 7)
    assert result == expected

    result = get_since_until(since="5 days ago", until="tomorrow")
    expected = datetime(2016, 11, 2), datetime(2016, 11, 8)
    assert result == expected

    result = get_since_until(time_range="yesterday : tomorrow", time_shift="1 day")
    expected = datetime(2016, 11, 5), datetime(2016, 11, 7)
    assert result == expected

    result = get_since_until(time_range="5 days : now")
    expected = datetime(2016, 11, 2), datetime(2016, 11, 7, 9, 30, 10)
    assert result == expected

    result = get_since_until("Last week", relative_end="now")
    expected = datetime(2016, 10, 31), datetime(2016, 11, 7, 9, 30, 10)
    assert result == expected

    result = get_since_until("Last week", relative_start="now")
    expected = datetime(2016, 10, 31, 9, 30, 10), datetime(2016, 11, 7)
    assert result == expected

    result = get_since_until("Last week", relative_start="now", relative_end="now")
    expected = datetime(2016, 10, 31, 9, 30, 10), datetime(2016, 11, 7, 9, 30, 10)
    assert result == expected

    result = get_since_until("previous calendar week")
    expected = datetime(2016, 10, 31, 0, 0, 0), datetime(2016, 11, 7, 0, 0, 0)
    assert result == expected

    result = get_since_until("previous calendar month")
    expected = datetime(2016, 10, 1, 0, 0, 0), datetime(2016, 11, 1, 0, 0, 0)
    assert result == expected

    result = get_since_until("previous calendar year")
    expected = datetime(2015, 1, 1, 0, 0, 0), datetime(2016, 1, 1, 0, 0, 0)
    assert result == expected

    result = get_since_until("Current day")
    expected = datetime(2016, 11, 7, 0, 0, 0), datetime(2016, 11, 8, 0, 0, 0)
    assert result == expected

    result = get_since_until("Current week")
    expected = datetime(2016, 11, 7, 0, 0, 0), datetime(2016, 11, 14, 0, 0, 0)
    assert result == expected

    result = get_since_until("Current month")
    expected = datetime(2016, 11, 1, 0, 0, 0), datetime(2016, 12, 1, 0, 0, 0)
    assert result == expected

    result = get_since_until("Current quarter")
    expected = datetime(2016, 10, 1, 0, 0, 0), datetime(2017, 1, 1, 0, 0, 0)
    assert result == expected

    result = get_since_until("Current year")
    expected = expected = datetime(2016, 1, 1, 0, 0, 0), datetime(2017, 1, 1, 0, 0, 0)
    assert result == expected

    # Tests for our new instant_time_comparison logic and Feature Flag off
    result = get_since_until(
        time_range="2000-01-01T00:00:00 : 2018-01-01T00:00:00",
        instant_time_comparison_range="y",
    )
    expected = datetime(2000, 1, 1), datetime(2018, 1, 1)
    assert result == expected

    result = get_since_until(
        time_range="2000-01-01T00:00:00 : 2018-01-01T00:00:00",
        instant_time_comparison_range="m",
    )
    expected = datetime(2000, 1, 1), datetime(2018, 1, 1)
    assert result == expected

    result = get_since_until(
        time_range="2000-01-01T00:00:00 : 2018-01-01T00:00:00",
        instant_time_comparison_range="w",
    )
    expected = datetime(2000, 1, 1), datetime(2018, 1, 1)
    assert result == expected

    result = get_since_until(
        time_range="2000-01-01T00:00:00 : 2018-01-01T00:00:00",
        instant_time_comparison_range="r",
    )
    expected = datetime(2000, 1, 1), datetime(2018, 1, 1)
    assert result == expected

    result = get_since_until(
        time_range="2000-01-01T00:00:00 : 2018-01-01T00:00:00",
        time_shift="1 year ago",
    )
    expected = datetime(1999, 1, 1), datetime(2017, 1, 1)
    assert result == expected

    result = get_since_until(
        time_range="2000-01-01T00:00:00 : 2018-01-01T00:00:00",
        time_shift="1 month ago",
    )
    expected = datetime(1999, 12, 1), datetime(2017, 12, 1)
    assert result == expected

    result = get_since_until(
        time_range="2000-01-01T00:00:00 : 2018-01-01T00:00:00",
        time_shift="1 week ago",
    )
    expected = datetime(1999, 12, 25), datetime(2017, 12, 25)
    assert result == expected

    with pytest.raises(ValueError):  # noqa: PT011
        get_since_until(time_range="tomorrow : yesterday")


@with_feature_flags(CHART_PLUGINS_EXPERIMENTAL=True)
@patch("rama.utils.date_parser.parse_human_datetime", mock_parse_human_datetime)
def test_get_since_until_instant_time_comparison_enabled() -> None:
    result: tuple[Optional[datetime], Optional[datetime]]
    expected: tuple[Optional[datetime], Optional[datetime]]

    result = get_since_until(
        time_range="2000-01-01T00:00:00 : 2018-01-01T00:00:00",
        instant_time_comparison_range="y",
    )
    expected = datetime(1999, 1, 1), datetime(2017, 1, 1)
    assert result == expected

    result = get_since_until(
        time_range="2000-01-01T00:00:00 : 2018-01-01T00:00:00",
        instant_time_comparison_range="m",
    )
    expected = datetime(1999, 12, 1), datetime(2017, 12, 1)
    assert result == expected

    result = get_since_until(
        time_range="2000-01-01T00:00:00 : 2018-01-01T00:00:00",
        instant_time_comparison_range="w",
    )
    expected = datetime(1999, 12, 25), datetime(2017, 12, 25)
    assert result == expected

    result = get_since_until(
        time_range="2000-01-01T00:00:00 : 2018-01-01T00:00:00",
        instant_time_comparison_range="r",
    )
    expected = datetime(1981, 12, 31), datetime(2000, 1, 1)
    assert result == expected

    result = get_since_until(
        time_range="2000-01-01T00:00:00 : 2018-01-01T00:00:00",
        instant_time_comparison_range="unknown",
    )
    expected = datetime(2000, 1, 1), datetime(2018, 1, 1)
    assert result == expected


def test_previous_calendar_quarter():
    with freezegun.freeze_time("2023-01-15"):
        result = get_since_until("previous calendar quarter")
        expected = (datetime(2022, 10, 1), datetime(2023, 1, 1))
        assert result == expected

    with freezegun.freeze_time("2023, 4, 15"):
        result = get_since_until("previous calendar quarter")
        expected = (datetime(2023, 1, 1), datetime(2023, 4, 1))
        assert result == expected

    with freezegun.freeze_time("2023, 8, 15"):
        result = get_since_until("previous calendar quarter")
        expected = (datetime(2023, 4, 1), datetime(2023, 7, 1))
        assert result == expected

    with freezegun.freeze_time("2023, 10, 15"):
        result = get_since_until("previous calendar quarter")
        expected = (datetime(2023, 7, 1), datetime(2023, 10, 1))
        assert result == expected

    with freezegun.freeze_time("2024, 1, 1"):
        result = get_since_until("previous calendar quarter")
        expected = (datetime(2023, 10, 1), datetime(2024, 1, 1))
        assert result == expected


@patch("rama.utils.date_parser.parse_human_datetime", mock_parse_human_datetime)
def test_datetime_eval() -> None:
    result = datetime_eval("datetime('now')")
    expected = datetime(2016, 11, 7, 9, 30, 10)
    assert result == expected

    result = datetime_eval("datetime('today')")
    expected = datetime(2016, 11, 7)
    assert result == expected

    result = datetime_eval("datetime('2018')")
    expected = datetime(2018, 1, 1)
    assert result == expected

    result = datetime_eval("datetime('2018-9')")
    expected = datetime(2018, 9, 1)
    assert result == expected

    # Parse compact arguments spelling
    result = datetime_eval("dateadd(datetime('today'),1,year,)")
    expected = datetime(2017, 11, 7)
    assert result == expected

    result = datetime_eval("dateadd(datetime('today'), -2, year)")
    expected = datetime(2014, 11, 7)
    assert result == expected

    result = datetime_eval("dateadd(datetime('today'), 2, quarter)")
    expected = datetime(2017, 5, 7)
    assert result == expected

    result = datetime_eval("dateadd(datetime('today'), 3, month)")
    expected = datetime(2017, 2, 7)
    assert result == expected

    result = datetime_eval("dateadd(datetime('today'), -3, week)")
    expected = datetime(2016, 10, 17)
    assert result == expected

    result = datetime_eval("dateadd(datetime('today'), 3, day)")
    expected = datetime(2016, 11, 10)
    assert result == expected

    result = datetime_eval("dateadd(datetime('now'), 3, hour)")
    expected = datetime(2016, 11, 7, 12, 30, 10)
    assert result == expected

    result = datetime_eval("dateadd(datetime('now'), 40, minute)")
    expected = datetime(2016, 11, 7, 10, 10, 10)
    assert result == expected

    result = datetime_eval("dateadd(datetime('now'), -11, second)")
    expected = datetime(2016, 11, 7, 9, 29, 59)
    assert result == expected

    result = datetime_eval("datetrunc(datetime('now'), year)")
    expected = datetime(2016, 1, 1, 0, 0, 0)
    assert result == expected

    result = datetime_eval("datetrunc(datetime('now'), quarter)")
    expected = datetime(2016, 10, 1, 0, 0, 0)
    assert result == expected

    result = datetime_eval("datetrunc(datetime('now'), month)")
    expected = datetime(2016, 11, 1, 0, 0, 0)
    assert result == expected

    result = datetime_eval("datetrunc(datetime('now'), day)")
    expected = datetime(2016, 11, 7, 0, 0, 0)
    assert result == expected

    result = datetime_eval("datetrunc(datetime('now'), week)")
    expected = datetime(2016, 11, 7, 0, 0, 0)
    assert result == expected

    result = datetime_eval("datetrunc(datetime('now'), hour)")
    expected = datetime(2016, 11, 7, 9, 0, 0)
    assert result == expected

    result = datetime_eval("datetrunc(datetime('now'), minute)")
    expected = datetime(2016, 11, 7, 9, 30, 0)
    assert result == expected

    result = datetime_eval("datetrunc(datetime('now'), second)")
    expected = datetime(2016, 11, 7, 9, 30, 10)
    assert result == expected

    result = datetime_eval("lastday(datetime('now'), year)")
    expected = datetime(2016, 12, 31, 0, 0, 0)
    assert result == expected

    result = datetime_eval("lastday(datetime('today'), month)")
    expected = datetime(2016, 11, 30, 0, 0, 0)
    assert result == expected

    result = datetime_eval("holiday('Christmas')")
    expected = datetime(2016, 12, 25, 0, 0, 0)
    assert result == expected

    result = datetime_eval("holiday('Labor day', datetime('2018-01-01T00:00:00'))")
    expected = datetime(2018, 9, 3, 0, 0, 0)
    assert result == expected

    result = datetime_eval(
        "holiday('Eid al-Fitr', datetime('2000-01-01T00:00:00'), 'SA')"
    )
    expected = datetime(2000, 1, 8, 0, 0, 0)
    assert result == expected

    result = datetime_eval(
        "holiday('Boxing day', datetime('2018-01-01T00:00:00'), 'UK')"
    )
    expected = datetime(2018, 12, 26, 0, 0, 0)
    assert result == expected

    result = datetime_eval(
        "holiday('Juneteenth', datetime('2022-01-01T00:00:00'), 'US')"
    )
    expected = datetime(2022, 6, 19, 0, 0, 0)
    assert result == expected

    result = datetime_eval(
        "holiday('Independence Day', datetime('2022-01-01T00:00:00'), 'US')"
    )
    expected = datetime(2022, 7, 4, 0, 0, 0)
    assert result == expected

    result = datetime_eval(
        "lastday(dateadd(datetime('2018-01-01T00:00:00'), 1, month), month)"
    )
    expected = datetime(2018, 2, 28, 0, 0, 0)
    assert result == expected

    result = datetime_eval(
        "datediff(datetime('2018-01-01T00:00:00'), datetime('2018-01-10T00:00:00'))"  # pylint: disable=line-too-long,useless-suppression
    )
    assert result == 9

    result = datetime_eval(
        "datediff(datetime('2018-01-10T00:00:00'), datetime('2018-01-01T00:00:00'))"  # pylint: disable=line-too-long,useless-suppression
    )
    assert result == -9

    result = datetime_eval(
        "datediff(datetime('2018-01-01T00:00:00'), datetime('2018-01-10T00:00:00'), day)"  # pylint: disable=line-too-long,useless-suppression  # noqa: E501
    )
    assert result == 9

    result = datetime_eval(
        "datediff(datetime('2018-01-01T00:00:00'), datetime('2018-01-10T00:00:00'), year)"  # pylint: disable=line-too-long,useless-suppression  # noqa: E501
    )
    assert result == 0

    result = datetime_eval(
        "dateadd("
        "datetime('2018-01-01T00:00:00'), "
        "datediff(datetime('2018-01-10T00:00:00'), datetime('2018-01-01T00:00:00')), "  # pylint: disable=line-too-long,useless-suppression
        "day,"
        "),"
    )
    expected = datetime(2017, 12, 23, 0, 0, 0)
    assert result == expected


@patch("rama.utils.date_parser.datetime")
def test_parse_human_timedelta(mock_datetime: Mock) -> None:
    mock_datetime.now.return_value = datetime(2019, 4, 1)
    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
    assert parse_human_timedelta("now") == timedelta(0)
    assert parse_human_timedelta("1 year") == timedelta(366)
    assert parse_human_timedelta("-1 year") == timedelta(-365)
    assert parse_human_timedelta(None) == timedelta(0)
    assert parse_human_timedelta("1 month", datetime(2019, 4, 1)) == timedelta(30)
    assert parse_human_timedelta("1 month", datetime(2019, 5, 1)) == timedelta(31)
    assert parse_human_timedelta("1 month", datetime(2019, 2, 1)) == timedelta(28)
    assert parse_human_timedelta("-1 month", datetime(2019, 2, 1)) == timedelta(-31)


@patch("rama.utils.date_parser.datetime")
def test_parse_past_timedelta(mock_datetime: Mock) -> None:
    mock_datetime.now.return_value = datetime(2019, 4, 1)
    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
    assert parse_past_timedelta("1 year") == timedelta(365)
    assert parse_past_timedelta("-1 year") == timedelta(365)
    assert parse_past_timedelta("52 weeks") == timedelta(364)
    assert parse_past_timedelta("1 month") == timedelta(31)


def test_get_past_or_future() -> None:
    # 2020 is a leap year
    dttm = datetime(2020, 2, 29)
    assert get_past_or_future("1 year", dttm) == datetime(2021, 2, 28)
    assert get_past_or_future("-1 year", dttm) == datetime(2019, 2, 28)
    assert get_past_or_future("1 month", dttm) == datetime(2020, 3, 29)
    assert get_past_or_future("3 month", dttm) == datetime(2020, 5, 29)


def test_parse_human_datetime() -> None:
    with pytest.raises(TimeRangeAmbiguousError):
        parse_human_datetime("2 days")

    with pytest.raises(TimeRangeAmbiguousError):
        parse_human_datetime("2 day")

    with pytest.raises(TimeRangeParseFailError):
        parse_human_datetime("xxxxxxx")

    assert parse_human_datetime("2015-04-03") == datetime(2015, 4, 3, 0, 0)
    assert parse_human_datetime("2/3/1969") == datetime(1969, 2, 3, 0, 0)

    assert parse_human_datetime("now") <= datetime.now()
    assert parse_human_datetime("yesterday") < datetime.now()
    assert date.today() - timedelta(1) == parse_human_datetime("yesterday").date()

    assert (
        parse_human_datetime("one year ago").date()
        == (datetime.now() - relativedelta(years=1)).date()
    )
    assert (
        parse_human_datetime("2 years after").date()
        == (datetime.now() + relativedelta(years=2)).date()
    )


def test_date_range_migration() -> None:
    params = '{"time_range": "   8 days     : 2020-03-10T00:00:00"}'
    assert re.search(DateRangeMigration.x_dateunit_in_since, params)

    params = '{"time_range": "2020-03-10T00:00:00 :    8 days    "}'
    assert re.search(DateRangeMigration.x_dateunit_in_until, params)

    params = '{"time_range": "   2 weeks    :    8 days    "}'
    assert re.search(DateRangeMigration.x_dateunit_in_since, params)
    assert re.search(DateRangeMigration.x_dateunit_in_until, params)

    params = '{"time_range": "2 weeks ago : 8 days later"}'
    assert not re.search(DateRangeMigration.x_dateunit_in_since, params)
    assert not re.search(DateRangeMigration.x_dateunit_in_until, params)

    field = "   8 days   "
    assert re.search(DateRangeMigration.x_dateunit, field)

    field = "last week"
    assert not re.search(DateRangeMigration.x_dateunit, field)

    field = "10 years ago"
    assert not re.search(DateRangeMigration.x_dateunit, field)
