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

# Python version installed; we need 3.10-3.11
PYTHON=`command -v python3.11 || command -v python3.10`

.PHONY: install rama venv pre-commit

install: rama pre-commit

rama:
	# Install external dependencies
	pip install -r requirements/development.txt

	# Install Rama in editable (development) mode
	pip install -e .

	# Create an admin user in your metadata database
	rama fab create-admin \
                    --username admin \
                    --firstname "Admin I."\
                    --lastname Strator \
                    --email admin@rama.io \
                    --password general

	# Initialize the database
	rama db upgrade

	# Create default roles and permissions
	rama init

	# Load some data to play with
	# rama load-examples

	# Install node packages
	cd rama-frontend; npm ci

update: update-py update-js

update-py:
	# Install external dependencies
	pip install -r requirements/development.txt

	# Install Rama in editable (development) mode
	pip install -e .

	# Initialize the database
	rama db upgrade

	# Create default roles and permissions
	rama init

update-js:
	# Install js packages
	cd rama-frontend; npm ci

venv:
	# Create a virtual environment and activate it (recommended)
	if ! [ -x "${PYTHON}" ]; then echo "You need Python 3.10 or 3.11 installed"; exit 1; fi
	test -d venv || ${PYTHON} -m venv venv # setup a python3 virtualenv
	. venv/bin/activate

activate:
	. venv/bin/activate

pre-commit:
	# setup pre commit dependencies
	pip3 install -r requirements/development.txt
	pre-commit install

format: py-format js-format

py-format: pre-commit
	pre-commit run black --all-files

js-format:
	cd rama-frontend; npm run prettier

flask-app:
	flask run -p 8088 --with-threads --reload --debugger

node-app:
	cd rama-frontend; npm run dev-server

build-cypress:
	cd rama-frontend; npm run build-instrumented
	cd rama-frontend/cypress-base; npm ci

open-cypress:
	if ! [ $(port) ]; then cd rama-frontend/cypress-base; CYPRESS_BASE_URL=http://localhost:9000 npm run cypress open; fi
	cd rama-frontend/cypress-base; CYPRESS_BASE_URL=http://localhost:$(port) npm run cypress open

report-celery-worker:
	celery --app=rama.tasks.celery_app:app worker

report-celery-beat:
	celery --app=rama.tasks.celery_app:app beat --pidfile /tmp/celerybeat.pid --schedule /tmp/celerybeat-schedulecd

admin-user:
	rama fab create-admin
