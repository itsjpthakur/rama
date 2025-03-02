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
import { ChartProps, SqlaFormData, ramaTheme } from '@rama-ui/core';
import transformProps from '../../src/Graph/transformProps';
import { DEFAULT_GRAPH_SERIES_OPTION } from '../../src/Graph/constants';
import { EchartsGraphChartProps } from '../../src/Graph/types';

describe('EchartsGraph transformProps', () => {
  it('should transform chart props for viz without category', () => {
    const formData: SqlaFormData = {
      colorScheme: 'bnbColors',
      datasource: '3__table',
      granularity_sqla: 'ds',
      metric: 'count',
      source: 'source_column',
      target: 'target_column',
      category: null,
      viz_type: 'graph',
    };
    const queriesData = [
      {
        colnames: ['source_column', 'target_column', 'count'],
        data: [
          {
            source_column: 'source_value_1',
            target_column: 'target_value_1',
            count: 6,
          },
          {
            source_column: 'source_value_2',
            target_column: 'target_value_2',
            count: 5,
          },
        ],
      },
    ];
    const chartPropsConfig = {
      formData,
      width: 800,
      height: 600,
      queriesData,
      theme: ramaTheme,
    };

    const chartProps = new ChartProps(chartPropsConfig);
    expect(transformProps(chartProps as EchartsGraphChartProps)).toEqual(
      expect.objectContaining({
        width: 800,
        height: 600,
        echartOptions: expect.objectContaining({
          legend: expect.objectContaining({
            data: [],
          }),
          series: expect.arrayContaining([
            expect.objectContaining({
              data: [
                {
                  col: 'source_column',
                  category: undefined,
                  id: '0',
                  itemStyle: {
                    color: '#1f77b4',
                  },
                  label: { show: true },
                  name: 'source_value_1',
                  select: {
                    itemStyle: { borderWidth: 3, opacity: 1 },
                    label: { fontWeight: 'bolder' },
                  },
                  symbolSize: 50,
                  tooltip: expect.anything(),
                  value: 6,
                },
                {
                  col: 'target_column',
                  category: undefined,
                  id: '1',
                  itemStyle: {
                    color: '#1f77b4',
                  },
                  label: { show: true },
                  name: 'target_value_1',
                  select: {
                    itemStyle: { borderWidth: 3, opacity: 1 },
                    label: { fontWeight: 'bolder' },
                  },
                  symbolSize: 50,
                  tooltip: expect.anything(),
                  value: 6,
                },
                {
                  col: 'source_column',
                  category: undefined,
                  id: '2',
                  itemStyle: {
                    color: '#1f77b4',
                  },
                  label: { show: true },
                  name: 'source_value_2',
                  select: {
                    itemStyle: { borderWidth: 3, opacity: 1 },
                    label: { fontWeight: 'bolder' },
                  },
                  symbolSize: 10,
                  tooltip: expect.anything(),
                  value: 5,
                },
                {
                  col: 'target_column',
                  category: undefined,
                  id: '3',
                  itemStyle: {
                    color: '#1f77b4',
                  },
                  label: { show: true },
                  name: 'target_value_2',
                  select: {
                    itemStyle: { borderWidth: 3, opacity: 1 },
                    label: { fontWeight: 'bolder' },
                  },
                  symbolSize: 10,
                  tooltip: expect.anything(),
                  value: 5,
                },
              ],
            }),
            expect.objectContaining({
              links: [
                {
                  emphasis: { lineStyle: { width: 12 } },
                  lineStyle: { width: 6, color: '#1f77b4' },
                  select: {
                    lineStyle: { opacity: 1, width: 9.600000000000001 },
                  },
                  source: '0',
                  target: '1',
                  value: 6,
                },
                {
                  emphasis: { lineStyle: { width: 5 } },
                  lineStyle: { width: 1.5, color: '#1f77b4' },
                  select: { lineStyle: { opacity: 1, width: 5 } },
                  source: '2',
                  target: '3',
                  value: 5,
                },
              ],
            }),
          ]),
        }),
      }),
    );
  });

  it('should transform chart props for viz with category and falsy normalization', () => {
    const formData: SqlaFormData = {
      colorScheme: 'bnbColors',
      datasource: '3__table',
      granularity_sqla: 'ds',
      metric: 'count',
      source: 'source_column',
      target: 'target_column',
      sourceCategory: 'source_category_column',
      targetCategory: 'target_category_column',
      viz_type: 'graph',
    };
    const queriesData = [
      {
        colnames: [
          'source_column',
          'target_column',
          'source_category_column',
          'target_category_column',
          'count',
        ],
        data: [
          {
            source_column: 'source_value',
            target_column: 'target_value',
            source_category_column: 'category_value_1',
            target_category_column: 'category_value_2',
            count: 6,
          },
          {
            source_column: 'source_value',
            target_column: 'target_value',
            source_category_column: 'category_value_1',
            target_category_column: 'category_value_2',
            count: 5,
          },
        ],
      },
    ];
    const chartPropsConfig = {
      formData,
      width: 800,
      height: 600,
      queriesData,
      theme: ramaTheme,
    };

    const chartProps = new ChartProps(chartPropsConfig);
    expect(transformProps(chartProps as EchartsGraphChartProps)).toEqual(
      expect.objectContaining({
        width: 800,
        height: 600,
        echartOptions: expect.objectContaining({
          legend: expect.objectContaining({
            data: ['category_value_1', 'category_value_2'],
          }),
          series: expect.arrayContaining([
            expect.objectContaining({
              data: [
                {
                  id: '0',
                  itemStyle: {
                    color: '#1f77b4',
                  },
                  col: 'source_column',
                  name: 'source_value',
                  value: 11,
                  symbolSize: 10,
                  category: 'category_value_1',
                  select: DEFAULT_GRAPH_SERIES_OPTION.select,
                  tooltip: expect.anything(),
                  label: { show: true },
                },
                {
                  id: '1',
                  itemStyle: {
                    color: '#ff7f0e',
                  },
                  col: 'target_column',
                  name: 'target_value',
                  value: 11,
                  symbolSize: 10,
                  category: 'category_value_2',
                  select: DEFAULT_GRAPH_SERIES_OPTION.select,
                  tooltip: expect.anything(),
                  label: { show: true },
                },
              ],
            }),
          ]),
        }),
      }),
    );
  });
});
