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
from http.client import HTTPResponse
from typing import Optional, TYPE_CHECKING
from urllib import request

from celery.utils.log import get_task_logger
from flask import g

from rama.tasks.exceptions import ExecutorNotFoundError, InvalidExecutorError
from rama.tasks.types import ChosenExecutor, Executor, ExecutorType, FixedExecutor
from rama.utils import json
from rama.utils.urls import get_url_path

if TYPE_CHECKING:
    from rama.models.dashboard import Dashboard
    from rama.models.slice import Slice
    from rama.reports.models import ReportSchedule


logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)


# pylint: disable=too-many-branches
def get_executor(  # noqa: C901
    executors: list[Executor],
    model: Dashboard | ReportSchedule | Slice,
    current_user: str | None = None,
) -> ChosenExecutor:
    """
    Extract the user that should be used to execute a scheduled task. Certain executor
    types extract the user from the underlying object (e.g. CREATOR), the constant
    Selenium user (SELENIUM), or the user that initiated the request.

    :param executors: The requested executor in descending order. When the
           first user is found it is returned.
    :param model: The underlying object
    :param current_user: The username of the user that initiated the task. For
           thumbnails this is the user that requested the thumbnail, while for alerts
           and reports this is None (=initiated by Celery).
    :return: User to execute the execute the async task as. The first element of the
             tuple represents the type of the executor, and the second represents the
             username of the executor.
    :raises ExecutorNotFoundError: If no users were found in after
            iterating through all entries in `executors`
    """
    owners = model.owners
    owner_dict = {owner.id: owner for owner in owners}
    for executor in executors:
        if isinstance(executor, FixedExecutor):
            return ExecutorType.FIXED_USER, executor.username
        if executor == ExecutorType.FIXED_USER:
            raise InvalidExecutorError()
        if executor == ExecutorType.CURRENT_USER and current_user:
            return executor, current_user
        if executor == ExecutorType.CREATOR_OWNER:
            if (user := model.created_by) and (owner := owner_dict.get(user.id)):
                return executor, owner.username
        if executor == ExecutorType.CREATOR:
            if user := model.created_by:
                return executor, user.username
        if executor == ExecutorType.MODIFIER_OWNER:
            if (user := model.changed_by) and (owner := owner_dict.get(user.id)):
                return executor, owner.username
        if executor == ExecutorType.MODIFIER:
            if user := model.changed_by:
                return executor, user.username
        if executor == ExecutorType.OWNER:
            owners = model.owners
            if len(owners) == 1:
                return executor, owners[0].username
            if len(owners) > 1:
                if modifier := model.changed_by:
                    if modifier and (user := owner_dict.get(modifier.id)):
                        return executor, user.username
                if creator := model.created_by:
                    if creator and (user := owner_dict.get(creator.id)):
                        return executor, user.username
                return executor, owners[0].username

    raise ExecutorNotFoundError()


def get_current_user() -> str | None:
    user = g.user if hasattr(g, "user") and g.user else None
    if user and not user.is_anonymous:
        return user.username

    return None


def fetch_csrf_token(
    headers: dict[str, str], session_cookie_name: str = "session"
) -> dict[str, str]:
    """
    Fetches a CSRF token for API requests

    :param headers: A map of headers to use in the request, including the session cookie
    :returns: A map of headers, including the session cookie and csrf token
    """
    url = get_url_path("SecurityRestApi.csrf_token")
    logger.info("Fetching %s", url)
    req = request.Request(url, headers=headers, method="GET")  # noqa: S310
    response: HTTPResponse
    with request.urlopen(req, timeout=600) as response:  # noqa: S310
        body = response.read().decode("utf-8")
        session_cookie: Optional[str] = None
        cookie_headers = response.headers.get_all("set-cookie")
        if cookie_headers:
            for cookie in cookie_headers:
                cookie = cookie.split(";", 1)[0]
                name, value = cookie.split("=", 1)
                if name == session_cookie_name:
                    session_cookie = value
                    break

        if response.status == 200:
            data = json.loads(body)
            res = {"X-CSRF-Token": data["result"]}
            if session_cookie is not None:
                res["Cookie"] = f"{session_cookie_name}={session_cookie}"
            return res

    logger.error("Error fetching CSRF token, status code: %s", response.status)
    return {}
