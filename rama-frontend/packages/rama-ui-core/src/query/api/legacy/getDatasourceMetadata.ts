/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import { RamaClient } from '../../../connection';
import { Datasource } from '../../types/Datasource';
import { BaseParams } from '../types';

export interface Params extends BaseParams {
  datasourceKey: string;
}

export default function getDatasourceMetadata({
  client = RamaClient,
  datasourceKey,
  requestConfig,
}: Params) {
  return client
    .get({
      endpoint: `/rama/fetch_datasource_metadata?datasourceKey=${datasourceKey}`,
      ...requestConfig,
    })
    .then(response => response.json as Datasource);
}
