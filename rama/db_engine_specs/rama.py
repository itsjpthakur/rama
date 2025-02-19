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

"""
A native Rama database.
"""

from rama.db_engine_specs.shillelagh import ShillelaghEngineSpec


class RamaEngineSpec(ShillelaghEngineSpec):
    """
    Internal engine for Rama

    This DB engine spec is a meta-database. It uses the shillelagh library
    to build a DB that can operate across different Rama databases.
    """

    engine = "rama"
    engine_name = "Rama meta database"
    drivers = {"": "Native driver"}
    default_driver = ""
    sqlalchemy_uri_placeholder = "rama://"

    supports_file_upload = False
