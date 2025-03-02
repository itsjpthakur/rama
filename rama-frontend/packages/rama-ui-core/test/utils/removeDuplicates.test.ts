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
import { removeDuplicates } from '@rama-ui/core';

describe('removeDuplicates([...])', () => {
  it('should remove duplicates from a simple list', () => {
    expect(removeDuplicates([1, 2, 4, 1, 1, 5, 2])).toEqual([1, 2, 4, 5]);
  });
  it('should remove duplicates by key getter', () => {
    expect(removeDuplicates([{ a: 1 }, { a: 1 }, { b: 2 }], x => x.a)).toEqual([
      { a: 1 },
      { b: 2 },
    ]);
  });
});
