import {expect,test} from '@playwright/test';

const response=(steer:number,source:number)=>({role:'rx',wavelength_m:.0075,steering_angle_deg:steer,source_angle_deg:source,elements:Array.from({length:6},(_,i)=>({index:i,position_y_m:(i-2.5)*.00375,steering_phase_re_broadside_rad:0,residual_phase_rad:(source-steer)*(i-2.5)*.01,contribution_real:1,contribution_imag:0})),evaluated_array_factor_power:1,evaluated_physical_beam_power:1,coherent_sum_real:6,coherent_sum_imag:0,array_factor_pattern:{angle_deg:[-80,0,80],normalized_power:[0,1,0]},physical_beam_pattern:{angle_deg:[-80,0,80],normalized_power:[0,1,0]},peak_angle_deg:steer,half_power_beamwidth_deg:18});

async function setRangeValue(locator:import('@playwright/test').Locator,value:string){await locator.evaluate((element,next)=>{const input=element as HTMLInputElement;const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value')?.set;if(!setter)throw new Error('HTMLInputElement value setter unavailable');setter.call(input,next);input.dispatchEvent(new Event('input',{bubbles:true}));input.dispatchEvent(new Event('change',{bubbles:true}))},value)}

test('D6 keeps the physical array fixed while electronic steering changes',async({page})=>{
 const requests:Array<Record<string,unknown>>=[];
 await page.route('**/api/v1/pedagogical/beamforming',async route=>{const req=route.request().postDataJSON() as Record<string,unknown>;requests.push(req);await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(response(Number(req.steering_angle_deg),Number(req.source_angle_deg)))})});
 await page.goto('/#beamforming-lab');
 await expect(page.getByRole('heading',{name:'Steer a beam without moving the transducer'})).toBeVisible();
 await expect(page.getByText('Fixed 6-element array',{exact:true})).toBeVisible();
 await expect(page.locator('.fixed-elements i')).toHaveCount(6);
 await expect.poll(()=>requests.length).toBeGreaterThan(0);
 expect(requests.at(-1)?.element_count).toBe(6);
 expect(requests.at(-1)?.role).toBe('rx');
 const steering=page.getByLabel('Steering angle');
 await setRangeValue(steering,'30');
 await expect.poll(()=>requests.at(-1)?.steering_angle_deg).toBe(30);
 expect(requests.at(-1)?.element_count).toBe(6);
 await expect(page.getByText('Physical peak').locator('..').getByText('+30°',{exact:true})).toBeVisible();
 await expect(page.locator('.fixed-array-rail span')).toHaveCount(6);
});
