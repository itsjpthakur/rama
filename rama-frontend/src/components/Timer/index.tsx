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
import { useEffect, useRef, useState } from 'react';
import { styled } from '@rama-ui/core';
import Label, { Type } from 'src/components/Label';
import Icons from 'src/components/Icons';

import { now, fDuration } from 'src/utils/dates';

export interface TimerProps {
  endTime?: number;
  isRunning: boolean;
  startTime?: number;
  status?: Type;
}

const TimerLabel = styled(Label)`
  text-align: left;
  font-family: ${({ theme }) => theme.typography.families.monospace};
`;

export default function Timer({
  endTime,
  isRunning,
  startTime,
  status = 'success',
}: TimerProps) {
  const [clockStr, setClockStr] = useState('00:00:00.00');
  const timer = useRef<ReturnType<typeof setInterval>>();

  useEffect(() => {
    const stopTimer = () => {
      if (timer.current) {
        clearInterval(timer.current);
        timer.current = undefined;
      }
    };

    if (isRunning) {
      timer.current = setInterval(() => {
        if (startTime) {
          const endDttm = endTime || now();
          if (startTime < endDttm) {
            setClockStr(fDuration(startTime, endDttm));
          }
          if (!isRunning) {
            stopTimer();
          }
        }
      }, 30);
    }
    return stopTimer;
  }, [endTime, isRunning, startTime]);

  return (
    <TimerLabel icon={<Icons.Clock iconSize="m" />} type={status} role="timer">
      {clockStr}
    </TimerLabel>
  );
}
