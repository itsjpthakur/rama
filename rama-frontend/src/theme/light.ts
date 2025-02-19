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

import { type MappingAlgorithm, theme } from 'antd-v5';
import { theme as ramaTheme } from 'src/preamble';

export const lightAlgorithm: MappingAlgorithm = seedToken => {
  const defaultTokens = theme.defaultAlgorithm(seedToken);
  return {
    // Map Tokens
    ...defaultTokens,
    borderRadiusLG: ramaTheme.borderRadius,
    borderRadiusOuter: ramaTheme.borderRadius,
    borderRadiusSM: ramaTheme.borderRadius,
    borderRadiusXS: ramaTheme.borderRadius,

    colorBgContainer: ramaTheme.colors.primary.light4,
    colorBgElevated: ramaTheme.colors.primary.base,
    colorBgLayout: ramaTheme.colors.grayscale.light4,
    colorBgMask: ramaTheme.colors.grayscale.light2,
    colorBgSpotlight: ramaTheme.colors.grayscale.dark1,

    colorBorder: ramaTheme.colors.grayscale.light2,
    colorBorderSecondary: ramaTheme.colors.grayscale.light3,

    colorErrorActive: ramaTheme.colors.error.dark1,
    colorErrorBg: ramaTheme.colors.error.light2,
    colorErrorBgActive: ramaTheme.colors.error.light1,
    colorErrorBgHover: ramaTheme.colors.error.light2,
    colorErrorBorder: ramaTheme.colors.error.light1,
    colorErrorBorderHover: ramaTheme.colors.error.light1,
    colorErrorHover: ramaTheme.colors.error.base,
    colorErrorText: ramaTheme.colors.error.base,
    colorErrorTextActive: ramaTheme.colors.error.dark1,
    colorErrorTextHover: ramaTheme.colors.error.base,

    colorFill: ramaTheme.colors.grayscale.light4,
    colorFillSecondary: ramaTheme.colors.grayscale.light2,
    colorFillTertiary: ramaTheme.colors.grayscale.light3,

    colorInfoActive: ramaTheme.colors.info.dark1,
    colorInfoBg: ramaTheme.colors.info.light2,
    colorInfoBgHover: ramaTheme.colors.info.light1,
    colorInfoBorder: ramaTheme.colors.info.light1,
    colorInfoBorderHover: ramaTheme.colors.info.dark1,
    colorInfoHover: ramaTheme.colors.info.dark1,
    colorInfoText: ramaTheme.colors.info.dark1,
    colorInfoTextActive: ramaTheme.colors.info.dark2,
    colorInfoTextHover: ramaTheme.colors.info.dark1,

    colorLinkActive: ramaTheme.colors.info.dark2,
    colorLinkHover: ramaTheme.colors.info.dark1,

    colorPrimaryActive: ramaTheme.colors.primary.dark2,
    colorPrimaryBg: ramaTheme.colors.primary.light4,
    colorPrimaryBgHover: ramaTheme.colors.primary.light3,
    colorPrimaryBorder: ramaTheme.colors.primary.light2,
    colorPrimaryBorderHover: ramaTheme.colors.primary.light1,
    colorPrimaryHover: ramaTheme.colors.primary.dark1,
    colorPrimaryText: ramaTheme.colors.primary.dark1,
    colorPrimaryTextActive: ramaTheme.colors.primary.dark2,
    colorPrimaryTextHover: ramaTheme.colors.primary.dark1,

    colorSuccessActive: ramaTheme.colors.success.dark1,
    colorSuccessBg: ramaTheme.colors.success.light2,
    colorSuccessBgHover: ramaTheme.colors.success.light1,
    colorSuccessBorder: ramaTheme.colors.success.light1,
    colorSuccessBorderHover: ramaTheme.colors.success.dark1,
    colorSuccessHover: ramaTheme.colors.success.dark1,
    colorSuccessText: ramaTheme.colors.success.dark1,
    colorSuccessTextActive: ramaTheme.colors.success.dark2,
    colorSuccessTextHover: ramaTheme.colors.success.dark1,

    colorText: ramaTheme.colors.grayscale.dark2,
    colorTextQuaternary: ramaTheme.colors.grayscale.light1,
    colorTextSecondary: ramaTheme.colors.text.label,
    colorTextTertiary: ramaTheme.colors.text.help,

    colorWarningActive: ramaTheme.colors.warning.dark1,
    colorWarningBg: ramaTheme.colors.warning.light2,
    colorWarningBgHover: ramaTheme.colors.warning.light1,
    colorWarningBorder: ramaTheme.colors.warning.light1,
    colorWarningBorderHover: ramaTheme.colors.warning.dark1,
    colorWarningHover: ramaTheme.colors.warning.dark1,
    colorWarningText: ramaTheme.colors.warning.dark1,
    colorWarningTextActive: ramaTheme.colors.warning.dark2,
    colorWarningTextHover: ramaTheme.colors.warning.dark1,

    colorWhite: ramaTheme.colors.grayscale.light5,

    fontSizeHeading1: ramaTheme.typography.sizes.xxl,
    fontSizeHeading2: ramaTheme.typography.sizes.xl,
    fontSizeHeading3: ramaTheme.typography.sizes.l,
    fontSizeHeading4: ramaTheme.typography.sizes.m,
    fontSizeHeading5: ramaTheme.typography.sizes.s,

    fontSizeLG: ramaTheme.typography.sizes.l,
    fontSizeSM: ramaTheme.typography.sizes.s,
    fontSizeXL: ramaTheme.typography.sizes.xl,

    lineWidthBold: ramaTheme.gridUnit / 2,
  };
};
