import { expect, test } from '@playwright/test';

const realApiEnabled = process.env.HYDROSIM_E2E_REAL_API === '1';
const geometryPath = '/api/v1/pedagogical/echosounders';
const directionalPath = '/api/v1/pedagogical/echosounders/selected-directional-response';

test('D7 real API: geometry and directional response follow learner controls', async ({ page }) => {
  test.skip(!realApiEnabled, 'Run only in the targeted React + Python end-to-end gate.');
  await page.addInitScript(() => sessionStorage.setItem('hydrosim-language', 'en'));

  const geometryRequests: any[] = [];
  const directionalRequests: any[] = [];
  const statuses: number[] = [];

  page.on('request', request => {
    if (request.method() !== 'POST') return;
    if (request.url().endsWith(geometryPath)) geometryRequests.push(request.postDataJSON());
    if (request.url().endsWith(directionalPath)) directionalRequests.push(request.postDataJSON());
  });
  page.on('response', response => {
    if (response.url().includes('/api/v1/pedagogical/echosounders')) statuses.push(response.status());
  });

  const initialDirectionalPromise = page.waitForResponse(response => response.url().endsWith(directionalPath) && response.request().method() === 'POST');
  await page.goto('/#echosounder-lab');
  const initialDirectional = await initialDirectionalPromise;
  expect(initialDirectional.status()).toBe(200);
  const initialDirectionalBody = await initialDirectional.json();
  await expect.poll(() => geometryRequests.length).toBeGreaterThan(0);
  await expect.poll(() => directionalRequests.length).toBeGreaterThan(0);
  expect(statuses.every(status => status === 200)).toBeTruthy();

  const sector = page.getByRole('slider', { name: 'Sector' });
  const sectorBefore = await sector.inputValue();
  const geometryCount = geometryRequests.length;
  await sector.press('ArrowRight');
  await expect.poll(() => geometryRequests.length).toBeGreaterThan(geometryCount);
  expect(await sector.inputValue()).not.toBe(sectorBefore);
  expect(geometryRequests.at(-1).maximum_angle_deg).not.toBe(geometryRequests.at(-2).maximum_angle_deg);

  await expect(page.getByTestId('d7-selected-directional')).toBeVisible();
  await expect(page.getByRole('img', { name: 'Selected directional response' })).toBeVisible();
  const txAcross = page.getByRole('slider', { name: 'TX across-track beamwidth' });
  const requestCount = directionalRequests.length;
  const changedDirectionalPromise = page.waitForResponse(response => response.url().endsWith(directionalPath) && response.request().method() === 'POST');
  await txAcross.press('ArrowRight');
  const changedDirectional = await changedDirectionalPromise;
  expect(changedDirectional.status()).toBe(200);
  const changedDirectionalBody = await changedDirectional.json();
  await expect.poll(() => directionalRequests.length).toBeGreaterThan(requestCount);
  expect(directionalRequests.at(-1).transmit_across_track_beamwidth_deg).not.toBe(directionalRequests.at(-2).transmit_across_track_beamwidth_deg);
  expect(changedDirectionalBody.tx_one_way.normalized_power).not.toEqual(initialDirectionalBody.tx_one_way.normalized_power);
  expect(statuses.every(status => status === 200)).toBeTruthy();
  await expect(page.getByText(/Scientific API unavailable|response unavailable/i)).toHaveCount(0);
});
