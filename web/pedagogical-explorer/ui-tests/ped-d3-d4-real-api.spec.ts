import { expect, test } from '@playwright/test';

const realApiEnabled=process.env.HYDROSIM_E2E_REAL_API==='1';

test.describe('D3/D4 real scientific API runtime boundary',()=>{
  test.skip(!realApiEnabled,'Run only in the targeted React + Python end-to-end gate.');
  test.beforeEach(async({page})=>{await page.addInitScript(()=>sessionStorage.setItem('hydrosim-language','en'))});

  test('D3 live range/noise controls preserve RL independence from noise while SNR changes',async({page})=>{
    const statuses:number[]=[];
    page.on('response',response=>{if(response.url().includes('/api/v1/pedagogical/sonar-equation'))statuses.push(response.status())});
    await page.goto('/#sonar-equation-lab');
    await expect.poll(()=>statuses.length).toBeGreaterThan(0);
    expect(statuses.at(-1)).toBe(200);
    const rail=page.locator('.d3-budget-rail');
    await expect(rail).toContainText('= Received level');
    await expect(rail).toContainText('= SNR');
    const range=page.getByRole('slider',{name:'Range'});
    const beforeRange=statuses.length;
    await range.press('ArrowRight');
    await expect.poll(()=>statuses.length).toBeGreaterThan(beforeRange);
    expect(statuses.at(-1)).toBe(200);
    const rl=rail.getByText('= Received level',{exact:true}).locator('..').locator('strong');
    const snr=rail.getByText('= SNR',{exact:true}).locator('..').locator('strong');
    const rlBefore=await rl.textContent();
    const snrBefore=await snr.textContent();
    const noise=page.getByRole('slider',{name:'Noise level'});
    const beforeNoise=statuses.length;
    await noise.press('ArrowRight');
    await expect.poll(()=>statuses.length).toBeGreaterThan(beforeNoise);
    expect(statuses.at(-1)).toBe(200);
    await expect(rl).toHaveText(rlBefore??'');
    await expect(snr).not.toHaveText(snrBefore??'');
  });

  test('D4 live profile mismatch renders Truth/Processing displacement and authoritative angle sweep',async({page})=>{
    const statuses:number[]=[];
    page.on('response',response=>{if(response.url().includes('/api/v1/pedagogical/refraction'))statuses.push(response.status())});
    await page.goto('/#refraction-lab');
    await expect.poll(()=>statuses.length).toBeGreaterThan(0);
    expect(statuses.at(-1)).toBe(200);
    await expect(page.getByTestId('truth-ray')).toHaveAttribute('points',/\d/);
    await page.getByRole('button',{name:'3 · Profile mismatch'}).click();
    await expect.poll(()=>statuses.length).toBeGreaterThan(1);
    expect(statuses.at(-1)).toBe(200);
    await expect(page.getByTestId('processing-ray')).toHaveAttribute('points',/\d/);
    // Comparison intentionally starts matched. Create the learner-visible mismatch through the Processing control.
    const processing=page.getByRole('slider',{name:'Processing-profile sound speed'});
    const beforeMismatch=statuses.length;
    await processing.press('ArrowRight');
    await expect.poll(()=>statuses.length).toBeGreaterThan(beforeMismatch);
    expect(statuses.at(-1)).toBe(200);
    await expect(page.getByTestId('endpoint-error-vector')).toBeVisible();
    await expect(page.getByTestId('d4-error-sweep')).toBeVisible();
    await expect(page.getByText('Across-swath consequence',{exact:true})).toBeVisible();
  });
});
