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
from typing import cast

from flask import session

from rama.commands.dashboard.filter_state.utils import check_access
from rama.commands.temporary_cache.create import CreateTemporaryCacheCommand
from rama.commands.temporary_cache.entry import Entry
from rama.commands.temporary_cache.parameters import CommandParameters
from rama.extensions import cache_manager
from rama.key_value.utils import random_key
from rama.temporary_cache.utils import cache_key
from rama.utils.core import get_user_id


class CreateFilterStateCommand(CreateTemporaryCacheCommand):
    def create(self, cmd_params: CommandParameters) -> str:
        resource_id = cmd_params.resource_id
        tab_id = cmd_params.tab_id
        contextual_key = cache_key(session.get("_id"), tab_id, resource_id)
        key = cache_manager.filter_state_cache.get(contextual_key)
        if not key or not tab_id:
            key = random_key()
        value = cast(str, cmd_params.value)  # schema ensures that value is not optional
        check_access(resource_id)
        entry: Entry = {"owner": get_user_id(), "value": value}
        cache_manager.filter_state_cache.set(cache_key(resource_id, key), entry)
        cache_manager.filter_state_cache.set(contextual_key, key)
        return key
