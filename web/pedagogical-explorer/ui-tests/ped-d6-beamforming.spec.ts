import {expect,test} from '@playwright/test';

const response=(req:Record<string,unknown>)=>{const mode=String(req.steering_control_mode??'angle');const requested=Number(req.steering_angle_deg??0);const delay=Number(req.delay_gradient_us_per_element??0);const steer=mode==='delay_gradient'?18:requested;const source=Number(req.source_angle_deg??0);const aliased=mode==='delay_gradient';return {role:'rx',wavelength_m:.0075,steering_control_mode:mode,steering_angle_deg:steer,requested_steering_angle_deg:mode==='angle'?requested:null,requested_delay_gradient_us_per_element:mode==='delay_gradient'?delay:null,steering_delay_gradient_us_per_element:-.00085,source_angle_deg:source,reference_channel_index:0,reference_channel_convention:'channel 0',steering_regime:aliased?'aliased':'unambiguous',grating_lobe_angles_deg:aliased?[-47.5]:[],elements:Array.from({length:6},(_,i)=>({index:i,position_y_m:(i-2.5)*.00375,steering_phase_re_broadside_rad:0,residual_phase_rad:(source-steer)*(i)*.01,relative_arrival_offset_us:i*.001,relative_compensation_delay_us:-i*.0008,residual_relative_timing_us:i*.0002,residual_relative_phase_rad:i*.01,contribution_real:1,contribution_imag:0})),evaluated_array_factor_power:1,evaluated_physical_beam_power:1,coherent_sum_real:6,coherent_sum_imag:0,array_factor_pattern:{angle_deg:[-80,0,80],normalized_power:[0,1,0]},physical_beam_pattern:{angle_deg:[-80,0,80],normalized_power:[0,1,0]},peak_angle_deg:steer,half_power_beamwidth_deg:18};};

async function setRangeValue(locator:import('@playwright/test').Locator,value:string){await locator.evaluate((element,next)=>{const input=element as HTMLInputElement;const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value')?.set;if(!setter)throw new Error('HTMLInputElement value setter unavailable');setter.call(input,next);input.dispatchEvent(new Event('input',{bubbles:true}));input.dispatchEvent(new Event('change',{bubbles:true}))},value)}

test('D6 keeps the array fixed and exposes authoritative channel timing',async({page})=>{
 const requests:Array<Record<string,unknown>>=[];
 await page.route('**/api/v1/pedagogical/beamforming',async route=>{const req=route.request().postDataJSON() as Record<string,unknown>;requests.push(req);await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(response(req))})});
 await page.goto('/#beamforming-lab');
 await expect(page.getByRole('heading',{name:'Steer a beam without moving the transducer'})).toBeVisible();
 await expect(page.getByText('Fixed 6-element array',{exact:true})).toBeVisible();
 await expect(page.locator('.fixed-elements i')).toHaveCount(6);
 await expect(page.locator('.timing-row')).toHaveCount(6);
 await expect(page.getByText('Arrival → applied delay → alignment',{exact:true})).toBeVisible();
 await expect(page.getByText('Unambiguous',{exact:true})).toBeVisible();
 const steering=page.getByRole('slider',{name:'Steering angle'});
 await setRangeValue(steering,'30');
 await expect.poll(()=>requests.at(-1)?.steering_angle_deg).toBe(30);
 expect(requests.at(-1)?.element_count).toBe(6);
 await expect(page.getByText('Physical peak').locator('..').getByText('+30°',{exact:true})).toBeVisible();
 await page.locator('label').filter({hasText:'Steering control'}).locator('select').selectOption('delay_gradient');
 const delay=page.getByRole('slider',{name:'Delay per channel'});
 await setRangeValue(delay,'0.001');
 await expect.poll(()=>requests.at(-1)?.steering_control_mode).toBe('delay_gradient');
 expect(requests.at(-1)?.delay_gradient_us_per_element).toBe(.001);
 await expect(page.locator('.beamforming-readouts div').filter({hasText:'Effective steering'}).locator('output')).toHaveText('+18°');
 await expect(page.getByText('Aliased',{exact:true})).toBeVisible();
 await expect(page.getByText('-47.5°',{exact:false})).toBeVisible();
});
