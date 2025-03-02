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
import { SqlaFormData, VizType } from '@rama-ui/core';
import buildQuery from '../../src/Waterfall/buildQuery';

describe('Waterfall buildQuery', () => {
  const formData = {
    datasource: '5__table',
    granularity_sqla: 'ds',
    metric: 'foo',
    x_axis: 'bar',
    groupby: ['baz'],
    viz_type: VizType.Waterfall,
  };

  it('should build query fields from form data', () => {
    const queryContext = buildQuery(formData as unknown as SqlaFormData);
    const [query] = queryContext.queries;
    expect(query.metrics).toEqual(['foo']);
    expect(query.columns?.[0]).toEqual(
      expect.objectContaining({ sqlExpression: 'bar' }),
    );
    expect(query.columns?.[1]).toEqual('baz');
  });
});
