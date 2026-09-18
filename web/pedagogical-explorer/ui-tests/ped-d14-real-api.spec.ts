import { expect, test } from '@playwright/test';

test('D14 sounding-formation boundary stays Python-owned end to end', async ({ page }) => {
  test.skip(process.env.HYDROSIM_E2E_REAL_API !== '1', 'requires the live HydroSIM API');

  const endpoint = '/api/v1/pedagogical/sounding-formation';
  await page.goto('/#sounding-formation-lab');

  const soundingResponse = page.waitForResponse(
    response =>
      response.url().includes(endpoint) &&
      response.request().method() === 'POST' &&
      response.request().postDataJSON()?.active_stage === 'reconstruction',
  );
  await page.getByRole('button', { name: /Sounding/ }).click();
  const initial = await soundingResponse;
  expect(initial.status()).toBe(200);
  const initialRequest = initial.request().postDataJSON();
  const initialBody = await initial.json();

  expect(initialRequest.active_stage).toBe('reconstruction');
  expect(initialBody.reconstructed_range_m).toBeGreaterThan(0);
  await expect(page.getByText('Reconstructed sounding', { exact: true }).last()).toBeVisible();
  await expect(page.getByText(new RegExp(`Y ${initialBody.reconstructed_sounding.y.toFixed(2)} · Z ${initialBody.reconstructed_sounding.z.toFixed(2)} m`))).toBeVisible();

  const twtt = page.locator('.sf-control').filter({ hasText: 'TWTT' }).locator('input[type="range"]');
  const changedResponse = page.waitForResponse(
    response =>
      response.url().includes(endpoint) &&
      response.request().method() === 'POST' &&
      response.request().postDataJSON()?.active_stage === 'reconstruction' &&
      response.request().postDataJSON()?.twtt_seconds === 0.06,
  );
  await twtt.fill('60');
  const changed = await changedResponse;
  expect(changed.status()).toBe(200);
  const changedBody = await changed.json();

  expect(changedBody.reconstructed_range_m).not.toBe(initialBody.reconstructed_range_m);
  expect(changedBody.reconstructed_sounding).not.toEqual(initialBody.reconstructed_sounding);
  await expect(page.getByText(`${changedBody.reconstructed_range_m.toFixed(2)} m`, { exact: true })).toBeVisible();
  await expect(page.getByText(new RegExp(`Y ${changedBody.reconstructed_sounding.y.toFixed(2)} · Z ${changedBody.reconstructed_sounding.z.toFixed(2)} m`))).toBeVisible();

  const compareResponse = page.waitForResponse(
    response =>
      response.url().includes(endpoint) &&
      response.request().method() === 'POST' &&
      response.request().postDataJSON()?.active_stage === 'truth-observed',
  );
  await page.getByRole('button', { name: /Compare/ }).click();
  const compared = await compareResponse;
  expect(compared.status()).toBe(200);
  const compareBody = await compared.json();

  await expect(page.getByText('Truth', { exact: true }).last()).toBeVisible();
  await expect(page.getByText(new RegExp(`Y ${compareBody.truth_sounding.y.toFixed(2)} · Z ${compareBody.truth_sounding.z.toFixed(2)} m`))).toBeVisible();
  await expect(page.getByText(new RegExp(`ΔY ${compareBody.truth_minus_reconstructed.y.toFixed(2)} · ΔZ ${compareBody.truth_minus_reconstructed.z.toFixed(2)} m`))).toBeVisible();
});
