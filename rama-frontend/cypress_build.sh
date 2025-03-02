#!/bin/bash
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
set -e

cd "$(dirname "$0")"

#run all the python steps in a background process
time rama db upgrade
time rama load_test_users
time rama load_examples --load-test-data
time rama init
echo "[completed python build steps]"
PORT='8081'
flask run -p $PORT --with-threads --reload --debugger &

#block on the longer running javascript process
time npm ci
time npm run build-instrumented
echo "[completed js build steps]"

#setup cypress
cd cypress-base
time npm ci
export CYPRESS_BASE_URL="http://localhost:${PORT}"
if [ -n "$1" ]; then
    CYPRESS_PATH='cypress/e2e/'${1}'/*'
    time npm run cypress-run-chrome -- --spec "$CYPRESS_PATH" --record false --config video=false || true
else
    time npm run cypress-run-chrome -- --record false --config video=false || true
fi
kill %1
