import { expect, test } from '@playwright/test';

const realApiEnabled = process.env.HYDROSIM_E2E_REAL_API === '1';
const endpoint = '/api/v1/pedagogical/multisector';

test('D9 real API: sector centre support and timing cross the boundary', async ({ page }) => {
  test.skip(!realApiEnabled, 'Run only in the targeted React + Python end-to-end gate.');
  await page.addInitScript(() => sessionStorage.setItem('hydrosim-language', 'en'));
  const requests: any[] = [];
  const statuses: number[] = [];
  page.on('request', request => {
    if (request.method() === 'POST' && request.url().endsWith(endpoint)) requests.push(request.postDataJSON());
  });
  page.on('response', response => {
    if (response.url().endsWith(endpoint)) statuses.push(response.status());
  });

  await page.goto('/#multisector-lab');
  await expect.poll(() => requests.length).toBeGreaterThan(0);
  expect(statuses.at(-1)).toBe(200);

  const modeCount = requests.length;
  await page.getByRole('button', { name: 'Three TX sectors' }).click();
  await expect.poll(() => requests.length).toBeGreaterThan(modeCount);
  expect(requests.at(-1).sectors).toHaveLength(3);
  expect(statuses.at(-1)).toBe(200);

  const centre = page.getByRole('slider', { name: 'Centre 0°' });
  const centreBefore = Number(await centre.inputValue());
  const centreCount = requests.length;
  await centre.press('ArrowRight');
  await expect.poll(() => requests.length).toBeGreaterThan(centreCount);
  expect(requests.at(-1).sectors.find((s: any) => s.sector_id === 'centre').centre_across_track_deg).toBe(centreBefore + 5);
  expect(statuses.at(-1)).toBe(200);

  const support = page.getByRole('slider', { name: 'Angular support 30°' });
  const supportBefore = Number(await support.inputValue());
  const supportCount = requests.length;
  await support.press('ArrowRight');
  await expect.poll(() => requests.length).toBeGreaterThan(supportCount);
  const selected = requests.at(-1).sectors.find((s: any) => s.sector_id === 'centre');
  expect(selected.across_track_max_deg - selected.across_track_min_deg).toBe(supportBefore + 5);
  expect(statuses.at(-1)).toBe(200);

  const delay = page.getByRole('slider', { name: 'TX delay 0.35 ms' });
  const delayBefore = Number(await delay.inputValue());
  const delayCount = requests.length;
  await delay.press('ArrowRight');
  await expect.poll(() => requests.length).toBeGreaterThan(delayCount);
  expect(requests.at(-1).sectors.find((s: any) => s.sector_id === 'centre').tx_delay_ms).toBeCloseTo(delayBefore + 0.05);
  expect(statuses.at(-1)).toBe(200);
  await expect(page.getByText(/error|unavailable/i)).toHaveCount(0);
});
