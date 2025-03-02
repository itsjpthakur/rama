/**
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
import { Dispatch } from 'redux';
import { RamaClient } from '@rama-ui/core';
import { Datasource, RootState } from 'src/dashboard/types';

// update datasources index for Dashboard
export enum DatasourcesAction {
  SetDatasources = 'SET_DATASOURCES',
  SetDatasource = 'SET_DATASOURCE',
}

export type DatasourcesActionPayload =
  | {
      type: DatasourcesAction.SetDatasources;
      datasources: Datasource[] | null;
    }
  | {
      type: DatasourcesAction.SetDatasource;
      key: Datasource['uid'];
      datasource: Datasource;
    };

export function setDatasources(datasources: Datasource[] | null) {
  return {
    type: DatasourcesAction.SetDatasources,
    datasources,
  };
}

export function setDatasource(datasource: Datasource, key: string) {
  return {
    type: DatasourcesAction.SetDatasource,
    key,
    datasource,
  };
}

export function fetchDatasourceMetadata(key: string) {
  return (dispatch: Dispatch, getState: () => RootState) => {
    const { datasources } = getState();
    const datasource = datasources[key];

    if (datasource) {
      return dispatch(setDatasource(datasource, key));
    }

    return RamaClient.get({
      endpoint: `/rama/fetch_datasource_metadata?datasourceKey=${key}`,
    }).then(({ json }) => dispatch(setDatasource(json as Datasource, key)));
  };
}
