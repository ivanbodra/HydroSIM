import { expect, test } from '@playwright/test';

const ray={start_depth_m:0,target_depth_m:100,launch_angle_deg_from_vertical:30,ray_parameter_seconds_per_m:0.0003333,horizontal_distance_m:58.2,path_length_m:115.4,travel_time_seconds:0.0764,segments:[{layer_index:0,start_depth_m:0,end_depth_m:50,sound_speed_mps:1500,angle_from_vertical_deg:30,horizontal_distance_m:28.9,path_length_m:57.7,travel_time_seconds:0.0385,ray_parameter_seconds_per_m:0.0003333},{layer_index:1,start_depth_m:50,end_depth_m:100,sound_speed_mps:1520,angle_from_vertical_deg:30.47,horizontal_distance_m:29.3,path_length_m:57.7,travel_time_seconds:0.0379,ray_parameter_seconds_per_m:0.0003333}]};

test('PED-D4 uses canonical refraction response, comparison state and bilingual copy',async({page})=>{
 const requests:Array<Record<string,unknown>>=[];
 await page.route('**/api/v1/pedagogical/refraction',async route=>{const body=route.request().postDataJSON();requests.push(body);const processing={...ray,target_depth_m:98.7,horizontal_distance_m:56.9};await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({reference_ray:ray,profile_comparison:body.processing_profile?{reference:ray,processing,horizontal_endpoint_error_m:-1.3,depth_endpoint_error_m:-1.3,path_length_difference_m:-1.1,travel_time_difference_seconds:0}:null,metadata:{ray_outputs_state:'Derived'}})});});
 await page.goto('/#refraction-lab');
 await expect(page.getByRole('heading',{name:'Bend the ray by changing the water column.'})).toBeVisible();
 await expect(page.getByText('Horizontal distance',{exact:true})).toBeVisible();
 await expect(page.getByText('58.20 m',{exact:true})).toBeVisible();
 expect(requests[0].processing_profile).toBeNull();
 await page.getByRole('button',{name:'Wrong processing profile'}).click();
 await expect.poll(()=>requests.length).toBeGreaterThan(1);
 expect(requests.at(-1)?.processing_profile).not.toBeNull();
 await expect(page.getByText(/Δx -1.30 m/)).toBeVisible();
 await page.getByRole('button',{name:'PT-BR'}).click();
 await expect(page.getByRole('heading',{name:'Curve o raio alterando a coluna d’água.'})).toBeVisible();
 await expect(page.getByText('Configurado',{exact:true})).toBeVisible();
});
