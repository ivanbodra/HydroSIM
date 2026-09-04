import { expect, test } from '@playwright/test';

const realApiEnabled = process.env.HYDROSIM_E2E_REAL_API === '1';

test('PED-D2 runs end to end against the real Python pedagogical API', async ({ page }) => {
  test.skip(!realApiEnabled, 'Run only in the targeted React + Python end-to-end gate.');

  const signalResponses: number[] = [];
  page.on('response', (response) => {
    if (response.url().includes('/api/v1/pedagogical/signal')) signalResponses.push(response.status());
  });

  await page.goto('/#signal-lab');
  await expect(page.getByRole('heading', { name: 'Change the transmitted pulse and observe the signal response.' })).toBeVisible();
  await expect.poll(() => signalResponses.length).toBeGreaterThan(0);
  expect(signalResponses.at(-1)).toBe(200);

  const cards = page.locator('.chain-card');
  await expect(cards.getByText('Acoustic waveform', { exact: true })).toBeVisible();
  await expect(cards.getByText('Instantaneous frequency', { exact: true })).toBeVisible();
  await expect(cards.getByText('Matched-filter response', { exact: true })).toBeVisible();
  await expect(cards.getByText('Time (ms)', { exact: true }).first()).toBeVisible();
  await expect(cards.getByText('Lag (µs)', { exact: true })).toBeVisible();

  const duration = page.locator('label').filter({ hasText: 'Pulse duration' }).locator('input[type="range"]');
  await duration.focus();
  await duration.press('End');
  await expect.poll(() => signalResponses.length).toBeGreaterThan(1);
  expect(signalResponses.at(-1)).toBe(200);
  await expect(page.locator('.pulse-duration-marker').first()).toHaveAttribute('style', /left: 100%/);

  await page.getByRole('button', { name: 'PT-BR' }).click();
  await expect(page.getByRole('heading', { name: 'Altere o pulso transmitido e observe a resposta do sinal.' })).toBeVisible();
});
