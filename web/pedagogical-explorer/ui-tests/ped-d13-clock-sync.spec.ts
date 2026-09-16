import { expect, test } from '@playwright/test';

const response = (request: any) => ({
  trigger_time_s: 0,
  tx_time_s: 0.041,
  rx_start_time_s: 0.042,
  rx_end_time_s: 0.062,
  receive_duration_ms: 20,
  tx_to_rx_end_ms: 62,
  vessel_speed_mps: request.vessel_speed_mps,
  clock_synchronization: {
    synchronization_mode: request.synchronization_mode,
    clock_offset_s: request.synchronization_mode === 'fixed_clock_offset' ? 0.0125 : 0,
    common_measurement_time_s: 0.02,
    sensor_reported_time_s: request.synchronization_mode === 'fixed_clock_offset' ? 0.0325 : 0.02,
    availability_time_s: 0.028,
    association_time_s: 0.041,
    correction_applied: request.apply_clock_correction,
    corrected_common_time_s: request.apply_clock_correction ? 0.02 : null,
    interpreted_measurement_time_s: request.apply_clock_correction ? 0.02 : 0.0325,
    clock_epoch_error_s: request.apply_clock_correction ? 0 : 0.0125,
  },
  associations: [{
    stream_id: request.selected_streams[0],
    update_rate_hz: request.selected_streams[0] === 'position' ? request.position_update_rate_hz : request.attitude_update_rate_hz,
    sample_period_s: request.selected_streams[0] === 'position' ? 1 / request.position_update_rate_hz : 1 / request.attitude_update_rate_hz,
    latency_ms: request.selected_streams[0] === 'position' ? request.position_latency_ms : request.attitude_latency_ms,
    tx_time_s: 0.041,
    available: true,
    sample_time_s: 0.02,
    availability_time_s: 0.028,
    age_s: 0.021,
    along_track_timing_consequence_m: request.selected_streams[0] === 'position' ? 0.105 : null,
  }],
});

test('D13 exposes measurement to availability to TX causality without frontend timing arithmetic', async ({ page }) => {
  let latestRequest: any = null;
  await page.route('**/api/v1/pedagogical/timing', async route => {
    latestRequest = route.request().postDataJSON();
    await route.fulfill({ contentType: 'application/json', body: JSON.stringify(response(latestRequest)) });
  });

  await page.goto('/#timing-lab');
  await expect(page.getByText('Measurement → availability → use at TX')).toBeVisible();
  await expect(page.getByText('Latest available at TX')).toBeVisible();
  await expect(page.getByText('Sample age')).toBeVisible();
  await expect(page.getByText('0.10 m')).toBeVisible();

  await page.getByRole('button', { name: 'Attitude' }).click();
  await expect.poll(() => latestRequest?.selected_streams?.[0]).toBe('attitude');
  await expect(page.getByText('Sample age only — no metre consequence is inferred.')).toBeVisible();
});

test('D13 keeps synchronization distinct from latency and localized in PT-BR', async ({ page }) => {
  let latestRequest: any = null;
  await page.route('**/api/v1/pedagogical/timing', async route => {
    latestRequest = route.request().postDataJSON();
    await route.fulfill({ contentType: 'application/json', body: JSON.stringify(response(latestRequest)) });
  });

  await page.goto('/#timing-lab');
  await page.getByText('Synchronization').click();
  await page.getByLabel('Synchronization mode').selectOption('fixed_clock_offset');
  const offset = page.locator('label').filter({ hasText: 'Sensor clock offset' }).locator('input[type="range"]');
  await offset.fill('12.5');
  await expect.poll(() => latestRequest?.clock_offset_ms).toBe(12.5);
  await expect(page.getByTestId('d13-clock-sync')).toContainText('12.5 ms');

  await page.evaluate(() => { sessionStorage.setItem('hydrosim-language', 'pt'); location.reload(); });
  await expect(page.getByText('Medição → disponibilidade → uso no TX')).toBeVisible();
  await expect(page.getByText('Consequência temporal no estado de posição')).toBeVisible();
});
