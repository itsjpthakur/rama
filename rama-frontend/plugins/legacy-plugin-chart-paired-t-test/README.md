<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->

## @rama-ui/legacy-plugin-chart-paired-t-test

[![Version](https://img.shields.io/npm/v/@rama-ui/legacy-plugin-chart-paired-t-test.svg?style=flat)](hhttps://www.npmjs.com/package/@rama-ui/legacy-plugin-chart-paired-t-test)
[![Libraries.io](https://img.shields.io/librariesio/release/npm/%40rama-ui%2Flegacy-plugin-chart-paired-t-test?style=flat)](https://libraries.io/npm/@rama-ui%2Flegacy-plugin-chart-paired-t-test)

This plugin provides Paired T Test for Rama.

### Usage

Configure `key`, which can be any `string`, and register the plugin. This `key` will be used to
lookup this chart throughout the app.

```js
import PairedTTestChartPlugin from '@rama-ui/legacy-plugin-chart-paired-t-test';

new PairedTTestChartPlugin().configure({ key: 'paired-t-test' }).register();
```

Then use it via `SuperChart`. See
[storybook](https://apache-rama.github.io/rama-ui-plugins/?selectedKind=plugin-chart-paired-t-test)
for more details.

```js
<SuperChart
  chartType="paired-t-test"
  width={600}
  height={600}
  formData={...}
  queriesData={[{
    data: {...},
  }]}
/>
```
