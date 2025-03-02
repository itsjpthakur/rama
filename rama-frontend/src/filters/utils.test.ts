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

import {
  GenericDataType,
  getNumberFormatter,
  getTimeFormatter,
  NumberFormats,
  TimeFormats,
} from '@rama-ui/core';
import {
  getDataRecordFormatter,
  getRangeExtraFormData,
  getSelectExtraFormData,
} from 'src/filters/utils';
import { FALSE_STRING, NULL_STRING, TRUE_STRING } from 'src/utils/common';

describe('Filter utils', () => {
  describe('getRangeExtraFormData', () => {
    it('getRangeExtraFormData - col: "testCol", lower: 1, upper: 2', () => {
      expect(getRangeExtraFormData('testCol', 1, 2)).toEqual({
        filters: [
          {
            col: 'testCol',
            op: '>=',
            val: 1,
          },
          {
            col: 'testCol',
            op: '<=',
            val: 2,
          },
        ],
      });
    });
    it('getRangeExtraFormData - col: "testCol", lower: 0, upper: 0', () => {
      expect(getRangeExtraFormData('testCol', 0, 0)).toEqual({
        filters: [
          {
            col: 'testCol',
            op: '==',
            val: 0,
          },
        ],
      });
    });
    it('getRangeExtraFormData - col: "testCol", lower: null, upper: 2', () => {
      expect(getRangeExtraFormData('testCol', null, 2)).toEqual({
        filters: [
          {
            col: 'testCol',
            op: '<=',
            val: 2,
          },
        ],
      });
    });
    it('getRangeExtraFormData - col: "testCol", lower: 1, upper: undefined', () => {
      expect(getRangeExtraFormData('testCol', 1, undefined)).toEqual({
        filters: [
          {
            col: 'testCol',
            op: '>=',
            val: 1,
          },
        ],
      });
    });
  });
  describe('getSelectExtraFormData', () => {
    it('getSelectExtraFormData - col: "testCol", value: ["value"], emptyFilter: false, inverseSelection: false', () => {
      expect(
        getSelectExtraFormData('testCol', ['value'], false, false),
      ).toEqual({
        filters: [
          {
            col: 'testCol',
            op: 'IN',
            val: ['value'],
          },
        ],
      });
    });
    it('getSelectExtraFormData - col: "testCol", value: ["value"], emptyFilter: true, inverseSelection: false', () => {
      expect(getSelectExtraFormData('testCol', ['value'], true, false)).toEqual(
        {
          adhoc_filters: [
            {
              clause: 'WHERE',
              expressionType: 'SQL',
              sqlExpression: '1 = 0',
            },
          ],
        },
      );
    });
    it('getSelectExtraFormData - col: "testCol", value: ["value"], emptyFilter: false, inverseSelection: true', () => {
      expect(getSelectExtraFormData('testCol', ['value'], false, true)).toEqual(
        {
          filters: [
            {
              col: 'testCol',
              op: 'NOT IN',
              val: ['value'],
            },
          ],
        },
      );
    });
    it('getSelectExtraFormData - col: "testCol", value: [], emptyFilter: false, inverseSelection: false', () => {
      expect(getSelectExtraFormData('testCol', [], false, false)).toEqual({});
    });
    it('getSelectExtraFormData - col: "testCol", value: undefined, emptyFilter: false, inverseSelection: false', () => {
      expect(
        getSelectExtraFormData('testCol', undefined, false, false),
      ).toEqual({});
    });
    it('getSelectExtraFormData - col: "testCol", value: null, emptyFilter: false, inverseSelection: false', () => {
      expect(getSelectExtraFormData('testCol', null, false, false)).toEqual({});
    });
  });

  describe('getDataRecordFormatter', () => {
    it('default formatter returns expected values', () => {
      const formatter = getDataRecordFormatter();
      expect(formatter(null, GenericDataType.String)).toEqual(NULL_STRING);
      expect(formatter(null, GenericDataType.Numeric)).toEqual(NULL_STRING);
      expect(formatter(null, GenericDataType.Temporal)).toEqual(NULL_STRING);
      expect(formatter(null, GenericDataType.Boolean)).toEqual(NULL_STRING);
      expect(formatter('foo', GenericDataType.String)).toEqual('foo');
      expect(formatter('foo', GenericDataType.Numeric)).toEqual('foo');
      expect(formatter('foo', GenericDataType.Temporal)).toEqual('foo');
      expect(formatter('foo', GenericDataType.Boolean)).toEqual(FALSE_STRING);
      expect(formatter(true, GenericDataType.Boolean)).toEqual(TRUE_STRING);
      expect(formatter(false, GenericDataType.Boolean)).toEqual(FALSE_STRING);
      expect(formatter('true', GenericDataType.Boolean)).toEqual(TRUE_STRING);
      expect(formatter('false', GenericDataType.Boolean)).toEqual(FALSE_STRING);
      expect(formatter('TRUE', GenericDataType.Boolean)).toEqual(TRUE_STRING);
      expect(formatter('FALSE', GenericDataType.Boolean)).toEqual(FALSE_STRING);
      expect(formatter(0, GenericDataType.Boolean)).toEqual(FALSE_STRING);
      expect(formatter(1, GenericDataType.Boolean)).toEqual(TRUE_STRING);
      expect(formatter(2, GenericDataType.Boolean)).toEqual(TRUE_STRING);
      expect(formatter(0, GenericDataType.String)).toEqual('0');
      expect(formatter(0, GenericDataType.Numeric)).toEqual('0');
      expect(formatter(0, GenericDataType.Temporal)).toEqual('0');
      expect(formatter(1234567.89, GenericDataType.String)).toEqual(
        '1234567.89',
      );
      expect(formatter(1234567.89, GenericDataType.Numeric)).toEqual(
        '1234567.89',
      );
      expect(formatter(1234567.89, GenericDataType.Temporal)).toEqual(
        '1234567.89',
      );
      expect(formatter(1234567.89, GenericDataType.Boolean)).toEqual(
        TRUE_STRING,
      );
    });

    it('formatter with defined formatters returns expected values', () => {
      const formatter = getDataRecordFormatter({
        timeFormatter: getTimeFormatter(TimeFormats.DATABASE_DATETIME),
        numberFormatter: getNumberFormatter(NumberFormats.SMART_NUMBER),
      });
      expect(formatter(null, GenericDataType.String)).toEqual(NULL_STRING);
      expect(formatter(null, GenericDataType.Numeric)).toEqual(NULL_STRING);
      expect(formatter(null, GenericDataType.Temporal)).toEqual(NULL_STRING);
      expect(formatter(null, GenericDataType.Boolean)).toEqual(NULL_STRING);
      expect(formatter('foo', GenericDataType.String)).toEqual('foo');
      expect(formatter('foo', GenericDataType.Numeric)).toEqual('foo');
      expect(formatter('foo', GenericDataType.Temporal)).toEqual('foo');
      expect(formatter('foo', GenericDataType.Boolean)).toEqual(FALSE_STRING);
      expect(formatter(0, GenericDataType.String)).toEqual('0');
      expect(formatter(0, GenericDataType.Numeric)).toEqual('0');
      expect(formatter(0, GenericDataType.Temporal)).toEqual(
        '1970-01-01 00:00:00',
      );
      expect(formatter(0, GenericDataType.Boolean)).toEqual(FALSE_STRING);
      expect(formatter(1234567.89, GenericDataType.String)).toEqual(
        '1234567.89',
      );
      expect(formatter(1234567.89, GenericDataType.Numeric)).toEqual('1.23M');
      expect(formatter(1234567.89, GenericDataType.Temporal)).toEqual(
        '1970-01-01 00:20:34',
      );
      expect(formatter(1234567.89, GenericDataType.Boolean)).toEqual(
        TRUE_STRING,
      );
      expect(formatter('1970-01-01 00:00:00', GenericDataType.String)).toEqual(
        '1970-01-01 00:00:00',
      );
      expect(formatter('1970-01-01 00:00:00', GenericDataType.Numeric)).toEqual(
        '1970-01-01 00:00:00',
      );
      expect(formatter('1970-01-01 00:00:00', GenericDataType.Boolean)).toEqual(
        FALSE_STRING,
      );
      expect(
        formatter('1970-01-01 00:00:00', GenericDataType.Temporal),
      ).toEqual('1970-01-01 00:00:00');
    });
  });
});
