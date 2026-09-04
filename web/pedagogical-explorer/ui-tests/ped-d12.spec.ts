import { expect, test } from '@playwright/test';

test('PED-D12 sends learner motion controls to canonical API and renders Truth outputs', async ({ page }) => {
  const requests: Array<Record<string, unknown>>=[];
  await page.route('**/api/v1/pedagogical/vessel-motion', async route=>{
    const body=route.request().postDataJSON() as Record<string, unknown>;requests.push(body);
    const heading=Number(body.heading_deg);const speed=Number(body.speed_mps);const duration=Number(body.duration_seconds);
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({samples:[{time_seconds:0,north_m:0,east_m:0,down_m:0,roll_deg:0,pitch_deg:0,heading_deg:heading,yaw_deviation_deg:0,heave_up_m:0},{time_seconds:duration,north_m:speed*duration,east_m:1,down_m:-1,roll_deg:4,pitch_deg:2,heading_deg:heading+3,yaw_deviation_deg:3,heave_up_m:1}],metadata:{frame:'N (North-East-Down)'}})});
  });
  await page.goto('/#vessel-motion-lab');
  await expect(page.getByRole('heading',{name:'Vessel Motion'})).toBeVisible();
  await expect.poll(()=>requests.length).toBeGreaterThan(0);
  const speed=page.getByLabel('Speed');
  await speed.evaluate((el:HTMLInputElement)=>{el.value='5';el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}))});
  await expect.poll(()=>Number(requests.at(-1)?.speed_mps)).toBe(5);
  await expect(page.getByText('Not yet represented by the canonical D12 API')).toBeVisible();
  await page.getByRole('button',{name:'PT-BR'}).click();
  await expect(page.getByRole('heading',{name:'Movimento da Embarcação'})).toBeVisible();
  await page.getByRole('button',{name:/Roll/}).first().click();
  await expect(page.getByText(/eixo longitudinal/)).toBeVisible();
});
