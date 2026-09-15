import { expect, test } from '@playwright/test';

const realApiEnabled=process.env.HYDROSIM_E2E_REAL_API==='1';

test.describe('D1/D2 real scientific API runtime boundary',()=>{
  test.skip(!realApiEnabled,'Run only in the targeted React + Python end-to-end gate.');

  test('D1 renders the real wave-kinematics response',async({page})=>{
    await page.addInitScript(()=>sessionStorage.setItem('hydrosim-language','en'));
    const responses:number[]=[];
    page.on('response',response=>{if(response.url().includes('/api/v1/pedagogical/wave-kinematics'))responses.push(response.status())});
    await page.goto('/#wave-lab');
    await expect.poll(()=>responses.length).toBeGreaterThan(0);
    expect(responses.at(-1)).toBe(200);
    await expect(page.getByText('Scientific API unavailable',{exact:true})).toHaveCount(0);
    await expect(page.locator('.wave-consequence-strip').getByText(/µs$/)).not.toHaveText('— µs');
    await expect(page.locator('.wave-line').first()).toHaveAttribute('d',/L/);
  });

  test('D2 renders the real signal response',async({page})=>{
    await page.addInitScript(()=>sessionStorage.setItem('hydrosim-language','en'));
    const responses:number[]=[];
    page.on('response',response=>{if(response.url().includes('/api/v1/pedagogical/signal'))responses.push(response.status())});
    await page.goto('/#signal-lab');
    await expect.poll(()=>responses.length).toBeGreaterThan(0);
    expect(responses.at(-1)).toBe(200);
    await expect(page.getByText('Signal response unavailable',{exact:true})).toHaveCount(0);
    await expect(page.locator('.signal-story-stage .wave-path').first()).toHaveAttribute('d',/L/);
    await expect(page.locator('.signal-story-stage .echo-path').first()).toHaveAttribute('d',/L/);
  });
});
