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

import { makeApi } from '@rama-ui/core';
import { useEffect, useMemo, useRef, useState } from 'react';

export enum ResourceStatus {
  Loading = 'loading',
  Complete = 'complete',
  Error = 'error',
}

/**
 * An object containing the data fetched from the API,
 * as well as loading and error info
 */
export type Resource<T> = LoadingState | CompleteState<T> | ErrorState;

// Trying out something a little different: a separate type per status.
// This should let TypeScript know whether a Resource has a result or error.
// It's possible that I'm expecting too much from TypeScript here.
// If this ends up causing problems, we can change the type to:
//
// export type Resource<T> = {
//   status: ResourceStatus;
//   result: null | T;
//   error: null | Error;
// }

type LoadingState = {
  status: ResourceStatus.Loading;
  result: null;
  error: null;
};

type CompleteState<T> = {
  status: ResourceStatus.Complete;
  result: T;
  error: null;
};

type ErrorState = {
  status: ResourceStatus.Error;
  result: null;
  error: Error;
};

const initialState: LoadingState = {
  status: ResourceStatus.Loading,
  result: null,
  error: null,
};

/**
 * A general-purpose hook to fetch the response from an endpoint.
 * Returns the full response body from the API, including metadata.
 *
 * Note: You likely want {useApiV1Resource} instead of this!
 *
 * TODO Store the state in redux or something, share state between hook instances.
 *
 * TODO Include a function in the returned resource object to refresh the data.
 *
 * A core design decision here is composition > configuration,
 * and every hook should only have one job.
 * Please address new needs with new hooks if possible,
 * rather than adding config options to this hook.
 *
 * @param endpoint The url where the resource is located.
 */
export function useApiResourceFullBody<RESULT>(
  endpoint: string,
): Resource<RESULT> {
  const [resource, setResource] = useState<Resource<RESULT>>(initialState);
  const cancelRef = useRef<() => void>(() => {});

  useEffect(() => {
    // If refresh is implemented, this will need to change.
    // The previous values should stay during refresh.
    setResource(initialState);

    // when this effect runs, the endpoint has changed.
    // cancel any current calls so that state doesn't get messed up.
    cancelRef.current();
    let cancelled = false;
    cancelRef.current = () => {
      cancelled = true;
    };

    const fetchResource = makeApi<{}, RESULT>({
      method: 'GET',
      endpoint,
    });

    fetchResource({})
      .then(result => {
        if (!cancelled) {
          setResource({
            status: ResourceStatus.Complete,
            result,
            error: null,
          });
        }
      })
      .catch(error => {
        if (!cancelled) {
          setResource({
            status: ResourceStatus.Error,
            result: null,
            error,
          });
        }
      });

    // Cancel the request when the component un-mounts
    return () => {
      cancelled = true;
    };
  }, [endpoint]);

  return resource;
}

/**
 * For when you want to transform the result of an api resource hook before using it.
 *
 * @param resource the Resource object returned from useApiV1Resource
 * @param transformFn a callback that transforms the result object into the shape you want.
 * Make sure to use a persistent function for this so it doesn't constantly recalculate!
 */
export function useTransformedResource<IN, OUT>(
  resource: Resource<IN>,
  transformFn: (result: IN) => OUT,
): Resource<OUT> {
  return useMemo(() => {
    if (resource.status !== ResourceStatus.Complete) {
      // While incomplete, there is no result - no need to transform.
      return resource;
    }
    try {
      return {
        ...resource,
        result: transformFn(resource.result),
      };
    } catch (e) {
      return {
        status: ResourceStatus.Error,
        result: null,
        error: e,
      };
    }
  }, [resource, transformFn]);
}

// returns the "result" field from a fetched API v1 endpoint
const extractInnerResult = <T>(responseBody: { result: T }) =>
  responseBody.result;

/**
 * A general-purpose hook to fetch a Rama resource from a v1 API endpoint.
 * Handles request lifecycle and async logic so you don't have to.
 *
 * This returns the data under the "result" field in the API response body.
 * If you need the full response body, use {useFullApiResource} instead.
 *
 * @param endpoint The url where the resource is located.
 */
export function useApiV1Resource<RESULT>(endpoint: string): Resource<RESULT> {
  return useTransformedResource(
    useApiResourceFullBody<{ result: RESULT }>(endpoint),
    extractInnerResult,
  );
}
