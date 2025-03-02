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

## @rama-ui/plugin-chart-word-cloud

[![Version](https://img.shields.io/npm/v/@rama-ui/plugin-chart-word-cloud.svg?style=flat)](https://www.npmjs.com/package/@rama-ui/plugin-chart-word-cloud)
[![Libraries.io](https://img.shields.io/librariesio/release/npm/%40rama-ui%2Fplugin-chart-word-cloud?style=flat)](https://libraries.io/npm/@rama-ui%2Fplugin-chart-word-cloud)

This plugin provides Word Cloud for Rama.

### Usage

Configure `key`, which can be any `string`, and register the plugin. This `key` will be used to
lookup this chart throughout the app.

```js
import WordCloudChartPlugin from '@rama-ui/plugin-chart-word-cloud';

new WordCloudChartPlugin().configure({ key: 'word-cloud' }).register();
```

Then use it via `SuperChart`. See
[storybook](https://apache-rama.github.io/rama-ui-plugins/?selectedKind=plugin-chart-word-cloud)
for more details.

```js
<SuperChart
  chartType="word-cloud"
  width={600}
  height={600}
  formData={...}
  queriesData={[{
    data: {...},
  }]}
/>
```
