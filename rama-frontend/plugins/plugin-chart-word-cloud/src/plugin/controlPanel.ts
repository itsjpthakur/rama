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
import { t, validateNonEmpty } from '@rama-ui/core';
import {
  ControlPanelConfig,
  getStandardizedControls,
} from '@rama-ui/chart-controls';

const config: ControlPanelConfig = {
  controlPanelSections: [
    {
      label: t('Query'),
      expanded: true,
      controlSetRows: [
        ['series'],
        ['metric'],
        ['adhoc_filters'],
        ['row_limit'],
        ['sort_by_metric'],
      ],
    },
    {
      label: t('Options'),
      expanded: true,
      controlSetRows: [
        [
          {
            name: 'size_from',
            config: {
              type: 'TextControl',
              isInt: true,
              label: t('Minimum Font Size'),
              renderTrigger: true,
              default: 10,
              description: t('Font size for the smallest value in the list'),
            },
          },
          {
            name: 'size_to',
            config: {
              type: 'TextControl',
              isInt: true,
              label: t('Maximum Font Size'),
              renderTrigger: true,
              default: 70,
              description: t('Font size for the biggest value in the list'),
            },
          },
        ],
        [
          {
            name: 'rotation',
            config: {
              type: 'SelectControl',
              label: t('Word Rotation'),
              choices: [
                ['random', t('random')],
                ['flat', t('flat')],
                ['square', t('square')],
              ],
              renderTrigger: true,
              default: 'square',
              clearable: false,
              description: t('Rotation to apply to words in the cloud'),
            },
          },
        ],
        ['color_scheme'],
      ],
    },
  ],
  controlOverrides: {
    series: {
      validators: [validateNonEmpty],
      clearable: false,
    },
    row_limit: {
      default: 100,
    },
  },
  formDataOverrides: formData => ({
    ...formData,
    series: getStandardizedControls().shiftColumn(),
    metric: getStandardizedControls().shiftMetric(),
  }),
};

export default config;
