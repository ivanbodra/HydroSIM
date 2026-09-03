import { expect, test } from '@playwright/test';

const angles=[-80,-40,0,20,40,80];
const response={
 role:'tx',wavelength_m:0.0075,steering_angle_deg:20,source_angle_deg:20,
 steering_direction_array_frame:{x:0,y:-0.342,z:0.94},source_direction_array_frame:{x:0,y:-0.342,z:0.94},
 elements:Array.from({length:16},(_,i)=>({index:i,position_y_m:(i-7.5)*0.00375,steering_phase_re_broadside_rad:(i-7.5)*0.3,residual_phase_rad:0,contribution_real:1,contribution_imag:0})),
 evaluated_array_factor_magnitude:1,evaluated_array_factor_power:1,evaluated_physical_beam_power:0.84,coherent_sum_real:16,coherent_sum_imag:0,
 array_factor_pattern:{angle_deg:angles,normalized_power:[0.02,0.08,0.2,1,0.16,0.02]},physical_beam_pattern:{angle_deg:angles,normalized_power:[0.01,0.06,0.18,0.84,0.11,0.01]},
 peak_angle_deg:20,peak_normalized_power:0.84,half_power_beamwidth_deg:7.2,
 metadata:{positive_angle_direction:'Port (-Y)',negative_angle_direction:'Starboard (+Y)',state_semantics:'Configured inputs; Derived outputs'}
};

test('PED-D7 consumes canonical steering outputs, reacts to controls and supports EN/PT-BR',async({page})=>{
 const requests:Array<Record<string,unknown>>=[];
 await page.route('**/api/v1/pedagogical/beamforming',async route=>{const request=route.request().postDataJSON();requests.push(request);await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({...response,role:request.role,steering_angle_deg:request.steering_angle_deg,source_angle_deg:request.source_angle_deg,peak_angle_deg:request.steering_angle_deg})});});
 await page.goto('/#beamforming-lab');
 await expect(page.getByRole('heading',{name:'Steer the array and watch coherence move through space.'})).toBeVisible();
 await expect(page.getByText('7.50 mm',{exact:true})).toBeVisible();
 await expect(page.getByText('7.20°',{exact:true})).toBeVisible();
 await expect(page.getByRole('img',{name:'Canonical steered one-way beam patterns'})).toBeVisible();
 expect(requests[0].steering_angle_deg).toBe(20);
 expect(requests[0].source_angle_deg).toBe(20);
 expect(requests[0].role).toBe('tx');
 const steer=page.getByRole('slider',{name:'Steering angle'});
 await steer.evaluate((node:HTMLInputElement)=>{node.value='35';node.dispatchEvent(new Event('input',{bubbles:true}));});
 await expect.poll(()=>requests.at(-1)?.steering_angle_deg).toBe(35);
 await page.getByLabel('Beamformer role').selectOption('rx');
 await expect.poll(()=>requests.at(-1)?.role).toBe('rx');
 await page.getByRole('button',{name:'PT-BR'}).click();
 await expect(page.getByRole('heading',{name:'Aponte o arranjo e observe a coerência se mover no espaço.'})).toBeVisible();
 await expect(page.getByText('Configurado',{exact:true})).toBeVisible();
});
