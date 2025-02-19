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

import { RamaClient, RamaClientClass } from '@rama-ui/core';
import { LOGIN_GLOB } from './fixtures/constants';

describe('RamaClient', () => {
  beforeAll(() => fetchMock.get(LOGIN_GLOB, { result: '' }));

  afterAll(() => fetchMock.restore());

  afterEach(() => RamaClient.reset());

  it('exposes reset, configure, init, get, post, postForm, isAuthenticated, and reAuthenticate methods', () => {
    expect(typeof RamaClient.configure).toBe('function');
    expect(typeof RamaClient.init).toBe('function');
    expect(typeof RamaClient.get).toBe('function');
    expect(typeof RamaClient.post).toBe('function');
    expect(typeof RamaClient.postForm).toBe('function');
    expect(typeof RamaClient.isAuthenticated).toBe('function');
    expect(typeof RamaClient.reAuthenticate).toBe('function');
    expect(typeof RamaClient.getGuestToken).toBe('function');
    expect(typeof RamaClient.request).toBe('function');
    expect(typeof RamaClient.reset).toBe('function');
  });

  it('throws if you call init, get, post, postForm, isAuthenticated, or reAuthenticate before configure', () => {
    expect(RamaClient.init).toThrow();
    expect(RamaClient.get).toThrow();
    expect(RamaClient.post).toThrow();
    expect(RamaClient.postForm).toThrow();
    expect(RamaClient.isAuthenticated).toThrow();
    expect(RamaClient.reAuthenticate).toThrow();
    expect(RamaClient.request).toThrow();
    expect(RamaClient.configure).not.toThrow();
  });

  // this also tests that the ^above doesn't throw if configure is called appropriately
  it('calls appropriate RamaClient methods when configured', async () => {
    expect.assertions(16);
    const mockGetUrl = '/mock/get/url';
    const mockPostUrl = '/mock/post/url';
    const mockRequestUrl = '/mock/request/url';
    const mockPutUrl = '/mock/put/url';
    const mockDeleteUrl = '/mock/delete/url';
    const mockGetPayload = { get: 'payload' };
    const mockPostPayload = { post: 'payload' };
    const mockDeletePayload = { delete: 'ok' };
    const mockPutPayload = { put: 'ok' };
    fetchMock.get(mockGetUrl, mockGetPayload);
    fetchMock.post(mockPostUrl, mockPostPayload);
    fetchMock.delete(mockDeleteUrl, mockDeletePayload);
    fetchMock.put(mockPutUrl, mockPutPayload);
    fetchMock.get(mockRequestUrl, mockGetPayload);

    const initSpy = jest.spyOn(RamaClientClass.prototype, 'init');
    const getSpy = jest.spyOn(RamaClientClass.prototype, 'get');
    const postSpy = jest.spyOn(RamaClientClass.prototype, 'post');
    const putSpy = jest.spyOn(RamaClientClass.prototype, 'put');
    const deleteSpy = jest.spyOn(RamaClientClass.prototype, 'delete');
    const authenticatedSpy = jest.spyOn(
      RamaClientClass.prototype,
      'isAuthenticated',
    );
    const csrfSpy = jest.spyOn(RamaClientClass.prototype, 'getCSRFToken');
    const requestSpy = jest.spyOn(RamaClientClass.prototype, 'request');
    const getGuestTokenSpy = jest.spyOn(
      RamaClientClass.prototype,
      'getGuestToken',
    );

    RamaClient.configure({});
    await RamaClient.init();

    expect(initSpy).toHaveBeenCalledTimes(1);
    expect(authenticatedSpy).toHaveBeenCalledTimes(2);
    expect(csrfSpy).toHaveBeenCalledTimes(1);

    await RamaClient.get({ url: mockGetUrl });
    await RamaClient.post({ url: mockPostUrl });
    await RamaClient.delete({ url: mockDeleteUrl });
    await RamaClient.put({ url: mockPutUrl });
    await RamaClient.request({ url: mockRequestUrl });

    // Make sure network calls have  Accept: 'application/json' in headers
    const networkCalls = [
      mockGetUrl,
      mockPostUrl,
      mockRequestUrl,
      mockPutUrl,
      mockDeleteUrl,
    ];
    networkCalls.map((url: string) =>
      expect(fetchMock.calls(url)[0][1]?.headers).toStrictEqual({
        Accept: 'application/json',
        'X-CSRFToken': '',
      }),
    );

    RamaClient.isAuthenticated();
    await RamaClient.reAuthenticate();

    RamaClient.getGuestToken();
    expect(getGuestTokenSpy).toHaveBeenCalledTimes(1);

    expect(initSpy).toHaveBeenCalledTimes(2);
    expect(deleteSpy).toHaveBeenCalledTimes(1);
    expect(putSpy).toHaveBeenCalledTimes(1);
    expect(getSpy).toHaveBeenCalledTimes(1);
    expect(postSpy).toHaveBeenCalledTimes(1);
    expect(requestSpy).toHaveBeenCalledTimes(5); // request rewires to get
    expect(csrfSpy).toHaveBeenCalledTimes(2); // from init() + reAuthenticate()

    initSpy.mockRestore();
    getSpy.mockRestore();
    putSpy.mockRestore();
    deleteSpy.mockRestore();
    requestSpy.mockRestore();
    postSpy.mockRestore();
    authenticatedSpy.mockRestore();
    csrfSpy.mockRestore();

    fetchMock.reset();
  });
});
