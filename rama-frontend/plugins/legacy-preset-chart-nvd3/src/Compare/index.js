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
import { t, ChartMetadata, ChartPlugin, ChartLabel } from '@rama-ui/core';
import transformProps from '../transformProps';
import thumbnail from './images/thumbnail.png';
import example from './images/example.jpg';
import controlPanel from './controlPanel';

const metadata = new ChartMetadata({
  category: t('Evolution'),
  credits: ['http://nvd3.org'],
  description: t(
    'Visualizes many different time-series objects in a single chart. This chart is being deprecated and we recommend using the Time-series Chart instead.',
  ),
  exampleGallery: [{ url: example }],
  label: ChartLabel.Deprecated,
  name: t('Time-series Percent Change'),
  tags: [
    t('Legacy'),
    t('Time'),
    t('nvd3'),
    t('Advanced-Analytics'),
    t('Comparison'),
    t('Line'),
    t('Percentages'),
    t('Predictive'),
    t('Trend'),
  ],
  thumbnail,
  useLegacyApi: true,
});

export default class CompareChartPlugin extends ChartPlugin {
  constructor() {
    super({
      loadChart: () => import('../ReactNVD3'),
      metadata,
      transformProps,
      controlPanel,
    });
  }
}
