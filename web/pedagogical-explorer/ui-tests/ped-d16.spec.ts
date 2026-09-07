import { expect, test } from '@playwright/test';

async function setRangeValue(locator: import('@playwright/test').Locator, value: string) {
  await locator.evaluate((el: HTMLInputElement, nextValue) => {
    const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value')?.set;
    setter?.call(el,nextValue);
    el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
  }, value);
}

test('PED-D16 turns planning controls into visible lines and coverage', async ({ page }) => {
  const requests:Array<Record<string,unknown>>=[];
  await page.route('**/api/v1/pedagogical/survey-planning', async route=>{
    const req=route.request().postDataJSON() as Record<string,unknown>;requests.push(req);
    const speed=Number(req.vessel_speed_knots);const overlap=req.overlap_percent as number|null;const spacing=req.line_spacing_m as number|null;
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({status:'ready',reference_geometry:{selected_system:'mbes',reference_depth_m:50,usable_swath_width_m:120,area_length_m:1000,area_width_m:500,line_direction_deg:Number(req.line_direction_deg),vessel_speed_knots:speed,vessel_speed_mps:speed*.5,planning_frame:'local'},spacing_mode:overlap==null?'explicit_spacing':'overlap',configured_overlap_percent:overlap,configured_line_spacing_m:spacing,requested_spacing_m:spacing??96,actual_spacing_m:spacing??95,projected_cross_line_span_m:500,planned_lines:[{line_index:0,center_offset_m:-190,start_m:[-500,-190],end_m:[500,-190],length_m:1000},{line_index:1,center_offset_m:0,start_m:[500,0],end_m:[-500,0],length_m:1000},{line_index:2,center_offset_m:190,start_m:[-500,190],end_m:[500,190],length_m:1000}],coverage_strips:[{line_index:0,polygon_m:[[-500,-250],[500,-250],[500,-130],[-500,-130]]},{line_index:1,polygon_m:[[-500,-60],[500,-60],[500,60],[-500,60]]},{line_index:2,polygon_m:[[-500,130],[500,130],[500,250],[-500,250]]}],line_count:3,total_planned_length_m:3000,overlap_width_m:overlap==null?null:25,gap_width_m:overlap==null?Math.max(0,(spacing??0)-120):null,coverage_classification:overlap==null&&(spacing??0)>120?'gapped':'overlapping',idealized_on_line_time_s:speed===0?null:1800})});
  });
  await page.goto('/#survey-planning-lab');
  await expect(page.getByRole('heading',{name:'Survey planning'})).toBeVisible();
  await expect(page.locator('.d16-line')).toHaveCount(3);
  await expect(page.getByText('3',{exact:true}).first()).toBeVisible();

  const speed=page.locator('label').filter({hasText:'Vessel speed'}).locator('input');
  await setRangeValue(speed,'8');
  await expect.poll(()=>requests.at(-1)?.vessel_speed_knots).toBe(8);

  await page.locator('label').filter({hasText:'Spacing control'}).locator('select').selectOption('spacing');
  const spacing=page.locator('label').filter({hasText:'Line spacing'}).locator('input');
  await setRangeValue(spacing,'180');
  await expect.poll(()=>requests.at(-1)?.line_spacing_m).toBe(180);
  await expect(page.getByText('Gapped')).toBeVisible();

  await page.getByRole('button',{name:'PT-BR'}).click();
  await expect(page.getByRole('heading',{name:'Planejamento do levantamento'})).toBeVisible();
  await expect(page.getByText('Com lacunas')).toBeVisible();
});
