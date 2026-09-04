import { expect, test } from '@playwright/test';

async function setRangeValue(locator: import('@playwright/test').Locator, value: string) {
  await locator.evaluate((el: HTMLInputElement, nextValue) => {
    const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value')?.set;
    setter?.call(el,nextValue);
    el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
  }, value);
}

test('PED-D17 links learner controls to canonical D8 and D10 outputs', async ({ page }) => {
  const echoRequests: Array<Record<string, unknown>> = [];
  const multiRequests: Array<Record<string, unknown>> = [];
  await page.route('**/api/v1/pedagogical/echosounders', async route => {
    echoRequests.push(route.request().postDataJSON() as Record<string, unknown>);
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({mbes:{beams:[{endpoint_across_track_m:80,footprint:{effective_across_track_width_m:2.4}},{endpoint_across_track_m:0,footprint:{effective_across_track_width_m:1.2}},{endpoint_across_track_m:-80,footprint:{effective_across_track_width_m:2.4}}],adjacent_across_track_spacings_m:[80,80],geometric_beam_center_swath_width_m:160}})});
  });
  await page.route('**/api/v1/pedagogical/multisector', async route => {
    multiRequests.push(route.request().postDataJSON() as Record<string, unknown>);
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({sectors:[{sector_id:'port',wavelength_m:.005,tx_time_s:10,tx_end_time_s:10.0005},{sector_id:'centre',wavelength_m:.005,tx_time_s:10.00035,tx_end_time_s:10.00085},{sector_id:'starboard',wavelength_m:.005,tx_time_s:10,tx_end_time_s:10.0005}],transmit_groups:[['port','starboard'],['centre']]})});
  });

  await page.goto('/#tradeoff-lab');
  await expect(page.getByRole('heading',{name:'Acquisition trade-offs'})).toBeVisible();
  await expect(page.getByText('160.0 m').first()).toBeVisible();
  await expect(page.getByText('80.0 m').first()).toBeVisible();
  await expect(page.getByText('5.00 mm').first()).toBeVisible();
  await expect(page.getByText('Baseline',{exact:true})).toBeVisible();
  await expect(page.getByText('Current',{exact:true})).toBeVisible();

  const depth=page.locator('label').filter({hasText:'Depth'}).locator('input');
  await setRangeValue(depth,'200');
  await expect.poll(()=>echoRequests.at(-1)?.vertical_separation_m).toBe(200);

  const frequency=page.locator('label').filter({hasText:'Sector frequency'}).locator('input');
  await setRangeValue(frequency,'400');
  await expect.poll(()=>((multiRequests.at(-1)?.sectors as Array<Record<string,unknown>>)?.[1]?.frequency_khz)).toBe(400);

  await page.getByRole('button',{name:'PT-BR'}).click();
  await expect(page.getByRole('heading',{name:'Compromissos da aquisição'})).toBeVisible();
  await expect(page.getByText('Atual',{exact:true})).toBeVisible();
});
