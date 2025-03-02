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
import contextlib
from typing import Any

from flask import request
from flask_appbuilder import permission_name
from flask_appbuilder.api import expose
from flask_appbuilder.security.decorators import has_access

from rama import event_logger
from rama.constants import MODEL_API_RW_METHOD_PERMISSION_MAP
from rama.rama_typing import FlaskResponse
from rama.utils import json

from .base import BaseRamaView


class SqllabView(BaseRamaView):
    route_base = "/sqllab"
    class_permission_name = "SQLLab"

    method_permission_name = MODEL_API_RW_METHOD_PERMISSION_MAP

    @expose("/", methods=["GET", "POST"])
    @has_access
    @permission_name("read")
    @event_logger.log_this
    def root(self, **kwargs: Any) -> FlaskResponse:
        """Handles the default SQL Lab page."""
        payload = {}
        if form_data := request.form.get("form_data"):
            with contextlib.suppress(json.JSONDecodeError):
                payload["requested_query"] = json.loads(form_data)
        return self.render_app_template(payload)

    @expose("/p/<string:permalink>/", methods=["GET"])
    @has_access
    @permission_name("read")
    @event_logger.log_this
    def permalink_view(self, permalink: str, **kwargs: Any) -> FlaskResponse:
        """Handles permalinks for SQL Lab."""
        return self.root(permalink=permalink, **kwargs)

    @expose("/history/", methods=("GET",))
    @has_access
    @permission_name("read")
    @event_logger.log_this
    def history(self) -> FlaskResponse:
        return self.render_app_template()
