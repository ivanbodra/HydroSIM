import { expect, test } from '@playwright/test';

test('PED-D8 keeps learner controls wired to canonical echosounder outputs', async ({ page }) => {
  let lastBody:any=null;
  await page.route('**/api/v1/pedagogical/echosounders', async route => {
    lastBody=JSON.parse(route.request().postData()||'{}');
    const beams=lastBody.selected_system==='sbes'?[{steering_angle_deg:0,endpoint_across_track_m:0,incidence_angle_from_normal_deg:0,footprint:{effective_across_track_width_m:2,effective_area_m2:4,across_track_limiting_mechanism:'beam'}}]:[-40,0,40].map((a:number)=>({steering_angle_deg:a,endpoint_across_track_m:a*2,incidence_angle_from_normal_deg:Math.abs(a),footprint:{effective_across_track_width_m:3,effective_area_m2:6,across_track_limiting_mechanism:'beam'}}));
    const system={system:lastBody.selected_system,spacing_method:lastBody.selected_system==='sbes'?null:lastBody.spacing_method,beams,adjacent_across_track_spacings_m:lastBody.selected_system==='sbes'?[]:[80,80],geometric_beam_center_swath_width_m:lastBody.selected_system==='sbes'?0:160,target_across_track_positions_m:null};
    await route.fulfill({json:{selected_system:lastBody.selected_system,target_depth_m:lastBody.vertical_separation_m,sbes:lastBody.selected_system==='sbes'?system:{...system,system:'sbes',beams:[beams[1]??beams[0]],adjacent_across_track_spacings_m:[],geometric_beam_center_swath_width_m:0},mbes:lastBody.selected_system==='mbes'?system:{...system,system:'mbes'},metadata:{}}});
  });
  await page.goto('/#echosounder-lab');
  await expect(page.getByRole('heading',{name:'Single beam or swath?'})).toBeVisible();
  await expect(page.getByText('160.0 m')).toBeVisible();
  await page.getByRole('button',{name:'SBES'}).click();
  await expect.poll(()=>lastBody?.selected_system).toBe('sbes');
  await expect(page.getByText('0.0 m').first()).toBeVisible();
  await page.getByRole('button',{name:'PT-BR'}).click();
  await expect(page.getByRole('heading',{name:'Um feixe ou uma faixa?'})).toBeVisible();
});
