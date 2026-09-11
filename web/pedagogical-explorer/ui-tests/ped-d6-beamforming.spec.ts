import {expect,test} from '@playwright/test';

const response=(req:Record<string,unknown>)=>{const mode=String(req.steering_control_mode??'angle');const requested=Number(req.steering_angle_deg??0);const delay=Number(req.delay_gradient_us_per_element??0);const steer=mode==='delay_gradient'?18:requested;const source=Number(req.source_angle_deg??0);const aliased=mode==='delay_gradient';return {role:String(req.role??'rx'),wavelength_m:.0075,steering_control_mode:mode,steering_angle_deg:steer,requested_steering_angle_deg:mode==='angle'?requested:null,requested_delay_gradient_us_per_element:mode==='delay_gradient'?delay:null,steering_delay_gradient_us_per_element:-.00085,source_angle_deg:source,reference_channel_index:0,reference_channel_convention:'channel 0',steering_regime:aliased?'aliased':'unambiguous',grating_lobe_angles_deg:aliased?[-47.5]:[],elements:Array.from({length:6},(_,i)=>({index:i,position_y_m:(i-2.5)*.00375,steering_phase_re_broadside_rad:0,residual_phase_rad:(source-steer)*i*.01,relative_arrival_offset_us:(i-2.5)*source*.00008,relative_compensation_delay_us:-(i-2.5)*steer*.00008,residual_relative_timing_us:(i-2.5)*(source-steer)*.00008,residual_relative_phase_rad:i*.01,contribution_real:1,contribution_imag:0})),evaluated_array_factor_power:1,evaluated_physical_beam_power:1,coherent_sum_real:Math.max(1,6-Math.abs(source-steer)/10),coherent_sum_imag:0,array_factor_pattern:{angle_deg:[-80,0,80],normalized_power:[0,1,0]},physical_beam_pattern:{angle_deg:[-80,steer,80],normalized_power:[0,1,0]},peak_angle_deg:steer,half_power_beamwidth_deg:18};};
const multiResponse=(req:Record<string,unknown>)=>{const source=Number(req.source_angle_deg??0);const angles=(req.steering_angles_deg as number[])??[-30,0,30];return {source_angle_deg:source,reference_channel_index:0,shared_channels:Array.from({length:6},(_,i)=>({index:i,position_y_m:(i-2.5)*.00375,relative_arrival_offset_us:(i-2.5)*source*.00008})),virtual_beams:angles.map((angle,index)=>({steering_angle_deg:angle,steering_delay_gradient_us_per_element:angle/30000,relative_compensation_delays_us:Array.from({length:6},(_,i)=>(i-2.5)*angle/100000),evaluated_array_factor_power:index===1?1:.5,evaluated_physical_beam_power:index===1?1:.5,coherent_sum_real:index===1?6:3,coherent_sum_imag:0,peak_angle_deg:angle,peak_normalized_power:1,half_power_beamwidth_deg:18,physical_beam_pattern:{angle_deg:[-80,angle,80],normalized_power:[0,1,0]}})),metadata:{channel_snapshot:'one shared physical RX element snapshot',virtual_beam_operation:'independent canonical steering/delay set per beam'}}};
async function setRangeValue(locator:import('@playwright/test').Locator,value:string){await locator.evaluate((element,next)=>{const input=element as HTMLInputElement;const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value')?.set;if(!setter)throw new Error('HTMLInputElement value setter unavailable');setter.call(input,next);input.dispatchEvent(new Event('input',{bubbles:true}));input.dispatchEvent(new Event('change',{bubbles:true}))},value)}

test('D6 makes fixed-array beamforming causal and shows shared RX virtual beams',async({page})=>{
 await page.addInitScript(()=>sessionStorage.setItem('hydrosim-language','en'));
 const requests:Array<Record<string,unknown>>=[];const multiRequests:Array<Record<string,unknown>>=[];
 await page.route('**/api/v1/pedagogical/beamforming/multibeam',async route=>{const req=route.request().postDataJSON() as Record<string,unknown>;multiRequests.push(req);await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(multiResponse(req))})});
 await page.route('**/api/v1/pedagogical/beamforming',async route=>{const req=route.request().postDataJSON() as Record<string,unknown>;requests.push(req);await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(response(req))})});
 await page.goto('/#beamforming-lab');
 await expect(page.locator('.lesson-location').getByText('D6',{exact:true})).toBeVisible();
 await expect(page.getByText('Fixed 6-element array',{exact:true})).toBeVisible();
 await expect(page.getByTestId('d6-wavefront-scene')).toBeVisible();
 await expect(page.locator('.scene-element')).toHaveCount(6);
 await expect(page.getByTestId('d6-channel-alignment')).toBeVisible();
 await expect(page.locator('.trace-row')).toHaveCount(6);
 await expect(page.locator('.coherent-meter')).toBeVisible();
 await expect(page.getByText('Same RX channels → several virtual beams',{exact:true})).toBeVisible();
 await expect(page.locator('.shared-dots span')).toHaveCount(6);
 await expect(page.locator('.virtual-beam-grid article')).toHaveCount(3);
 await expect.poll(()=>multiRequests.length).toBeGreaterThan(0);
 expect(multiRequests.at(-1)?.steering_angles_deg).toEqual([-30,0,30]);
 await page.getByRole('combobox',{name:'Virtual RX directions'}).selectOption('45');
 await expect.poll(()=>multiRequests.at(-1)?.steering_angles_deg).toEqual([-45,0,45]);
 const arrivalBefore=await page.locator('.trace-arrival').nth(5).getAttribute('cx');
 const source=page.getByRole('slider',{name:'Arrival angle'});await setRangeValue(source,'20');
 await expect.poll(()=>requests.at(-1)?.source_angle_deg).toBe(20);
 await expect.poll(async()=>page.locator('.trace-arrival').nth(5).getAttribute('cx')).not.toBe(arrivalBefore);
 const steering=page.getByRole('slider',{name:'Steering angle'});await setRangeValue(steering,'20');
 await expect.poll(()=>requests.at(-1)?.steering_angle_deg).toBe(20);
 await expect(page.locator('.trace-residual.aligned')).toHaveCount(6);
 await expect(page.locator('.beamforming-pattern .source-marker')).toHaveCount(1);
 await expect(page.locator('.beamforming-pattern .steer-marker')).toHaveCount(1);
 await page.getByText('More',{exact:true}).click();
 await page.locator('label').filter({hasText:'Steering control'}).locator('select').selectOption('delay_gradient');
 const delay=page.getByRole('slider',{name:'Delay per channel'});await setRangeValue(delay,'0.001');
 await expect.poll(()=>requests.at(-1)?.delay_gradient_us_per_element).toBe(.001);
 await expect(page.getByText('Aliased',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Mudar idioma para português'}).click();
 await expect(page.getByText('Temporização relativa dos canais',{exact:true})).toBeVisible();
});
