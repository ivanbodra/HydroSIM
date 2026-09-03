import { expect, test } from '@playwright/test';

const angles=[-80,-40,0,40,80];
const response={
 wavelength_m:0.0075,
 physical_aperture_m:0.05925,
 element_positions_m:[-0.028125,-0.024375,-0.020625,-0.016875,-0.013125,-0.009375,-0.005625,-0.001875,0.001875,0.005625,0.009375,0.013125,0.016875,0.020625,0.024375,0.028125],
 element_factor:{angle_deg:angles,normalized_power:[0.2,0.75,1,0.75,0.2]},
 array_factor:{angle_deg:angles,normalized_power:[0.02,0.08,1,0.08,0.02]},
 combined_pattern:{angle_deg:angles,normalized_power:[0.004,0.06,1,0.06,0.004]},
 peak_angle_deg:0,
 peak_normalized_power:1,
 half_power_beamwidth_deg:6.4,
 metadata:{state_semantics:'Configured inputs; Derived outputs',positive_angle_direction:'Port (-Y)',negative_angle_direction:'Starboard (+Y)'}
};

test('PED-D6 consumes canonical patterns, reacts to Configured controls and supports EN/PT-BR',async({page})=>{
 const requests:Array<Record<string,unknown>>=[];
 await page.route('**/api/v1/pedagogical/array-directivity',async route=>{requests.push(route.request().postDataJSON());await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(response)});});
 await page.goto('/#array-directivity-lab');
 await expect(page.getByRole('heading',{name:'Build the aperture and watch the beam emerge.'})).toBeVisible();
 await expect(page.getByText('7.50 mm',{exact:true})).toBeVisible();
 await expect(page.getByText('59.25 mm',{exact:true})).toBeVisible();
 await expect(page.getByText('6.40°',{exact:true})).toBeVisible();
 await expect(page.getByRole('img',{name:'Canonical normalized one-way directivity patterns'})).toBeVisible();
 expect(requests[0].element_count).toBe(16);
 const count=page.getByRole('slider',{name:'Element count'});
 await count.evaluate((node:HTMLInputElement)=>{node.value='24';node.dispatchEvent(new Event('input',{bubbles:true}));});
 await expect.poll(()=>requests.at(-1)?.element_count).toBe(24);
 await page.getByRole('button',{name:'PT-BR'}).click();
 await expect(page.getByRole('heading',{name:'Construa a abertura e observe o feixe surgir.'})).toBeVisible();
 await expect(page.getByText('Configurado',{exact:true})).toBeVisible();
});
