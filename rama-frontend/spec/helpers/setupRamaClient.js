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
import fetchMock from 'fetch-mock';
// https://jestjs.io/docs/jest-object#jestmockmodulename-factory-options
// in order to mock modules in test case, so avoid absolute import module
import { RamaClient } from '../../packages/rama-ui-core/src/connection';

export default function setupRamaClient() {
  // The following is needed to mock out RamaClient requests
  // including CSRF authentication and initialization
  global.FormData = window.FormData; // used by RamaClient
  fetchMock.get('glob:*/api/v1/security/csrf_token/*', { result: '1234' });
  RamaClient.configure({ protocol: 'http', host: 'localhost' }).init();
}
