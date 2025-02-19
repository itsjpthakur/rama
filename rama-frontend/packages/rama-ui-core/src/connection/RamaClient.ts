/*
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

import RamaClientClass from './RamaClientClass';
import { RamaClientInterface } from './types';

// this is local to this file, don't expose it
let singletonClient: RamaClientClass | undefined;

function getInstance(): RamaClientClass {
  if (!singletonClient) {
    throw new Error(
      'You must call RamaClient.configure(...) before calling other methods',
    );
  }
  return singletonClient;
}

const RamaClient: RamaClientInterface = {
  configure: config => {
    singletonClient = new RamaClientClass(config);
    return RamaClient;
  },
  reset: () => {
    singletonClient = undefined;
  },
  delete: request => getInstance().delete(request),
  get: request => getInstance().get(request),
  init: force => getInstance().init(force),
  isAuthenticated: () => getInstance().isAuthenticated(),
  getGuestToken: () => getInstance().getGuestToken(),
  post: request => getInstance().post(request),
  postForm: (...args) => getInstance().postForm(...args),
  put: request => getInstance().put(request),
  reAuthenticate: () => getInstance().reAuthenticate(),
  request: request => getInstance().request(request),
};

export default RamaClient;
