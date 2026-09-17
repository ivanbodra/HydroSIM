import { expect, test } from '@playwright/test';

const endpoint = '/api/v1/pedagogical/pu-sensor';

test('D12 carries learner PU-sensor changes through the real Python API', async ({ page }) => {
  const requests: any[] = [];
  const responses: any[] = [];

  page.on('request', request => {
    if (request.url().includes(endpoint) && request.method() === 'POST') {
      requests.push(request.postDataJSON());
    }
  });
  page.on('response', async response => {
    if (response.url().includes(endpoint)) {
      responses.push({ status: response.status(), body: await response.json() });
    }
  });

  await page.goto('/#pu-sensor-lab');
  await expect.poll(() => responses.length).toBeGreaterThan(0);
  expect(responses.at(-1)?.status).toBe(200);
  expect(responses.at(-1)?.body.status).toBe('compatible');
  await expect(page.getByRole('img', { name: /Configuration compatible/ })).toBeVisible();
  await expect(page.getByLabel('PU input: PASS').getByText('PU-A', { exact: true })).toBeVisible();

  const sensor = page.getByLabel('Sensor', { exact: true });
  await sensor.selectOption('attitude_sensor');

  await expect.poll(() => requests.at(-1)?.stream?.device_class).toBe('attitude_sensor');
  await expect.poll(() => responses.at(-1)?.body.status).toBe('incompatible');
  expect(responses.at(-1)?.status).toBe(200);
  expect(responses.at(-1)?.body.reason_codes).toContain('device_class_mismatch');
  await expect(page.getByRole('img', { name: /Needs correction/ })).toBeVisible();
  await expect(page.getByLabel('Sensor role: REJECTED HERE')).toBeVisible();
  await expect(page.getByText('Sensor type is not accepted by this PU input.')).toBeVisible();
  await expect(page.getByText(/Configuration unavailable/)).toHaveCount(0);
});
