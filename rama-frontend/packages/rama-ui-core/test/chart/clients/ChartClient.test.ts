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

import fetchMock from 'fetch-mock';
import {
  RamaClientClass,
  RamaClient,
  buildQueryContext,
  QueryFormData,
  configure as configureTranslation,
  ChartClient,
  getChartBuildQueryRegistry,
  getChartMetadataRegistry,
  ChartMetadata,
  VizType,
} from '@rama-ui/core';

import { LOGIN_GLOB } from '../fixtures/constants';
import { sankeyFormData } from '../fixtures/formData';
import { SliceIdAndOrFormData } from '../../../src/chart/clients/ChartClient';

configureTranslation();

describe('ChartClient', () => {
  let chartClient: ChartClient;

  beforeAll(() => {
    fetchMock.get(LOGIN_GLOB, { result: '1234' });
    RamaClient.reset();
    RamaClient.configure().init();
  });

  beforeEach(() => {
    chartClient = new ChartClient();
  });

  afterEach(() => fetchMock.restore());

  describe('new ChartClient(config)', () => {
    it('creates a client without argument', () => {
      expect(chartClient).toBeInstanceOf(ChartClient);
    });
    it('creates a client with specified config.client', () => {
      const customClient = new RamaClientClass();
      chartClient = new ChartClient({ client: customClient });
      expect(chartClient).toBeInstanceOf(ChartClient);
      expect(chartClient.client).toBe(customClient);
    });
  });

  describe('.loadFormData({ sliceId, formData }, options)', () => {
    const sliceId = 123;
    it('fetches formData if given only sliceId', () => {
      fetchMock.get(
        `glob:*/api/v1/form_data/?slice_id=${sliceId}`,
        sankeyFormData,
      );

      return expect(chartClient.loadFormData({ sliceId })).resolves.toEqual(
        sankeyFormData,
      );
    });
    it('fetches formData from sliceId and merges with specify formData if both fields are specified', () => {
      fetchMock.get(
        `glob:*/api/v1/form_data/?slice_id=${sliceId}`,
        sankeyFormData,
      );

      return expect(
        chartClient.loadFormData({
          sliceId,
          formData: {
            granularity: 'second',
            viz_type: VizType.Bar,
          },
        }),
      ).resolves.toEqual({
        ...sankeyFormData,
        granularity: 'second',
        viz_type: VizType.Bar,
      });
    });
    it('returns promise of formData if only formData was given', () =>
      expect(
        chartClient.loadFormData({
          formData: {
            datasource: '1__table',
            granularity: 'minute',
            viz_type: VizType.Line,
          },
        }),
      ).resolves.toEqual({
        datasource: '1__table',
        granularity: 'minute',
        viz_type: VizType.Line,
      }));
    it('rejects if none of sliceId or formData is specified', () =>
      expect(
        chartClient.loadFormData({} as SliceIdAndOrFormData),
      ).rejects.toEqual(
        new Error('At least one of sliceId or formData must be specified'),
      ));
  });

  describe('.loadQueryData(formData, options)', () => {
    it('returns a promise of query data for known chart type', () => {
      getChartMetadataRegistry().registerValue(
        VizType.WordCloud,
        new ChartMetadata({ name: 'Word Cloud', thumbnail: '' }),
      );

      getChartBuildQueryRegistry().registerValue(
        VizType.WordCloud,
        (formData: QueryFormData) => buildQueryContext(formData),
      );
      fetchMock.post('glob:*/api/v1/chart/data', [
        {
          field1: 'abc',
          field2: 'def',
        },
      ]);

      return expect(
        chartClient.loadQueryData({
          granularity: 'minute',
          viz_type: VizType.WordCloud,
          datasource: '1__table',
        }),
      ).resolves.toEqual([
        {
          field1: 'abc',
          field2: 'def',
        },
      ]);
    });
    it('returns a promise that rejects for unknown chart type', () =>
      expect(
        chartClient.loadQueryData({
          granularity: 'minute',
          viz_type: 'rainbow_3d_pie',
          datasource: '1__table',
        }),
      ).rejects.toEqual(new Error('Unknown chart type: rainbow_3d_pie')));

    it('fetches data from the legacy API if ChartMetadata has useLegacyApi=true,', () => {
      // note legacy charts do not register a buildQuery function in the registry
      getChartMetadataRegistry().registerValue(
        'word_cloud_legacy',
        new ChartMetadata({
          name: 'Legacy Word Cloud',
          thumbnail: '.png',
          useLegacyApi: true,
        }),
      );

      fetchMock.post('glob:*/api/v1/chart/data', () =>
        Promise.reject(new Error('Unexpected all to v1 API')),
      );

      fetchMock.post('glob:*/rama/explore_json/', {
        field1: 'abc',
        field2: 'def',
      });

      return expect(
        chartClient.loadQueryData({
          granularity: 'minute',
          viz_type: 'word_cloud_legacy',
          datasource: '1__table',
        }),
      ).resolves.toEqual([
        {
          field1: 'abc',
          field2: 'def',
        },
      ]);
    });
  });

  describe('.loadDatasource(datasourceKey, options)', () => {
    it('fetches datasource', () => {
      fetchMock.get(
        'glob:*/rama/fetch_datasource_metadata?datasourceKey=1__table',
        {
          field1: 'abc',
          field2: 'def',
        },
      );

      return expect(chartClient.loadDatasource('1__table')).resolves.toEqual({
        field1: 'abc',
        field2: 'def',
      });
    });
  });

  describe('.loadAnnotation(annotationLayer)', () => {
    it('returns an empty object if the annotation layer does not require query', () =>
      expect(
        chartClient.loadAnnotation({
          name: 'my-annotation',
        }),
      ).resolves.toEqual({}));
    it('otherwise returns a rejected promise because it is not implemented yet', () =>
      expect(
        chartClient.loadAnnotation({
          name: 'my-annotation',
          sourceType: 'abc',
        }),
      ).rejects.toEqual(new Error('This feature is not implemented yet.')));
  });

  describe('.loadAnnotations(annotationLayers)', () => {
    it('loads multiple annotation layers and combine results', () =>
      expect(
        chartClient.loadAnnotations([
          {
            name: 'anno1',
          },
          {
            name: 'anno2',
          },
          {
            name: 'anno3',
          },
        ]),
      ).resolves.toEqual({
        anno1: {},
        anno2: {},
        anno3: {},
      }));
    it('returns an empty object if input is not an array', () =>
      expect(chartClient.loadAnnotations()).resolves.toEqual({}));
    it('returns an empty object if input is an empty array', () =>
      expect(chartClient.loadAnnotations()).resolves.toEqual({}));
  });

  describe('.loadChartData({ sliceId, formData })', () => {
    const sliceId = 10120;
    it('loadAllDataNecessaryForAChart', () => {
      fetchMock.get(`glob:*/api/v1/form_data/?slice_id=${sliceId}`, {
        granularity: 'minute',
        viz_type: VizType.Line,
        datasource: '1__table',
        color: 'living-coral',
      });

      fetchMock.get(
        'glob:*/rama/fetch_datasource_metadata?datasourceKey=1__table',
        {
          name: 'transactions',
          schema: 'staging',
        },
      );

      fetchMock.post('glob:*/api/v1/chart/data', {
        lorem: 'ipsum',
        dolor: 'sit',
        amet: true,
      });

      getChartMetadataRegistry().registerValue(
        VizType.Line,
        new ChartMetadata({ name: 'Line', thumbnail: '.gif' }),
      );

      getChartBuildQueryRegistry().registerValue(
        VizType.Line,
        (formData: QueryFormData) => buildQueryContext(formData),
      );

      return expect(
        chartClient.loadChartData({
          sliceId,
        }),
      ).resolves.toEqual({
        annotationData: {},
        datasource: {
          name: 'transactions',
          schema: 'staging',
        },
        formData: {
          granularity: 'minute',
          viz_type: VizType.Line,
          datasource: '1__table',
          color: 'living-coral',
        },
        queriesData: [
          {
            lorem: 'ipsum',
            dolor: 'sit',
            amet: true,
          },
        ],
      });
    });
  });
});
