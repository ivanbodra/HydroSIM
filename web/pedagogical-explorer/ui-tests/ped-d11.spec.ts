import { expect, test } from '@playwright/test';

test('PED-D11 sends configured vessel geometry and renders canonical sensor/reference outputs', async ({ page }) => {
  const requests: Array<Record<string, unknown>> = [];
  await page.route('**/api/v1/pedagogical/vessel', async route => {
    requests.push(route.request().postDataJSON() as Record<string, unknown>);
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({vrp_position_m:{x:0,y:0,z:0},gnss_position_m:{x:-1,y:0,z:-4},imu_position_m:{x:0,y:0,z:-1},transducer_position_m:{x:2,y:0,z:3},waterline_z_from_vrp_m:1,static_draft_m:4,keel_z_from_vrp_m:5,transducer_z_from_vrp_m:3,transducer_depth_below_waterline_m:2,water_level_m_relative_to_datum:0,metadata:{frame:'B: +X Forward, +Y Starboard, +Z Down'}})});
  });

  await page.goto('/#vessel-configuration-lab');
  await expect(page.getByRole('heading',{name:'Vessel & Sensor Configuration'})).toBeVisible();
  await expect(page.getByText('2.00 m').first()).toBeVisible();
  await expect(page.getByText('5.00 m',{exact:true})).toBeVisible();

  const txX=page.locator('.d11-lever').first().locator('label').filter({hasText:'X · Forward'}).locator('input');
  await txX.evaluate((el:HTMLInputElement)=>{
    const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value')?.set;
    setter?.call(el,'6');
    el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
  });
  await expect.poll(()=>((requests.at(-1)?.transducer_lever_arm_m as Record<string,unknown>)?.x)).toBe(6);

  await page.getByRole('button',{name:'PT-BR'}).click();
  await expect(page.getByRole('heading',{name:'Configuração da Embarcação e Sensores'})).toBeVisible();
  await expect(page.getByText('X · Proa').first()).toBeVisible();
});
