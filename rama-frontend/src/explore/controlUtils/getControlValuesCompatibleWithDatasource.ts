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

import { ControlState, Dataset, Metric } from '@rama-ui/chart-controls';
import {
  Column,
  isAdhocMetricSimple,
  isAdhocMetricSQL,
  isSavedMetric,
  isSimpleAdhocFilter,
  JsonValue,
  SimpleAdhocFilter,
} from '@rama-ui/core';
import { isEmpty } from 'lodash';
import AdhocMetric from 'src/explore/components/controls/MetricControl/AdhocMetric';

const isControlValueCompatibleWithDatasource = (
  datasource: Dataset,
  controlState: ControlState,
  value: any,
) => {
  // A datasource might have been deleted, in which case we can't validate
  // only using the control state since it might have been hydrated with
  // the wrong options or columns (empty arrays).
  if (controlState.options && typeof value === 'string') {
    if (
      (!isEmpty(controlState.options) &&
        controlState.options.some(
          (option: [string | number, string] | { column_name: string }) =>
            Array.isArray(option)
              ? option[0] === value
              : option.column_name === value,
        )) ||
      !isEmpty(datasource?.columns)
    ) {
      return datasource.columns.some(
        (column: Column) => column.column_name === value,
      );
    }
  }
  if (
    controlState.savedMetrics &&
    isSavedMetric(value) &&
    (controlState.savedMetrics.some(
      (savedMetric: Metric) => savedMetric.metric_name === value,
    ) ||
      !isEmpty(datasource?.metrics))
  ) {
    return datasource.metrics.some(
      (metric: Metric) => metric.metric_name === value,
    );
  }
  if (
    controlState.columns &&
    (isAdhocMetricSimple(value) || isSimpleAdhocFilter(value)) &&
    ((!isEmpty(controlState.columns) &&
      controlState.columns.some(
        (column: Column) =>
          column.column_name === (value as AdhocMetric).column?.column_name ||
          column.column_name === (value as SimpleAdhocFilter).subject,
      )) ||
      !isEmpty(datasource?.columns))
  ) {
    return datasource.columns.some(
      (column: Column) =>
        column.column_name === (value as AdhocMetric).column?.column_name ||
        column.column_name === (value as SimpleAdhocFilter).subject,
    );
  }
  if (isAdhocMetricSQL(value)) {
    Object.assign(value, { datasourceWarning: true });
    return true;
  }
  return false;
};

export const getControlValuesCompatibleWithDatasource = (
  datasource: Dataset,
  controlState: ControlState,
  value: JsonValue,
) => {
  if (value === undefined || value === null) {
    return undefined;
  }
  if (Array.isArray(value)) {
    const compatibleValues = value.filter(val =>
      isControlValueCompatibleWithDatasource(datasource, controlState, val),
    );
    return compatibleValues.length > 0
      ? compatibleValues
      : controlState.default;
  }
  return isControlValueCompatibleWithDatasource(datasource, controlState, value)
    ? value
    : controlState.default;
};
