import { expect, test } from '@playwright/test';

test('PED-D10 sends configured vessel geometry and renders installation/reference consequences', async ({ page }) => {
  const requests: Array<Record<string, unknown>> = [];
  await page.route('**/api/v1/pedagogical/vessel', async route => {
    requests.push(route.request().postDataJSON() as Record<string, unknown>);
    const request = route.request().postDataJSON() as any;
    const tx = request.transducer_lever_arm_m ?? {x:2,y:0,z:3};
    const gnss = request.gnss_lever_arm_m ?? {x:-1,y:0,z:-4};
    const imu = request.imu_lever_arm_m ?? {x:0,y:0,z:-1};
    const vrp = request.vrp_position_from_envelope_center_m ?? {x:0,y:0,z:0};
    const axes = (orientation:any) => ({mounting_orientation:orientation,x_axis_in_vessel_frame:{x:1,y:0,z:0},y_axis_in_vessel_frame:{x:0,y:1,z:0},z_axis_in_vessel_frame:{x:0,y:0,z:1}});
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({vessel_length_m:30,vessel_beam_m:8,vessel_height_m:6,vrp_position_m:vrp,gnss_position_m:gnss,imu_position_m:imu,transducer_position_m:tx,gnss_lever_arm_from_selected_vrp_m:{x:gnss.x-vrp.x,y:gnss.y-vrp.y,z:gnss.z-vrp.z},imu_lever_arm_from_selected_vrp_m:{x:imu.x-vrp.x,y:imu.y-vrp.y,z:imu.z-vrp.z},transducer_lever_arm_from_selected_vrp_m:{x:tx.x-vrp.x,y:tx.y-vrp.y,z:tx.z-vrp.z},imu_body_axes:axes(request.imu_mounting_orientation_deg ?? {roll_deg:0,pitch_deg:0,yaw_deg:0}),transducer_body_axes:axes(request.transducer_mounting_orientation_deg ?? {roll_deg:0,pitch_deg:0,yaw_deg:0}),waterline_z_from_vrp_m:1,static_draft_m:4,keel_z_from_vrp_m:5,transducer_z_from_vrp_m:tx.z,transducer_depth_below_waterline_m:Math.abs(tx.z-1),water_level_m_relative_to_datum:0,metadata:{frame:'B: +X Forward, +Y Starboard, +Z Down'}})});
  });

  await page.goto('/#vessel-configuration-lab');
  const languageControl=page.getByRole('button',{name:'Mudar idioma para português'});
  await expect(languageControl).toHaveCount(1);
  await expect(page.getByText('Vessel blueprint')).toBeVisible();
  await expect(page.getByText('INSTALLATION MOVE').first()).toBeVisible();

  await page.getByRole('tab',{name:'Sonar'}).click();
  const txX=page.getByLabel('X · Forward');
  await txX.evaluate((el:HTMLInputElement)=>{
    const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value')?.set;
    setter?.call(el,'6');
    el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
  });
  await expect.poll(()=>((requests.at(-1)?.transducer_lever_arm_m as Record<string,unknown>)?.x)).toBe(6);
  await expect(page.getByText('Physical sensor position changes').first()).toBeVisible();

  await page.getByRole('tab',{name:'VRP'}).click();
  await expect(page.getByText('REFERENCE MOVE').first()).toBeVisible();
  await expect(page.getByText('Sensors stay fixed; only reference vectors change').first()).toBeVisible();

  await languageControl.click();
  await expect(page.getByRole('button',{name:'Switch language to English'})).toHaveCount(1);
  await expect(page.getByText('Planta da embarcação')).toBeVisible();
  await expect(page.getByText('X · Proa').first()).toBeVisible();
});
