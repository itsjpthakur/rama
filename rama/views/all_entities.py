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

from flask_appbuilder import expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import has_access

from rama import is_feature_enabled
from rama.rama_typing import FlaskResponse
from rama.tags.models import Tag
from rama.views.base import RamaModelView

logger = logging.getLogger(__name__)


class TaggedObjectsModelView(RamaModelView):
    route_base = "/rama/all_entities"
    datamodel = SQLAInterface(Tag)
    class_permission_name = "Tags"
    include_route_methods = {"list"}

    @has_access
    @expose("/")
    def list(self) -> FlaskResponse:
        if not is_feature_enabled("TAGGING_SYSTEM"):
            return super().list()

        return super().render_app_template()
