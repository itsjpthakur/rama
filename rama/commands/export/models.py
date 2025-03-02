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

from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Callable

import yaml
from flask_appbuilder import Model

from rama.commands.base import BaseCommand
from rama.commands.exceptions import CommandException
from rama.daos.base import BaseDAO
from rama.utils.dict_import_export import EXPORT_VERSION

METADATA_FILE_NAME = "metadata.yaml"


class ExportModelsCommand(BaseCommand):
    dao: type[BaseDAO[Model]] = BaseDAO
    not_found: type[CommandException] = CommandException

    def __init__(self, model_ids: list[int], export_related: bool = True):
        self.model_ids = model_ids
        self.export_related = export_related

        # this will be set when calling validate()
        self._models: list[Model] = []

    @staticmethod
    def _file_name(model: Model) -> str:
        raise NotImplementedError("Subclasses MUST implement _file_name")

    @staticmethod
    def _file_content(model: Model) -> str:
        raise NotImplementedError("Subclasses MUST implement _export")

    @staticmethod
    def _export(
        model: Model, export_related: bool = True
    ) -> Iterator[tuple[str, Callable[[], str]]]:
        raise NotImplementedError("Subclasses MUST implement _export")

    def run(self) -> Iterator[tuple[str, Callable[[], str]]]:
        self.validate()

        metadata = {
            "version": EXPORT_VERSION,
            "type": self.dao.model_cls.__name__,  # type: ignore
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }
        yield METADATA_FILE_NAME, lambda: yaml.safe_dump(metadata, sort_keys=False)

        seen = {METADATA_FILE_NAME}
        for model in self._models:
            for file_name, file_content in self._export(model, self.export_related):
                if file_name not in seen:
                    yield file_name, file_content
                    seen.add(file_name)

    def validate(self) -> None:
        self._models = self.dao.find_by_ids(self.model_ids)
        if len(self._models) != len(self.model_ids):
            raise self.not_found()
