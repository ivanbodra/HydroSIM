import { expect, test } from '@playwright/test';

test('PED-D10 posts canonical sector controls and renders timing/coverage consequences', async ({ page }) => {
  const requests: Array<Record<string, unknown>> = [];
  await page.route('**/api/v1/pedagogical/multisector', async route => {
    const body = route.request().postDataJSON() as Record<string, unknown>;
    requests.push(body);
    const sectors = body.sectors as Array<Record<string, number|string>>;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        sectors: sectors.map((sector, index) => ({
          ...sector,
          sector_index: index,
          tx_time_s: 10 + Number(sector.tx_delay_ms) / 1000,
          tx_end_time_s: 10 + (Number(sector.tx_delay_ms) + Number(sector.pulse_duration_ms)) / 1000,
          wavelength_m: Number(body.sound_speed_mps) / (Number(sector.frequency_khz) * 1000),
        })),
        coverage_supports_deg: sectors.map(sector => [sector.across_track_min_deg, sector.across_track_max_deg]),
        transmit_groups: [[String(sectors[0].sector_id), String(sectors[2].sector_id)], [String(sectors[1].sector_id)]],
        metadata: { across_track_sign: 'positive Port; negative Starboard' },
      }),
    });
  });

  await page.goto('/#multisector-lab');
  await expect(page.getByRole('heading', { name: 'Multisector MBES' })).toBeVisible();
  await expect(page.getByText('PORT + / STARBOARD −')).toBeVisible();
  await expect(page.getByText('ONE PING · MULTIPLE TX EVENTS')).toBeVisible();
  await expect.poll(() => requests.length).toBeGreaterThan(0);

  const initial = requests.at(-1)!;
  expect(initial).toHaveProperty('tx_time_s', 10);
  expect(initial).not.toHaveProperty('tx_time_seconds');
  const initialSectors = initial.sectors as Array<Record<string, unknown>>;
  expect(initialSectors[0]).toHaveProperty('tx_delay_ms');
  expect(initialSectors[0]).not.toHaveProperty('sector_tx_delay_ms');

  const centreDelay = page.locator('.d10-sector-controls').nth(1).getByLabel('TX delay');
  await centreDelay.evaluate((element: HTMLInputElement) => {
    element.value = '1';
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  });
  await expect.poll(() => ((requests.at(-1)?.sectors as Array<Record<string, unknown>>)?.[1]?.tx_delay_ms)).toBe(1);

  await page.getByRole('button', { name: 'PT-BR' }).click();
  await expect(page.getByRole('heading', { name: 'MBES Multissetorial' })).toBeVisible();
  await expect(page.getByText('CADEIA DE AQUISIÇÃO')).toBeVisible();
  await expect(page.getByText('BOMBORDO + / BORESTE −')).toBeVisible();
  await expect(page.getByText('UM PING · MÚLTIPLOS EVENTOS TX')).toBeVisible();
  await expect(page.getByText('Bombordo')).toBeVisible();
  await expect(page.getByText('Boreste')).toBeVisible();
});
