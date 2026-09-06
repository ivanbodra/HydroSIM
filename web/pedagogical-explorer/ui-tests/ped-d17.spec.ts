import { expect, test } from '@playwright/test';

async function setRangeValue(locator: import('@playwright/test').Locator, value: string) {
  await locator.evaluate((el: HTMLInputElement, nextValue) => {
    const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value')?.set;
    setter?.call(el,nextValue);
    el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
  }, value);
}

test('PED-D17 links learner controls to acquisition and detection outputs', async ({ page }) => {
  const echoRequests: Array<Record<string, unknown>> = [];
  const multiRequests: Array<Record<string, unknown>> = [];
  const detectionRequests: Array<Record<string, unknown>> = [];
  await page.route('**/api/v1/pedagogical/echosounders', async route => {
    echoRequests.push(route.request().postDataJSON() as Record<string, unknown>);
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({mbes:{beams:[{endpoint_across_track_m:80,footprint:{effective_across_track_width_m:2.4}},{endpoint_across_track_m:0,footprint:{effective_across_track_width_m:1.2}},{endpoint_across_track_m:-80,footprint:{effective_across_track_width_m:2.4}}],adjacent_across_track_spacings_m:[80,80],geometric_beam_center_swath_width_m:160}})});
  });
  await page.route('**/api/v1/pedagogical/multisector', async route => {
    multiRequests.push(route.request().postDataJSON() as Record<string, unknown>);
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({sectors:[{sector_id:'port',wavelength_m:.005,tx_time_s:10,tx_end_time_s:10.0005},{sector_id:'centre',wavelength_m:.005,tx_time_s:10.00035,tx_end_time_s:10.00085},{sector_id:'starboard',wavelength_m:.005,tx_time_s:10,tx_end_time_s:10.0005}],transmit_groups:[['port','starboard'],['centre']]})});
  });
  await page.route('**/api/v1/pedagogical/bottom-detection', async route => {
    const request=route.request().postDataJSON() as Record<string, unknown>;
    detectionRequests.push(request);
    const hd=Boolean(request.high_density_enabled);
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({retained_candidates:request.multiple_detections_enabled?[{sample_index:3},{sample_index:5}]:[{sample_index:3}],high_density:{enabled:hd,point_count:hd?5:1,density_multiplier:hd?5:1,target_spacing_m:hd?.24:1.2}})});
  });

  await page.goto('/#tradeoff-lab');
  await expect(page.getByRole('heading',{name:'Acquisition trade-offs'})).toBeVisible();
  await expect(page.getByText('160.0 m').first()).toBeVisible();
  await expect(page.getByText('80.0 m').first()).toBeVisible();
  await expect(page.getByText('5.00 mm').first()).toBeVisible();
  await expect(page.getByText('Baseline',{exact:true})).toBeVisible();
  await expect(page.getByText('Current',{exact:true})).toBeVisible();
  await expect(page.getByText('High Density points')).toBeVisible();

  const depth=page.locator('label').filter({hasText:'Depth'}).locator('input');
  await setRangeValue(depth,'200');
  await expect.poll(()=>echoRequests.at(-1)?.vertical_separation_m).toBe(200);

  const frequency=page.locator('label').filter({hasText:'Sector frequency'}).locator('input');
  await setRangeValue(frequency,'400');
  await expect.poll(()=>((multiRequests.at(-1)?.sectors as Array<Record<string,unknown>>)?.[1]?.frequency_khz)).toBe(400);

  await page.locator('label').filter({hasText:'Detection retention'}).locator('select').selectOption('multiple');
  await expect.poll(()=>detectionRequests.at(-1)?.multiple_detections_enabled).toBe(true);
  await expect(page.getByText('2').first()).toBeVisible();
  await page.locator('label').filter({hasText:'High Density'}).locator('select').selectOption('on');
  await expect.poll(()=>detectionRequests.at(-1)?.high_density_enabled).toBe(true);
  await expect(page.getByText('5×').first()).toBeVisible();

  await page.getByRole('button',{name:'PT-BR'}).click();
  await expect(page.getByRole('heading',{name:'Compromissos da aquisição'})).toBeVisible();
  await expect(page.getByText('Atual',{exact:true})).toBeVisible();
  await expect(page.getByText('Pontos High Density')).toBeVisible();
});
