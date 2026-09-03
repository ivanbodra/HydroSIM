import { expect, test } from '@playwright/test';

const waveResponse = {
  period_seconds: 0.000005,
  wavelength_m: 0.0075,
  temporal_waveform: { x: [0, 1, 2], y: [0, 1, 0], x_unit: 's', y_unit: 'normalized amplitude' },
  spatial_waveform: { x: [0, 0.00375, 0.0075], y: [0, 1, 0], x_unit: 'm', y_unit: 'normalized amplitude' },
  range_offset_m: null,
  metadata: { propagation_direction: '+x' },
};

const signalResponse = {
  pulse_type: 'lfm',
  waveform: { x: [0, 0.5, 1], y: [0, 1, 0], x_unit: 'ms', y_unit: 'normalized amplitude' },
  instantaneous_frequency: { x: [0, 0.5, 1], y: [150, 200, 250], x_unit: 'ms', y_unit: 'kHz' },
  matched_filter: { x: [-1, 0, 1], y: [0.1, 1, 0.1], x_unit: 'µs', y_unit: 'normalized power' },
  metadata: { chirp_direction: 'up' },
};

const d3Response = {
  received_level_db_re_1upa: 118.2,
  snr_db: 58.2,
  absorption_db_per_km: 52.4,
  two_way_transmission_loss_db: 71.8,
  received_level_vs_range: { x: [10, 100, 500], y: [150, 118.2, 82], x_unit: 'm', y_unit: 'dB re 1 µPa' },
  snr_vs_range: { x: [10, 100, 500], y: [90, 58.2, 22], x_unit: 'm', y_unit: 'dB' },
  frequency_loss_comparison: [
    { frequency_khz: 200, absorption_db_per_km: 52.4, two_way_transmission_loss_db: 71.8 },
    { frequency_khz: 400, absorption_db_per_km: 104.8, two_way_transmission_loss_db: 82.3 },
  ],
  contribution_breakdown: {
    source_level_db: 210,
    tx_relative_beam_gain_db: 0,
    outbound_spreading_loss_db: 40,
    outbound_absorption_loss_db: 5.2,
    outbound_total_loss_db: 45.2,
    backscatter_strength_db: -30,
    inbound_spreading_loss_db: 40,
    inbound_absorption_loss_db: 5.2,
    inbound_total_loss_db: 45.2,
    rx_relative_beam_gain_db: 0,
    noise_level_db: 60,
  },
  metadata: { state_input: 'Configured', state_output: 'Derived' },
};

test('PED-D1 keeps canonical API data flow, interaction and bilingual state visible', async ({ page }) => {
  const requests: Array<Record<string, unknown>> = [];
  await page.route('**/api/v1/pedagogical/wave-kinematics', async (route) => {
    requests.push(route.request().postDataJSON() as Record<string, unknown>);
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(waveResponse) });
  });

  await page.goto('/#wave-lab');
  await expect(page.getByRole('heading', { name: 'Change frequency and watch time and space respond together.' })).toBeVisible();
  await expect(page.getByText('CONFIGURED', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('DERIVED', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('5.00 µs')).toBeVisible();
  await expect(page.getByText('0.0075 m')).toBeVisible();
  await expect(page.getByText(/Propagation direction: \+x/)).toBeVisible();

  const frequency = page.locator('label').filter({ hasText: 'Frequency' }).locator('input[type="range"]');
  await frequency.fill('300');
  await expect.poll(() => requests.length).toBeGreaterThan(1);
  expect(requests.at(-1)?.frequency_khz).toBe(300);

  await page.getByRole('button', { name: 'PT-BR' }).click();
  await expect(page.getByRole('heading', { name: 'Altere a frequência e veja tempo e espaço responderem juntos.' })).toBeVisible();
  await expect(page.getByText('CONFIGURADO', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('DERIVADO', { exact: true }).first()).toBeVisible();
});

test('PED-D2 posts learner controls to the canonical signal endpoint and stays bilingual', async ({ page }) => {
  const requests: Array<Record<string, unknown>> = [];
  await page.route('**/api/v1/pedagogical/signal', async (route) => {
    requests.push(route.request().postDataJSON() as Record<string, unknown>);
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(signalResponse) });
  });

  await page.goto('/#signal-lab');
  await expect(page.getByRole('heading', { name: 'Change the transmitted pulse and watch the same scientific state reshape every visual.' })).toBeVisible();
  await expect(page.getByText('Configured', { exact: true })).toBeVisible();
  await expect(page.getByText('Derived', { exact: true })).toBeVisible();
  await expect(page.getByText('Acoustic passband waveform', { exact: true })).toBeVisible();
  await expect(page.getByText('Instantaneous frequency', { exact: true })).toBeVisible();
  await expect(page.getByText('Matched-filter / autocorrelation response', { exact: true })).toBeVisible();

  const frequency = page.locator('label').filter({ hasText: 'Centre frequency' }).locator('input[type="range"]');
  await frequency.fill('300');
  await expect.poll(() => requests.length).toBeGreaterThan(1);
  expect(requests.at(-1)?.center_frequency_khz).toBe(300);

  await page.getByRole('button', { name: 'CW' }).click();
  await expect.poll(() => requests.length).toBeGreaterThan(2);
  expect(requests.at(-1)?.pulse_type).toBe('cw');
  await expect(page.locator('label').filter({ hasText: 'LFM bandwidth' }).locator('input')).toBeDisabled();

  await page.getByRole('button', { name: 'PT-BR' }).click();
  await expect(page.getByRole('heading', { name: 'Altere o pulso transmitido e veja o mesmo estado científico transformar todas as visualizações.' })).toBeVisible();
  await expect(page.getByText('Entrada configurada')).toBeVisible();
  await expect(page.getByText('Resposta visual derivada')).toBeVisible();
});

test('PED-D3 posts configured controls and renders canonical derived outputs bilingually', async ({ page }) => {
  const requests: Array<Record<string, unknown>> = [];
  await page.route('**/api/v1/pedagogical/sonar-equation', async (route) => {
    requests.push(route.request().postDataJSON() as Record<string, unknown>);
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(d3Response) });
  });

  await page.goto('/#sonar-equation-lab');
  await expect(page.getByRole('heading', { name: 'Follow acoustic energy from source to return — and see where the margin is spent.' })).toBeVisible();
  await expect(page.getByText('CONFIGURED', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('DERIVED', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('118.2 dB', { exact: true })).toBeVisible();
  await expect(page.getByText('58.2 dB', { exact: true })).toBeVisible();
  await expect(page.getByText('71.8 dB', { exact: true })).toBeVisible();
  await expect(page.getByText('52.40 dB/km', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('SNR here is a level-domain margin, not probability of detection or a binary detection result.')).toBeVisible();

  const range = page.locator('label').filter({ hasText: 'Range' }).locator('input[type="range"]');
  await range.fill('250');
  await expect.poll(() => requests.length).toBeGreaterThan(1);
  expect(requests.at(-1)?.range_m).toBe(250);

  await page.getByRole('button', { name: 'PT-BR' }).click();
  await expect(page.getByRole('heading', { name: 'Acompanhe a energia acústica da fonte ao retorno — e veja onde a margem é consumida.' })).toBeVisible();
  await expect(page.getByText('Entradas configuradas')).toBeVisible();
  await expect(page.getByText('DERIVADO', { exact: true }).first()).toBeVisible();
  await expect(page.locator('.d3-budget').getByText('Nível de fonte', { exact: true })).toBeVisible();
  await expect(page.getByText(/71\.8 dB · ida e volta/)).toBeVisible();
});
