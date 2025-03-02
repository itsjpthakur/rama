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
from typing import Optional, Union

from rama.daos.base import BaseDAO
from rama.extensions import db
from rama.models.annotations import Annotation, AnnotationLayer

logger = logging.getLogger(__name__)


class AnnotationDAO(BaseDAO[Annotation]):
    @staticmethod
    def validate_update_uniqueness(
        layer_id: int, short_descr: str, annotation_id: Optional[int] = None
    ) -> bool:
        """
        Validate if this annotation short description is unique. `id` is optional
        and serves for validating on updates

        :param short_descr: The annotation short description
        :param layer_id: The annotation layer current id
        :param annotation_id: This annotation is (only for validating on updates)
        :return: bool
        """
        query = db.session.query(Annotation).filter(
            Annotation.short_descr == short_descr, Annotation.layer_id == layer_id
        )
        if annotation_id:
            query = query.filter(Annotation.id != annotation_id)
        return not db.session.query(query.exists()).scalar()


class AnnotationLayerDAO(BaseDAO[AnnotationLayer]):
    @staticmethod
    def has_annotations(model_id: Union[int, list[int]]) -> bool:
        if isinstance(model_id, list):
            return (
                db.session.query(AnnotationLayer)
                .filter(AnnotationLayer.id.in_(model_id))
                .join(Annotation)
                .first()
            ) is not None
        return (
            db.session.query(AnnotationLayer)
            .filter(AnnotationLayer.id == model_id)
            .join(Annotation)
            .first()
        ) is not None

    @staticmethod
    def validate_update_uniqueness(name: str, layer_id: Optional[int] = None) -> bool:
        """
        Validate if this layer name is unique. `layer_id` is optional
        and serves for validating on updates

        :param name: The annotation layer name
        :param layer_id: The annotation layer current id
        (only for validating on updates)
        :return: bool
        """
        query = db.session.query(AnnotationLayer).filter(AnnotationLayer.name == name)
        if layer_id:
            query = query.filter(AnnotationLayer.id != layer_id)
        return not db.session.query(query.exists()).scalar()
