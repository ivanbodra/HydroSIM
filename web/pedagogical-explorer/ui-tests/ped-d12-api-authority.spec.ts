import { expect, test } from '@playwright/test';

test('D12 submits the learner stream by canonical PU profile id only', async ({ page }) => {
  let body: Record<string, unknown> | null = null;
  await page.route('**/api/v1/pedagogical/pu-sensor', async route => {
    body = route.request().postDataJSON() as Record<string, unknown>;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'compatible',
        reason_codes: [],
        summary: {
          stream_id: 'learner-stream',
          pu_input_id: 'PU-A',
          device_class: 'position_sensor',
          transport_kind: 'serial',
          connection: 'COM1 @ 115200 Bd',
          protocol_id: 'nav',
          message_id: 'position',
          update_rate_hz: 10,
          nominal_update_period_s: 0.1,
          timestamp_source: 'gnss_utc'
        },
        pu_input_profile: { input_id: 'PU-A' },
        metadata: { profile_authority: 'Python/API-owned pedagogical profile when pu_input_id is used' }
      })
    });
  });

  await page.goto('/#pu-sensor-lab');
  await expect.poll(() => body).not.toBeNull();
  expect(body?.pu_input_id).toBe('PU-A');
  expect(body).not.toHaveProperty('pu_input');
  expect(body).toHaveProperty('stream');
  await expect(page.getByText('PU-A', { exact: true })).toBeVisible();
});
