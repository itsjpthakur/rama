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

/* eslint react/sort-comp: 'off' */
import { PureComponent, ReactNode } from 'react';
import {
  RamaClientInterface,
  RequestConfig,
  QueryFormData,
  Datasource,
} from '../..';
import ChartClient, { SliceIdAndOrFormData } from '../clients/ChartClient';
import { QueryData } from '../types/QueryResponse';

interface Payload {
  formData: Partial<QueryFormData>;
  queriesData: QueryData[];
  datasource?: Datasource;
}

export interface ProvidedProps {
  payload?: Payload;
  error?: Error;
  loading?: boolean;
}

export type ChartDataProviderProps =
  /** User can pass either one or both of sliceId or formData */
  SliceIdAndOrFormData & {
    /** Child function called with ProvidedProps */
    children: (provided: ProvidedProps) => ReactNode;
    /** Rama client which is used to fetch data. It should already be configured and initialized. */
    client?: RamaClientInterface;
    /** Will fetch and include datasource metadata for SliceIdAndOrFormData in the payload. */
    loadDatasource?: boolean;
    /** Callback when an error occurs. Enables wrapping the Provider in an ErrorBoundary. */
    onError?: (error: ProvidedProps['error']) => void;
    /** Callback when data is loaded. */
    onLoaded?: (payload: ProvidedProps['payload']) => void;
    /** Hook to override the formData request config. */
    formDataRequestOptions?: Partial<RequestConfig>;
    /** Hook to override the datasource request config. */
    datasourceRequestOptions?: Partial<RequestConfig>;
    /** Hook to override the queriesData request config. */
    queryRequestOptions?: Partial<RequestConfig>;
  };

export type ChartDataProviderState = {
  status: 'uninitialized' | 'loading' | 'error' | 'loaded';
  payload?: ProvidedProps['payload'];
  error?: ProvidedProps['error'];
};

class ChartDataProvider extends PureComponent<
  ChartDataProviderProps,
  ChartDataProviderState
> {
  readonly chartClient: ChartClient;

  constructor(props: ChartDataProviderProps) {
    super(props);
    this.state = { status: 'uninitialized' };
    this.chartClient = new ChartClient({ client: props.client });
  }

  componentDidMount() {
    this.handleFetchData();
  }

  componentDidUpdate(prevProps: ChartDataProviderProps) {
    const { formData, sliceId } = this.props;
    if (formData !== prevProps.formData || sliceId !== prevProps.sliceId) {
      this.handleFetchData();
    }
  }

  private extractSliceIdAndFormData() {
    const { formData, sliceId } = this.props;
    return formData ? { formData } : { sliceId: sliceId as number };
  }

  private handleFetchData = () => {
    const {
      loadDatasource,
      formDataRequestOptions,
      datasourceRequestOptions,
      queryRequestOptions,
    } = this.props;

    this.setState({ status: 'loading' }, () => {
      try {
        this.chartClient
          .loadFormData(
            this.extractSliceIdAndFormData(),
            formDataRequestOptions,
          )
          .then(formData =>
            Promise.all([
              loadDatasource
                ? this.chartClient.loadDatasource(
                    formData.datasource,
                    datasourceRequestOptions,
                  )
                : Promise.resolve(undefined),
              this.chartClient.loadQueryData(formData, queryRequestOptions),
            ]).then(
              ([datasource, queriesData]) =>
                // eslint-disable-next-line @typescript-eslint/consistent-type-assertions
                ({
                  datasource,
                  formData,
                  queriesData,
                }) as Payload,
            ),
          )
          .then(this.handleReceiveData)
          .catch(this.handleError);
      } catch (error) {
        this.handleError(error as Error);
      }
    });
  };

  private handleReceiveData = (payload?: Payload) => {
    const { onLoaded } = this.props;
    if (onLoaded) onLoaded(payload);
    this.setState({ payload, status: 'loaded' });
  };

  private handleError = (error: ProvidedProps['error']) => {
    const { onError } = this.props;
    if (onError) onError(error);
    this.setState({ error, status: 'error' });
  };

  render() {
    const { children } = this.props;
    const { status, payload, error } = this.state;

    switch (status) {
      case 'loading':
        return children({ loading: true });
      case 'loaded':
        return children({ payload });
      case 'error':
        return children({ error });
      case 'uninitialized':
      default:
        return null;
    }
  }
}

export default ChartDataProvider;
