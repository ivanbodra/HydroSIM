import { expect, test } from '@playwright/test';

const realApiEnabled=process.env.HYDROSIM_E2E_REAL_API==='1';

const trackStatuses=(page:any,path:string)=>{
  const statuses:number[]=[];
  page.on('response',(response:any)=>{if(response.url().includes(path))statuses.push(response.status())});
  return statuses;
};

test.describe('D7-D9 real scientific API runtime boundaries',()=>{
  test.skip(!realApiEnabled,'Run only in the targeted React + Python end-to-end gate.');

  test('D7 echosounder geometry and selected directional response cross the real API',async({page})=>{
    await page.addInitScript(()=>sessionStorage.setItem('hydrosim-language','en'));
    const geometry=trackStatuses(page,'/api/v1/pedagogical/echosounders');
    const directional=trackStatuses(page,'/api/v1/pedagogical/echosounders/selected-directional-response');
    await page.goto('/#echosounder-lab');
    await expect.poll(()=>geometry.length).toBeGreaterThan(0);
    await expect.poll(()=>directional.length).toBeGreaterThan(0);
    expect(geometry.at(-1)).toBe(200); expect(directional.at(-1)).toBe(200);

    const swathReadout=page.locator('.echo-readouts').first();
    const swathBefore=await swathReadout.innerText();
    await page.getByRole('slider',{name:'Sector'}).press('ArrowRight');
    await expect.poll(()=>geometry.length).toBeGreaterThan(1);
    expect(geometry.at(-1)).toBe(200);
    await expect.poll(async()=>swathReadout.innerText()).not.toBe(swathBefore);

    const response=page.getByTestId('d7-selected-directional');
    await expect(response).toBeVisible();
    const responseBefore=await response.innerText();
    const directionalCount=directional.length;
    await page.locator('.echo-water .echo-physical-point').nth(5).click();
    await expect.poll(()=>directional.length).toBeGreaterThan(directionalCount);
    expect(directional.at(-1)).toBe(200);
    await expect.poll(async()=>response.innerText()).not.toBe(responseBefore);
    await expect(page.getByText(/Scientific API unavailable|response unavailable/i)).toHaveCount(0);
  });

  test('D8 gate, threshold and High Density state cross the real bottom-detection API',async({page})=>{
    await page.addInitScript(()=>sessionStorage.setItem('hydrosim-language','en'));
    const responses=trackStatuses(page,'/api/v1/pedagogical/bottom-detection');
    await page.goto('/#bottom-detection-lab');
    await expect.poll(()=>responses.length).toBeGreaterThan(0); expect(responses.at(-1)).toBe(200);
    const readouts=page.locator('.d9-readouts');
    const initialReadouts=await readouts.innerText();

    const threshold=page.getByRole('slider',{name:'Detection threshold'});
    await threshold.press('ArrowRight');
    await expect.poll(()=>responses.length).toBeGreaterThan(1); expect(responses.at(-1)).toBe(200);

    const windowEnd=page.getByRole('slider',{name:'Window end'});
    for(let i=0;i<4;i++)await windowEnd.press('ArrowLeft');
    await expect.poll(()=>responses.length).toBeGreaterThan(2); expect(responses.at(-1)).toBe(200);
    await expect.poll(async()=>readouts.innerText()).not.toBe(initialReadouts);

    await page.getByText('More',{exact:true}).click();
    await page.getByLabel('High Density').selectOption('on');
    await expect.poll(()=>responses.length).toBeGreaterThan(3); expect(responses.at(-1)).toBe(200);
    await expect(page.getByText('Ordinary × High Density',{exact:true})).toBeVisible();
    await expect(page.getByText(/could not be updated|not available yet/i)).toHaveCount(0);
  });

  test('D9 multisector centre, support and timing changes cross the real API',async({page})=>{
    await page.addInitScript(()=>sessionStorage.setItem('hydrosim-language','en'));
    const responses=trackStatuses(page,'/api/v1/pedagogical/multisector');
    await page.goto('/#multisector-lab');
    await expect.poll(()=>responses.length).toBeGreaterThan(0); expect(responses.at(-1)).toBe(200);
    await page.getByRole('button',{name:'Three TX sectors'}).click();
    await expect.poll(()=>responses.length).toBeGreaterThan(1); expect(responses.at(-1)).toBe(200);

    const centreWedge=page.getByRole('button',{name:/TX sector centre:/});
    await expect(centreWedge).toBeVisible();
    const wedgeBefore=await centreWedge.getAttribute('aria-label');
    const centre=page.getByRole('slider',{name:/Centre/});
    await centre.press('ArrowRight');
    await expect.poll(()=>responses.length).toBeGreaterThan(2); expect(responses.at(-1)).toBe(200);
    await expect.poll(async()=>centreWedge.getAttribute('aria-label')).not.toBe(wedgeBefore);

    const support=page.getByRole('slider',{name:/Angular support/});
    const supportBefore=await centreWedge.getAttribute('aria-label');
    await support.press('ArrowRight');
    await expect.poll(()=>responses.length).toBeGreaterThan(3); expect(responses.at(-1)).toBe(200);
    await expect.poll(async()=>centreWedge.getAttribute('aria-label')).not.toBe(supportBefore);

    const selectedTimeline=page.locator('.d10-timeline-row.selected');
    const timelineBefore=await selectedTimeline.innerText();
    const delay=page.getByRole('slider',{name:/TX delay/});
    await delay.press('ArrowRight');
    await expect.poll(()=>responses.length).toBeGreaterThan(4); expect(responses.at(-1)).toBe(200);
    await expect.poll(async()=>selectedTimeline.innerText()).not.toBe(timelineBefore);
    await expect(page.locator('.d10-message')).toHaveCount(0);
  });
});
