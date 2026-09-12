import { expect, test } from '@playwright/test';

test('D13 keeps clock synchronization distinct from latency using API-owned times', async ({ page }) => {
  let latestRequest: any = null;
  await page.route('**/api/v1/pedagogical/timing', async route => {
    latestRequest = route.request().postDataJSON();
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        trigger_time_s: 0,
        tx_time_s: 0.001,
        rx_start_time_s: 0.002,
        rx_end_time_s: 0.022,
        receive_duration_ms: 20,
        tx_to_rx_end_ms: 22,
        sensor_sample_time_s: 0,
        sensor_available_time_s: 0.008,
        sensor_latency_ms: 8,
        vessel_speed_mps: 5,
        clock_synchronization: {
          synchronization_mode: latestRequest.synchronization_mode,
          clock_offset_s: latestRequest.synchronization_mode === 'fixed_clock_offset' ? 0.0125 : 0,
          common_measurement_time_s: 0,
          sensor_reported_time_s: latestRequest.synchronization_mode === 'fixed_clock_offset' ? 0.0125 : 0,
          availability_time_s: 0.008,
          association_time_s: 0.001,
          correction_applied: latestRequest.apply_clock_correction,
          corrected_common_time_s: latestRequest.apply_clock_correction ? 0 : null,
          interpreted_measurement_time_s: latestRequest.apply_clock_correction ? 0 : 0.0125,
          clock_epoch_error_s: latestRequest.apply_clock_correction ? 0 : 0.0125,
        },
        associations: [],
        timeline: [
          { kind: 'trigger', time_s: 0, state: 'Configured' },
          { kind: 'sensor_sample', time_s: 0, state: 'Configured' },
          { kind: 'tx', time_s: 0.001, state: 'Derived' },
          { kind: 'rx_start', time_s: 0.002, state: 'Derived' },
          { kind: 'sensor_available', time_s: 0.008, state: 'Derived' },
          { kind: 'rx_end', time_s: 0.022, state: 'Derived' },
        ],
      }),
    });
  });

  await page.goto('/#timing-lab');
  await expect(page.getByTestId('d13-clock-sync')).toContainText('Ideal common time');

  await page.getByLabel('Synchronization mode').selectOption('fixed_clock_offset');
  const offset = page.locator('label').filter({ hasText: 'Sensor clock offset' }).locator('input[type="range"]');
  await offset.fill('12.5');
  await expect.poll(() => latestRequest?.clock_offset_ms).toBe(12.5);

  const panel = page.getByTestId('d13-clock-sync');
  await expect(panel).toContainText('Common measurement epoch');
  await expect(panel).toContainText('Sensor-reported timestamp');
  await expect(panel).toContainText('Data availability');
  await expect(panel).toContainText('Interpreted common time');
  await expect(panel).toContainText('Clock epoch error');
  await expect(panel).toContainText('12.5 ms');

  await page.getByText('Apply known offset correction').click();
  await expect.poll(() => latestRequest?.apply_clock_correction).toBe(false);
  await expect(panel).toContainText('Clock epoch error');
  await expect(panel).toContainText('12.5 ms');
});

test('D13 clock experiment remains localized in PT-BR', async ({ page }) => {
  await page.addInitScript(() => sessionStorage.setItem('hydrosim-language', 'pt'));
  await page.route('**/api/v1/pedagogical/timing', async route => {
    await route.fulfill({ contentType: 'application/json', body: JSON.stringify({
      trigger_time_s:0,tx_time_s:.001,rx_start_time_s:.002,rx_end_time_s:.022,receive_duration_ms:20,tx_to_rx_end_ms:22,sensor_sample_time_s:0,sensor_available_time_s:.008,sensor_latency_ms:8,vessel_speed_mps:5,
      clock_synchronization:{synchronization_mode:'ideal_common_time',clock_offset_s:0,common_measurement_time_s:0,sensor_reported_time_s:0,availability_time_s:.008,association_time_s:.001,correction_applied:true,corrected_common_time_s:0,interpreted_measurement_time_s:0,clock_epoch_error_s:0},
      associations:[],timeline:[]
    })});
  });
  await page.goto('/#timing-lab');
  const panel = page.getByTestId('d13-clock-sync');
  await expect(panel).toContainText('Sincronização do relógio');
  await expect(panel).toContainText('Época comum da medição');
  await expect(panel).toContainText('Timestamp informado pelo sensor');
  await expect(panel).toContainText('Erro de época do relógio');
});
