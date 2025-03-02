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
import { Behavior } from '@rama-ui/core';
import { DashboardLayout } from 'src/dashboard/types';
import { CHART_TYPE } from 'src/dashboard/util/componentTypes';
import { nativeFilterGate, findTabsWithChartsInScope } from './utils';

describe('nativeFilterGate', () => {
  it('should return true for regular chart', () => {
    expect(nativeFilterGate([])).toEqual(true);
  });

  it('should return true for cross filter chart', () => {
    expect(nativeFilterGate([Behavior.InteractiveChart])).toEqual(true);
  });

  it('should return true for native filter chart with cross filter support', () => {
    expect(
      nativeFilterGate([Behavior.NativeFilter, Behavior.InteractiveChart]),
    ).toEqual(true);
  });

  it('should return false for native filter behavior', () => {
    expect(nativeFilterGate([Behavior.NativeFilter])).toEqual(false);
  });
});

test('findTabsWithChartsInScope should handle a recursive layout structure', () => {
  const dashboardLayout = {
    DASHBOARD_VERSION_KEY: 'v2',
    ROOT_ID: {
      children: ['GRID_ID'],
      id: 'ROOT_ID',
      type: 'ROOT',
    },
    GRID_ID: {
      children: ['TAB-LrujeuD5Qn', 'TABS-kN7tw6vFif'],
      id: 'GRID_ID',
      parents: ['ROOT_ID'],
      type: 'GRID',
    },
    'TAB-LrujeuD5Qn': {
      children: ['TABS-kN7tw6vFif'],
      id: 'TAB-LrujeuD5Qn',
      meta: {
        text: 'View by Totals',
      },
      parents: ['ROOT_ID'],
      type: 'TAB',
    },
    'TABS-kN7tw6vFif': {
      children: ['TAB-LrujeuD5Qn', 'TAB--7BUkKkNl'],
      id: 'TABS-kN7tw6vFif',
      meta: {},
      parents: ['ROOT_ID'],
      type: 'TABS',
    },
  } as any as DashboardLayout;

  const chartLayoutItems = Object.values(dashboardLayout).filter(
    item => item.type === CHART_TYPE,
  );
  expect(Array.from(findTabsWithChartsInScope(chartLayoutItems, []))).toEqual(
    [],
  );
});
