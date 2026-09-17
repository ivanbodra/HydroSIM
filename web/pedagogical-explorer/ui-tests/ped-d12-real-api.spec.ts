import { expect, test } from '@playwright/test';

const realApiEnabled = process.env.HYDROSIM_E2E_REAL_API === '1';
const endpoint = '/api/v1/pedagogical/pu-sensor';

test('D12 carries learner PU-sensor changes through the real Python API', async ({ page }) => {
  test.skip(!realApiEnabled, 'Run only in the targeted React + Python end-to-end gate.');
  await page.addInitScript(() => sessionStorage.setItem('hydrosim-language', 'en'));

  const requests: any[] = [];
  page.on('request', request => {
    if (request.url().endsWith(endpoint) && request.method() === 'POST') requests.push(request.postDataJSON());
  });

  const initialResponsePromise = page.waitForResponse(response => response.url().endsWith(endpoint) && response.request().method() === 'POST');
  await page.goto('/#pu-sensor-lab');
  const initialResponse = await initialResponsePromise;
  expect(initialResponse.status()).toBe(200);
  const initialBody = await initialResponse.json();
  expect(initialBody.status).toBe('compatible');
  await expect(page.getByRole('img', { name: /Configuration compatible/ })).toBeVisible();
  await expect(page.getByLabel('PU input: PASS').getByText('PU-A', { exact: true })).toBeVisible();

  const sensor = page.getByRole('combobox', { name: 'Sensor' });
  const changedResponsePromise = page.waitForResponse(response => response.url().endsWith(endpoint) && response.request().method() === 'POST');
  await sensor.selectOption('sound_speed_sensor');
  const changedResponse = await changedResponsePromise;
  expect(changedResponse.status()).toBe(200);
  const changedBody = await changedResponse.json();

  await expect.poll(() => requests.at(-1)?.stream?.device_class).toBe('sound_speed_sensor');
  expect(changedBody.status).toBe('incompatible');
  expect(changedBody.reason_codes).toContain('device_class_mismatch');
  await expect(page.getByRole('img', { name: /Needs correction/ })).toBeVisible();
  await expect(page.getByLabel('Sensor role: REJECTED HERE')).toBeVisible();
  await expect(page.getByText('Sensor type is not accepted by this PU input.')).toBeVisible();
  await expect(page.getByText(/Configuration unavailable/)).toHaveCount(0);
});
