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

import { addAlpha } from '@rama-ui/core';
import { type ThemeConfig } from 'antd-v5';
import { theme as ramaTheme } from 'src/preamble';
import { mix } from 'polished';
import { lightAlgorithm } from './light';

export enum ThemeType {
  LIGHT = 'light',
}

const themes = {
  [ThemeType.LIGHT]: lightAlgorithm,
};

// Want to figure out which tokens look like what? Try this!
// https://ant.design/theme-editor

const baseConfig: ThemeConfig = {
  token: {
    borderRadius: ramaTheme.borderRadius,
    colorBgBase: ramaTheme.colors.primary.light4,
    colorError: ramaTheme.colors.error.base,
    colorInfo: ramaTheme.colors.info.base,
    colorLink: ramaTheme.colors.grayscale.dark1,
    colorPrimary: ramaTheme.colors.primary.base,
    colorSuccess: ramaTheme.colors.success.base,
    colorTextBase: ramaTheme.colors.grayscale.dark2,
    colorWarning: ramaTheme.colors.warning.base,
    controlHeight: 32,
    fontFamily: ramaTheme.typography.families.sansSerif,
    fontFamilyCode: ramaTheme.typography.families.monospace,
    fontSize: ramaTheme.typography.sizes.m,
    lineType: 'solid',
    lineWidth: 1,
    sizeStep: ramaTheme.gridUnit,
    sizeUnit: ramaTheme.gridUnit,
    zIndexBase: 0,
    zIndexPopupBase: ramaTheme.zIndex.max,
  },
  components: {
    Avatar: {
      containerSize: 32,
      fontSize: ramaTheme.typography.sizes.s,
      lineHeight: 32,
    },
    Badge: {
      paddingXS: ramaTheme.gridUnit * 2,
    },
    Button: {
      defaultBg: ramaTheme.colors.primary.light4,
      defaultHoverBg: mix(
        0.1,
        ramaTheme.colors.primary.base,
        ramaTheme.colors.primary.light4,
      ),
      defaultActiveBg: mix(
        0.25,
        ramaTheme.colors.primary.base,
        ramaTheme.colors.primary.light4,
      ),
      defaultColor: ramaTheme.colors.primary.dark1,
      defaultHoverColor: ramaTheme.colors.primary.dark1,
      defaultBorderColor: 'transparent',
      defaultHoverBorderColor: 'transparent',
      colorPrimaryHover: ramaTheme.colors.primary.dark1,
      colorPrimaryActive: mix(
        0.2,
        ramaTheme.colors.grayscale.dark2,
        ramaTheme.colors.primary.dark1,
      ),
      primaryColor: ramaTheme.colors.grayscale.light5,
      colorPrimaryTextHover: ramaTheme.colors.grayscale.light5,
      colorError: ramaTheme.colors.error.base,
      colorErrorHover: mix(
        0.1,
        ramaTheme.colors.grayscale.light5,
        ramaTheme.colors.error.base,
      ),
      colorErrorBg: mix(
        0.2,
        ramaTheme.colors.grayscale.dark2,
        ramaTheme.colors.error.base,
      ),
      dangerColor: ramaTheme.colors.grayscale.light5,
      colorLinkHover: ramaTheme.colors.primary.base,
      linkHoverBg: 'transparent',
    },
    Card: {
      paddingLG: ramaTheme.gridUnit * 6,
      fontWeightStrong: ramaTheme.typography.weights.medium,
      colorBgContainer: ramaTheme.colors.grayscale.light4,
    },
    DatePicker: {
      colorBgContainer: ramaTheme.colors.grayscale.light5,
      colorBgElevated: ramaTheme.colors.grayscale.light5,
      borderRadiusSM: ramaTheme.gridUnit / 2,
    },
    Divider: {
      colorSplit: ramaTheme.colors.grayscale.light3,
    },
    Dropdown: {
      colorBgElevated: ramaTheme.colors.grayscale.light5,
      zIndexPopup: ramaTheme.zIndex.max,
    },
    Input: {
      colorBorder: ramaTheme.colors.secondary.light3,
      colorBgContainer: ramaTheme.colors.grayscale.light5,
      activeShadow: `0 0 0 ${ramaTheme.gridUnit / 2}px ${
        ramaTheme.colors.primary.light3
      }`,
    },
    InputNumber: {
      colorBorder: ramaTheme.colors.secondary.light3,
      colorBgContainer: ramaTheme.colors.grayscale.light5,
      activeShadow: `0 0 0 ${ramaTheme.gridUnit / 2}px ${
        ramaTheme.colors.primary.light3
      }`,
    },
    List: {
      itemPadding: `${ramaTheme.gridUnit + 2}px ${ramaTheme.gridUnit * 3}px`,
      paddingLG: ramaTheme.gridUnit * 3,
      colorSplit: ramaTheme.colors.grayscale.light3,
      colorText: ramaTheme.colors.grayscale.dark1,
    },
    Menu: {
      itemHeight: 32,
      colorBgContainer: ramaTheme.colors.grayscale.light5,
      subMenuItemBg: ramaTheme.colors.grayscale.light5,
      colorBgElevated: ramaTheme.colors.grayscale.light5,
      boxShadowSecondary: `0 3px 6px -4px ${addAlpha(ramaTheme.colors.grayscale.dark2, 0.12)}, 0 6px 16px 0 ${addAlpha(ramaTheme.colors.grayscale.dark2, 0.08)}, 0 9px 28px 8px ${addAlpha(ramaTheme.colors.grayscale.dark2, 0.05)}`,
      activeBarHeight: 0,
      itemHoverBg: ramaTheme.colors.secondary.light5,
      padding: ramaTheme.gridUnit * 2,
      subMenuItemBorderRadius: 0,
      horizontalLineHeight: 1.4,
      zIndexPopup: ramaTheme.zIndex.max,
    },
    Modal: {
      colorBgMask: `${ramaTheme.colors.grayscale.dark2}73`,
      contentBg: ramaTheme.colors.grayscale.light5,
      titleFontSize: ramaTheme.gridUnit * 4,
      titleColor: `${ramaTheme.colors.grayscale.dark2}D9`,
      headerBg: ramaTheme.colors.grayscale.light4,
    },
    Tag: {
      borderRadiusSM: 2,
      defaultBg: ramaTheme.colors.grayscale.light4,
    },
    Progress: {
      fontSize: ramaTheme.typography.sizes.s,
      colorText: ramaTheme.colors.text.label,
      remainingColor: ramaTheme.colors.grayscale.light4,
    },
    Popover: {
      colorBgElevated: ramaTheme.colors.grayscale.light5,
    },
    Slider: {
      trackBgDisabled: ramaTheme.colors.grayscale.light1,
      colorBgElevated: ramaTheme.colors.grayscale.light5,
      handleSizeHover: 10,
      handleLineWidthHover: 2,
    },
    Steps: {
      margin: ramaTheme.gridUnit * 2,
      iconSizeSM: 20,
    },
    Switch: {
      colorPrimaryHover: ramaTheme.colors.primary.base,
      colorTextTertiary: ramaTheme.colors.grayscale.light1,
    },
    Tooltip: {
      fontSize: ramaTheme.typography.sizes.s,
      lineHeight: 1.6,
    },
  },
};

export const getTheme = (themeType?: ThemeType) => ({
  ...baseConfig,
  algorithm: themes[themeType || ThemeType.LIGHT],
});
