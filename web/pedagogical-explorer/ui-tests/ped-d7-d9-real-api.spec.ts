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
    const response=page.getByTestId('d7-selected-directional');
    await expect(response).toBeVisible();
    const before=await response.innerText();
    await page.getByRole('slider',{name:'Sector'}).press('ArrowRight');
    await expect.poll(()=>geometry.length).toBeGreaterThan(1);
    await expect.poll(()=>directional.length).toBeGreaterThan(1);
    expect(geometry.at(-1)).toBe(200); expect(directional.at(-1)).toBe(200);
    await expect.poll(async()=>response.innerText()).not.toBe(before);
  });

  test('D8 gate, threshold and High Density state cross the real bottom-detection API',async({page})=>{
    await page.addInitScript(()=>sessionStorage.setItem('hydrosim-language','en'));
    const responses=trackStatuses(page,'/api/v1/pedagogical/bottom-detection');
    await page.goto('/#bottom-detection-lab');
    await expect.poll(()=>responses.length).toBeGreaterThan(0); expect(responses.at(-1)).toBe(200);
    const threshold=page.getByRole('slider',{name:'Detection threshold'});
    await threshold.press('ArrowRight');
    await expect.poll(()=>responses.length).toBeGreaterThan(1); expect(responses.at(-1)).toBe(200);
    const windowEnd=page.getByRole('slider',{name:'Window end'});
    await windowEnd.press('ArrowLeft');
    await expect.poll(()=>responses.length).toBeGreaterThan(2); expect(responses.at(-1)).toBe(200);
    await page.getByText('More',{exact:true}).click();
    await page.getByLabel('High Density').selectOption('on');
    await expect.poll(()=>responses.length).toBeGreaterThan(3); expect(responses.at(-1)).toBe(200);
    await expect(page.getByText('Ordinary × High Density',{exact:true})).toBeVisible();
  });

  test('D9 multisector support and timing changes cross the real API',async({page})=>{
    await page.addInitScript(()=>sessionStorage.setItem('hydrosim-language','en'));
    const responses=trackStatuses(page,'/api/v1/pedagogical/multisector');
    await page.goto('/#multisector-lab');
    await expect.poll(()=>responses.length).toBeGreaterThan(0); expect(responses.at(-1)).toBe(200);
    await page.getByRole('button',{name:'Three TX sectors'}).click();
    await expect.poll(()=>responses.length).toBeGreaterThan(1); expect(responses.at(-1)).toBe(200);
    await expect(page.getByRole('button',{name:/TX sector centre:/})).toBeVisible();
    const delay=page.getByRole('slider',{name:'TX delay'});
    await delay.press('ArrowRight');
    await expect.poll(()=>responses.length).toBeGreaterThan(2); expect(responses.at(-1)).toBe(200);
    const support=page.getByRole('slider',{name:'Angular support'});
    await support.press('ArrowRight');
    await expect.poll(()=>responses.length).toBeGreaterThan(3); expect(responses.at(-1)).toBe(200);
    await expect(page.getByText('Same ping · sector-specific TX epochs',{exact:true})).toBeVisible();
  });
});
