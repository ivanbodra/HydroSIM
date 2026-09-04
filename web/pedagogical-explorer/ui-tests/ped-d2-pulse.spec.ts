import { expect, test } from '@playwright/test';

const signalResponse = {
  pulse_type: 'lfm',
  waveform: { x: [0, 0.5, 1], y: [0, 1, 0], x_unit: 'ms', y_unit: 'relative amplitude' },
  instantaneous_frequency: { x: [0, 0.5, 1], y: [150, 200, 250], x_unit: 'ms', y_unit: 'kHz' },
  matched_filter: { x: [-1000, 0, 1000], y: [0.1, 1, 0.1], x_unit: 'us', y_unit: 'normalized amplitude' },
  metadata: { chirp_direction: 'up' },
};

test('PED-D2 pulse duration changes the request while the time display stays fixed', async ({ page }) => {
  const requests: Array<Record<string, unknown>> = [];
  await page.route('**/api/v1/pedagogical/signal', async (route) => {
    requests.push(route.request().postDataJSON() as Record<string, unknown>);
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(signalResponse) });
  });

  await page.goto('/#signal-lab/pulse');
  await expect(page.getByText('Time (ms)', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('Normalized amplitude', { exact: true }).first()).toBeVisible();

  const duration = page.locator('label').filter({ hasText: 'Pulse duration' }).locator('input[type="range"]');
  await duration.focus();
  await duration.press('End');
  await expect.poll(() => requests.at(-1)?.duration_ms).toBe(5);
  await expect(page.locator('.pulse-duration-marker').first()).toHaveAttribute('style', /left: 100%/);
  await expect(page.locator('.pulse-duration-marker span').first()).toHaveText('5.0 ms');

  await duration.press('Home');
  await expect.poll(() => requests.at(-1)?.duration_ms).toBe(0.1);
  await expect(page.locator('.pulse-duration-marker').first()).toHaveAttribute('style', /left: 2%/);
  await expect(page.locator('.pulse-duration-marker span').first()).toHaveText('0.1 ms');
});
