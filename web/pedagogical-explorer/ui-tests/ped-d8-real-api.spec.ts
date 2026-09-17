import { expect, test } from '@playwright/test';

const realApiEnabled=process.env.HYDROSIM_E2E_REAL_API==='1';

test('D8 real API: gate threshold and High Density state cross the boundary',async({page})=>{
  test.skip(!realApiEnabled,'Run only in the targeted React + Python end-to-end gate.');
  await page.addInitScript(()=>sessionStorage.setItem('hydrosim-language','en'));
  const requests:any[]=[];const statuses:number[]=[];
  page.on('request',request=>{if(request.method()==='POST'&&request.url().endsWith('/api/v1/pedagogical/bottom-detection'))requests.push(request.postDataJSON())});
  page.on('response',response=>{if(response.url().endsWith('/api/v1/pedagogical/bottom-detection'))statuses.push(response.status())});
  await page.goto('/#bottom-detection-lab');await expect.poll(()=>requests.length).toBeGreaterThan(0);await expect.poll(()=>statuses.length).toBeGreaterThan(0);expect(statuses.at(-1)).toBe(200);
  const threshold=page.getByRole('slider',{name:'Detection threshold'});const thresholdBefore=Number(await threshold.inputValue());const thresholdCount=requests.length;
  await threshold.press('ArrowRight');await expect.poll(()=>requests.length).toBeGreaterThan(thresholdCount);await expect.poll(()=>statuses.length).toBeGreaterThan(1);expect(requests.at(-1).threshold).not.toBe(thresholdBefore);expect(statuses.at(-1)).toBe(200);
  const windowEnd=page.getByRole('slider',{name:'Window end'});const windowBefore=Number(await windowEnd.inputValue());const windowCount=requests.length;
  await windowEnd.press('ArrowLeft');await expect.poll(()=>requests.length).toBeGreaterThan(windowCount);expect(requests.at(-1).detection_window_end_ms).toBeCloseTo(Number(await windowEnd.inputValue())/1000);expect(Number(await windowEnd.inputValue())).not.toBe(windowBefore);expect(statuses.at(-1)).toBe(200);
  await page.getByText('More',{exact:true}).click();const highDensity=page.getByLabel('High Density');const hdCount=requests.length;await highDensity.selectOption('on');await expect.poll(()=>requests.length).toBeGreaterThan(hdCount);expect(requests.at(-1).high_density.high_density_enabled).toBe(true);await expect.poll(()=>statuses.length).toBeGreaterThan(3);expect(statuses.at(-1)).toBe(200);await expect(page.getByText('Ordinary × High Density',{exact:true})).toBeVisible();await expect(page.getByText(/could not be updated|not available yet/i)).toHaveCount(0);
});
