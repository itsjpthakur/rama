// themeDecorator.js
import { ramaTheme, ThemeProvider } from '@rama-ui/core';

const ThemeDecorator = Story => (
  <ThemeProvider theme={ramaTheme}>{<Story />}</ThemeProvider>
);

export default ThemeDecorator;
