import { expect, test } from '@playwright/test';

const realApiEnabled = process.env.HYDROSIM_E2E_REAL_API === '1';

test('PED-D2 runs end to end against the real Python pedagogical API', async ({ page }) => {
  test.skip(!realApiEnabled, 'Run only in the targeted React + Python end-to-end gate.');

  const signalResponses: number[] = [];
  page.on('response', (response) => {
    if (response.url().includes('/api/v1/pedagogical/signal')) {
      signalResponses.push(response.status());
    }
  });

  await page.goto('/#signal-lab');

  await expect(page.getByRole('heading', {
    name: 'Change the transmitted pulse and watch the same scientific state reshape every visual.',
  })).toBeVisible();

  await expect.poll(() => signalResponses.length).toBeGreaterThan(0);
  expect(signalResponses.at(-1)).toBe(200);

  await expect(page.getByText('Acoustic passband waveform', { exact: true })).toBeVisible();
  await expect(page.getByText('Instantaneous frequency', { exact: true })).toBeVisible();
  await expect(page.getByText('Matched-filter / autocorrelation response', { exact: true })).toBeVisible();
  await expect(page.getByText('Configured', { exact: true })).toBeVisible();
  await expect(page.getByText('Derived', { exact: true })).toBeVisible();
  await expect(page.getByText('0–5 ms', { exact: true })).toBeVisible();

  const duration = page.locator('label').filter({ hasText: 'Pulse duration' }).locator('input[type="range"]');
  await duration.focus();
  await duration.press('ArrowRight');
  await expect.poll(() => signalResponses.length).toBeGreaterThan(1);
  expect(signalResponses.at(-1)).toBe(200);

  await page.getByRole('button', { name: 'PT-BR' }).click();
  await expect(page.getByRole('heading', {
    name: 'Altere o pulso transmitido e veja o mesmo estado científico transformar todas as visualizações.',
  })).toBeVisible();
});
