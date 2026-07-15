import { defineConfig } from '@playwright/test';
import baseConfig from '../../playwright.config.js';

export default defineConfig({
  ...baseConfig,
  testDir: '../../tests',
  projects: [
    {
      name: 'msedge',
      use: {
        channel: 'msedge',
      },
    },
  ],
});
