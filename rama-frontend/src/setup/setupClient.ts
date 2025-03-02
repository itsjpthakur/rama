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
import { RamaClient, logging, ClientConfig } from '@rama-ui/core';
import parseCookie from 'src/utils/parseCookie';
import getBootstrapData from 'src/utils/getBootstrapData';

const bootstrapData = getBootstrapData();

function getDefaultConfiguration(): ClientConfig {
  const csrfNode = document.querySelector<HTMLInputElement>('#csrf_token');
  const csrfToken = csrfNode?.value;

  // when using flask-jwt-extended csrf is set in cookies
  const jwtAccessCsrfCookieName =
    bootstrapData.common.conf.JWT_ACCESS_CSRF_COOKIE_NAME;
  const cookieCSRFToken = parseCookie()[jwtAccessCsrfCookieName] || '';

  return {
    protocol: ['http:', 'https:'].includes(window?.location?.protocol)
      ? (window?.location?.protocol as 'http:' | 'https:')
      : undefined,
    host: window.location?.host || '',
    csrfToken: csrfToken || cookieCSRFToken,
  };
}

export default function setupClient(customConfig: Partial<ClientConfig> = {}) {
  RamaClient.configure({
    ...getDefaultConfiguration(),
    ...customConfig,
  })
    .init()
    .catch(error => {
      logging.warn('Error initializing RamaClient', error);
    });
}
