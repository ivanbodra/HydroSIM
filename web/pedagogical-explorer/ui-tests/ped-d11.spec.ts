import { expect, test } from '@playwright/test';

const axes = {
  mounting_orientation: { roll_deg: 0, pitch_deg: 0, yaw_deg: 0 },
  x_axis_in_vessel_frame: { x: 1, y: 0, z: 0 },
  y_axis_in_vessel_frame: { x: 0, y: 1, z: 0 },
  z_axis_in_vessel_frame: { x: 0, y: 0, z: 1 },
};

test('PED-D10 edits installation and reference through the current scene-first contract', async ({ page }) => {
  const requests: Array<Record<string, unknown>> = [];
  await page.route('**/api/v1/pedagogical/vessel', async route => {
    const request = route.request().postDataJSON() as Record<string, unknown>;
    requests.push(request);
    const tx = request.transducer_lever_arm_m as { x: number; y: number; z: number };
    const vrp = request.vrp_position_from_envelope_center_m as { x: number; y: number; z: number };
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        vessel_length_m: 30,
        vessel_beam_m: 8,
        vessel_height_m: 6,
        vrp_position_m: vrp,
        gnss_position_m: { x: -1, y: 0, z: -4 },
        imu_position_m: { x: 0, y: 0, z: -1 },
        transducer_position_m: tx,
        gnss_lever_arm_from_selected_vrp_m: { x: -1 - vrp.x, y: -vrp.y, z: -4 - vrp.z },
        imu_lever_arm_from_selected_vrp_m: { x: -vrp.x, y: -vrp.y, z: -1 - vrp.z },
        transducer_lever_arm_from_selected_vrp_m: { x: tx.x - vrp.x, y: tx.y - vrp.y, z: tx.z - vrp.z },
        imu_body_axes: axes,
        transducer_body_axes: axes,
        waterline_z_from_vrp_m: 1,
        static_draft_m: 4,
        keel_z_from_vrp_m: 5,
        transducer_z_from_vrp_m: tx.z,
        transducer_depth_below_waterline_m: 2,
        water_level_m_relative_to_datum: 0,
        metadata: { frame: 'B: +X Forward, +Y Starboard, +Z Down' },
      }),
    });
  });

  await page.goto('/#vessel-configuration-lab');
  await expect(page.getByRole('tab', { name: 'Sonar' })).toHaveAttribute('aria-selected', 'true');
  await expect(page.getByText('INSTALLATION MOVE').first()).toBeVisible();

  const xControl = page.getByRole('slider', { name: 'X · Forward' });
  await xControl.fill('6');
  await expect.poll(() => ((requests.at(-1)?.transducer_lever_arm_m as Record<string, unknown>)?.x)).toBe(6);

  await page.getByRole('tab', { name: 'VRP' }).click();
  await expect(page.getByText('REFERENCE MOVE').first()).toBeVisible();
  await expect(page.getByText('Physical installation unchanged')).toBeVisible();
  await xControl.fill('2');
  await expect.poll(() => ((requests.at(-1)?.vrp_position_from_envelope_center_m as Record<string, unknown>)?.x)).toBe(2);
});
