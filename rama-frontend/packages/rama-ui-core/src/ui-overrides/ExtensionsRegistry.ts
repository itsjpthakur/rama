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
import { TypedRegistry } from '../models';
import { makeSingleton } from '../utils';
import { Extensions } from './types';

/**
 * A registry containing extensions which can alter Rama's UI at specific points defined by Rama.
 * See SIP-87: https://github.com/itsjpthakur/rama/issues/20615
 */
class ExtensionsRegistry extends TypedRegistry<Extensions> {
  name = 'ExtensionsRegistry';
}

export const getExtensionsRegistry = makeSingleton(ExtensionsRegistry, {});
