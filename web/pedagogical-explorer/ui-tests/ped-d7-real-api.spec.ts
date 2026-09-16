import { expect, test } from '@playwright/test';

const realApiEnabled=process.env.HYDROSIM_E2E_REAL_API==='1';

test('D7 real API: geometry and directional response follow learner controls',async({page})=>{
  test.skip(!realApiEnabled,'Run only in the targeted React + Python end-to-end gate.');
  await page.addInitScript(()=>sessionStorage.setItem('hydrosim-language','en'));
  const geometry:any[]=[]; const directional:any[]=[];
  page.on('request',request=>{if(request.method()!=='POST')return;const body=request.postDataJSON();if(request.url().endsWith('/api/v1/pedagogical/echosounders'))geometry.push(body);if(request.url().endsWith('/api/v1/pedagogical/echosounders/selected-directional-response'))directional.push(body)});
  const statuses:number[]=[];page.on('response',response=>{if(response.url().includes('/api/v1/pedagogical/echosounders'))statuses.push(response.status())});
  await page.goto('/#echosounder-lab');
  await expect.poll(()=>geometry.length).toBeGreaterThan(0);await expect.poll(()=>directional.length).toBeGreaterThan(0);expect(statuses.every(s=>s===200)).toBeTruthy();

  const sector=page.getByRole('slider',{name:'Sector'});const sectorBefore=await sector.inputValue();const geometryCount=geometry.length;
  await sector.press('ArrowRight');await expect.poll(()=>geometry.length).toBeGreaterThan(geometryCount);expect(await sector.inputValue()).not.toBe(sectorBefore);expect(geometry.at(-1).maximum_angle_deg).not.toBe(geometry.at(-2).maximum_angle_deg);

  const response=page.getByTestId('d7-selected-directional');await expect(response).toBeVisible();const responseBefore=await response.innerText();
  await page.getByText('More',{exact:true}).click();const txAcross=page.getByRole('slider',{name:'TX across-track beamwidth'});const directionalCount=directional.length;
  await txAcross.press('ArrowRight');await expect.poll(()=>directional.length).toBeGreaterThan(directionalCount);expect(directional.at(-1).transmit_across_track_beamwidth_deg).not.toBe(directional.at(-2).transmit_across_track_beamwidth_deg);await expect.poll(async()=>response.innerText()).not.toBe(responseBefore);
  expect(statuses.every(s=>s===200)).toBeTruthy();await expect(page.getByText(/Scientific API unavailable|response unavailable/i)).toHaveCount(0);
});
