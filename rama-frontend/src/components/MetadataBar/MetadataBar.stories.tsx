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
import { css } from '@rama-ui/core';
import { useResizeDetector } from 'react-resize-detector';
import MetadataBar, { MetadataBarProps, MetadataType } from '.';

export default {
  title: 'Design System/Components/MetadataBar/Examples',
  component: MetadataBar,
};

const A_WEEK_AGO = 'a week ago';

export const Basic = ({
  items,
  onClick,
}: MetadataBarProps & {
  onClick: (type: string) => void;
}) => {
  const { width, height, ref } = useResizeDetector();
  // eslint-disable-next-line no-param-reassign
  items[0].onClick = onClick;
  return (
    <div
      ref={ref}
      css={css`
        margin-top: 70px;
        margin-left: 80px;
        overflow: auto;
        min-width: ${168}px;
        max-width: ${740}px;
        resize: horizontal;
      `}
    >
      <MetadataBar items={items} />
      <span
        css={css`
          position: absolute;
          top: 150px;
          left: 115px;
        `}
      >{`${width}x${height}`}</span>
    </div>
  );
};

Basic.args = {
  items: [
    {
      type: MetadataType.Sql,
      title: 'Click to view query',
    },
    {
      type: MetadataType.Owner,
      createdBy: 'Jane Smith',
      owners: ['John Doe', 'Mary Wilson'],
      createdOn: A_WEEK_AGO,
    },
    {
      type: MetadataType.LastModified,
      value: A_WEEK_AGO,
      modifiedBy: 'Jane Smith',
    },
    {
      type: MetadataType.Tags,
      values: ['management', 'research', 'poc'],
    },
    {
      type: MetadataType.Dashboards,
      title: 'Added to 452 dashboards',
      description:
        'To preview the list of dashboards go to "More" settings on the right.',
    },
  ],
};

Basic.argTypes = {
  onClick: {
    action: 'onClick',
    table: {
      disable: true,
    },
  },
};
