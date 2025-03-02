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
import { StoryFn, Meta } from '@storybook/react';
import { TimeFormats } from '@rama-ui/core';
import TimeCell from '.';

export default {
  title: 'Design System/Components/Table/Cell Renderers/TimeCell',
  component: TimeCell,
} as Meta<typeof TimeCell>;

export const Basic: StoryFn<typeof TimeCell> = args => <TimeCell {...args} />;

Basic.args = {
  value: new Date('2015-07-02T16:16:00Z').getTime(),
};

Basic.argTypes = {
  format: {
    defaultValue: TimeFormats.DATABASE_DATETIME,
    control: 'select',
    options: Object.values(TimeFormats),
  },
};
