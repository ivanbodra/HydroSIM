import { expect, test } from '@playwright/test';

const realApiEnabled = process.env.HYDROSIM_E2E_REAL_API === '1';
const endpoint = '/api/v1/pedagogical/timing';

test('D13 carries learner timing changes through the real Python API', async ({ page }) => {
  test.skip(!realApiEnabled, 'Run only in the targeted React + Python end-to-end gate.');
  await page.addInitScript(() => sessionStorage.setItem('hydrosim-language', 'en'));

  const requests: any[] = [];
  page.on('request', request => {
    if (request.url().endsWith(endpoint) && request.method() === 'POST') requests.push(request.postDataJSON());
  });

  const initialResponsePromise = page.waitForResponse(
    response => response.url().endsWith(endpoint) && response.request().method() === 'POST',
  );
  await page.goto('/#timing-lab');
  const initialResponse = await initialResponsePromise;
  expect(initialResponse.status()).toBe(200);
  const initialBody = await initialResponse.json();
  expect(initialBody.associations[0].stream_id).toBe('position');
  expect(initialBody.associations[0].along_track_timing_consequence_m).not.toBeNull();
  await expect(page.getByText('Measurement → availability → use at TX')).toBeVisible();
  await expect(page.getByText('Position-state timing consequence')).toBeVisible();

  const changedResponsePromise = page.waitForResponse(
    response => response.url().endsWith(endpoint) && response.request().method() === 'POST',
  );
  await page.getByRole('button', { name: 'Attitude' }).click();
  const changedResponse = await changedResponsePromise;
  expect(changedResponse.status()).toBe(200);
  const changedBody = await changedResponse.json();

  await expect.poll(() => requests.at(-1)?.selected_streams?.[0]).toBe('attitude');
  expect(changedBody.associations[0].stream_id).toBe('attitude');
  expect(changedBody.associations[0].age_s).not.toBeNull();
  expect(changedBody.associations[0].along_track_timing_consequence_m).toBeNull();
  await expect(page.getByText('Attitude timing consequence')).toBeVisible();
  await expect(page.getByText('Sample age only — no metre consequence is inferred.')).toBeVisible();
  await expect(page.getByText(/Timing data could not be updated/)).toHaveCount(0);
});
