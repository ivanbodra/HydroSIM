import { expect, test } from '@playwright/test';

const realApiEnabled=process.env.HYDROSIM_E2E_REAL_API==='1';

test.describe('D5 real scientific API runtime boundary',()=>{
  test.skip(!realApiEnabled,'Run only in the targeted React + Python end-to-end gate.');

  test('geometry and frequency drive real array-directivity consequences',async({page})=>{
    await page.addInitScript(()=>sessionStorage.setItem('hydrosim-language','en'));
    const responses:number[]=[];
    page.on('response',response=>{if(response.url().includes('/api/v1/pedagogical/array-directivity'))responses.push(response.status())});
    await page.goto('/#array-directivity-lab');
    await expect.poll(()=>responses.length).toBeGreaterThan(0);
    expect(responses.at(-1)).toBe(200);
    await expect(page.getByText('Scientific API unavailable',{exact:true})).toHaveCount(0);

    const relation=page.getByTestId('d5-relation-strip');
    const envelopeGraphic=page.getByTestId('d5-main-lobe-envelope').getByRole('img');
    const beforeRelation=await relation.innerText();
    const beforeEnvelope=await envelopeGraphic.getAttribute('aria-label');
    const beforeElements=await page.locator('.array-element').count();

    const frequency=page.getByRole('slider',{name:'Frequency'});
    await frequency.press('ArrowRight');
    await expect.poll(()=>responses.length).toBeGreaterThan(1);
    expect(responses.at(-1)).toBe(200);
    await expect.poll(async()=>relation.innerText()).not.toBe(beforeRelation);

    const longCount=page.getByRole('slider',{name:'Along-track elements'});
    await longCount.press('ArrowRight');
    await expect.poll(()=>responses.length).toBeGreaterThan(2);
    expect(responses.at(-1)).toBe(200);
    await expect.poll(()=>page.locator('.array-element').count()).toBeGreaterThan(beforeElements);
    await expect.poll(async()=>envelopeGraphic.getAttribute('aria-label')).not.toBe(beforeEnvelope);
    await expect(page.locator('.beamwidth-bracket')).toHaveCount(2);
    await expect(page.locator('.half-power-guide')).toHaveCount(2);
  });
});
