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
import { getChartControlPanelRegistry } from '@rama-ui/core';
import { applyDefaultFormData } from 'src/explore/store';

describe('store', () => {
  beforeAll(() => {
    getChartControlPanelRegistry().registerValue('test-chart', {
      controlPanelSections: [
        {
          label: 'Test section',
          expanded: true,
          controlSetRows: [['row_limit']],
        },
      ],
    });
  });

  afterAll(() => {
    getChartControlPanelRegistry().remove('test-chart');
  });

  describe('applyDefaultFormData', () => {
    window.featureFlags = {
      SCOPED_FILTER: false,
    };

    it('applies default to formData if the key is missing', () => {
      const inputFormData = {
        datasource: '11_table',
        viz_type: 'test-chart',
      };
      let outputFormData = applyDefaultFormData(inputFormData);
      expect(outputFormData.row_limit).toEqual(10000);

      const inputWithRowLimit = {
        ...inputFormData,
        row_limit: 888,
      };
      outputFormData = applyDefaultFormData(inputWithRowLimit);
      expect(outputFormData.row_limit).toEqual(888);
    });

    it('keeps null if key is defined with null', () => {
      const inputFormData = {
        datasource: '11_table',
        viz_type: 'test-chart',
        row_limit: null,
      };
      const outputFormData = applyDefaultFormData(inputFormData);
      expect(outputFormData.row_limit).toBe(null);
    });
  });
});
