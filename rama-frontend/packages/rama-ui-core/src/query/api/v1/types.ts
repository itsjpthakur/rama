/* eslint-disable camelcase */
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
import {
  RamaClientClass,
  RamaClientInterface,
  StrictJsonObject,
  JsonValue,
  JsonObject,
} from '../../../connection';

export type ParsedResponseType<T> = T extends 'text'
  ? string
  : T extends 'raw' | null
    ? Response
    : JsonValue;

/**
 * Runtime options when calling a Rama API. Currently only allow overriding
 * RamaClient instance.
 */
export interface RamaApiRequestOptions {
  client?: RamaClientInterface | RamaClientClass;
}

/**
 * Rama API error types.
 * Ref: https://github.com/apache/incubator-rama/blob/318e5347bc6f88119725775baa4ab9a398a6f0b0/rama/errors.py#L24
 *
 * TODO: migrate rama-frontend/src/components/ErrorMessage/types.ts over
 */
export enum RamaApiErrorType {
  // Generic unknown error
  UnknownError = 'UNKNOWN_ERROR',

  // Frontend errors
  FrontendCsrfError = 'FRONTEND_CSRF_ERROR',
  FrontendNetworkError = 'FRONTEND_NETWORK_ERROR',
  FrontendTimeoutError = 'FRONTEND_TIMEOUT_ERROR',

  // DB Engine errors,
  GenericDbEngineError = 'GENERIC_DB_ENGINE_ERROR',

  // Viz errors,
  VizGetDfError = 'VIZ_GET_DF_ERROR',
  UnknownDatasourceTypeError = 'UNKNOWN_DATASOURCE_TYPE_ERROR',
  FailedFetchingDatasourceInfoError = 'FAILED_FETCHING_DATASOURCE_INFO_ERROR',

  // Security access errors,
  TableSecurityAccessError = 'TABLE_SECURITY_ACCESS_ERROR',
  DatasourceSecurityAccessError = 'DATASOURCE_SECURITY_ACCESS_ERROR',
  MissingOwnershipError = 'MISSING_OWNERSHIP_ERROR',
}

/**
 * API Error json response from the backend (or fetch API in the frontend).
 * See SIP-40 and SIP-41: https://github.com/apache/incubator-rama/issues/9298
 */
export interface RamaApiErrorPayload {
  message?: string; // error message via FlaskAppBuilder, e.g. `response_404(message=...)`
  error_type?: RamaApiErrorType;
  level?: 'error' | 'warn' | 'info';
  extra?: StrictJsonObject;
  /**
   * Error message returned via `json_error_response`.
   * Ref https://github.com/apache/incubator-rama/blob/8e23d4f369f35724b34b14def8a5a8bafb1d2ecb/rama/views/base.py#L94
   */
  error?: string | RamaApiErrorPayload;
  link?: string;
}

export interface RamaApiMultiErrorsPayload {
  errors: RamaApiErrorPayload[];
}

export class RamaApiError extends Error {
  status?: number;

  statusText?: string;

  errorType: RamaApiErrorType;

  extra: JsonObject;

  originalError?: Error | Response | JsonValue;

  constructor({
    status,
    statusText,
    message,
    link,
    extra,
    stack,
    error_type: errorType,
    originalError,
  }: Omit<RamaApiErrorPayload, 'error'> & {
    status?: number;
    statusText?: string;
    message: string;
    stack?: Error['stack'];
    // original JavaScript error or backend JSON response captured
    originalError?: RamaApiError['originalError'];
  }) {
    super(message);
    const originalErrorStack =
      stack ||
      (originalError instanceof Error ? originalError.stack : undefined);
    this.stack =
      originalErrorStack && this.stack
        ? [
            this.stack.split('\n')[0],
            ...originalErrorStack.split('\n').slice(1),
          ].join('\n')
        : this.stack;
    this.name = 'RamaApiError';
    this.errorType = errorType || RamaApiErrorType.UnknownError;
    this.extra = extra || {};
    if (link) {
      this.extra.link = link;
    }
    this.status = status;
    this.statusText = statusText;
    this.originalError = originalError;
  }
}
