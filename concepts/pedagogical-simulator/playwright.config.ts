import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './ui-tests',
  timeout: 20_000,
  expect: { timeout: 5_000 },
  use: {
    baseURL: 'http://127.0.0.1:4173',
    browserName: 'chromium',
    headless: true,
  },
});
