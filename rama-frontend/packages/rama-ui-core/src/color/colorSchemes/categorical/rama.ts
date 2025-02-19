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

import CategoricalScheme from '../../CategoricalScheme';
import { ColorSchemeGroup } from '../../types';

// TODO: add the colors to the theme while working on SIP https://github.com/itsjpthakur/rama/issues/20159
const schemes = [
  {
    id: 'ramaColors',
    label: 'Rama Colors',
    group: ColorSchemeGroup.Featured,
    colors: [
      '#D7282D',  // Base Primary Color
      '#B02125',  // Darker Primary 1
      '#8A1A1E',  // Darker Primary 2
      '#E15358',  // Slightly Lighter
      '#EA8588',  // Light Primary 1
      '#F3B7B8',  // Light Primary 2
      '#F9D8D9',  // Soft Pastel
      '#FDEDED',  // Very Light Primary
      '#921E1E',  // Deep Red
      '#A12A2A',  // Mid-tone Red
      '#C03C3C',  // Warm Red
      '#E14D4D',  // Vibrant Red
      '#F25E5E',  // Soft Vibrant
    ],
  },
].map(s => new CategoricalScheme(s));

export default schemes;
