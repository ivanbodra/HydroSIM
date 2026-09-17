import { expect, test } from '@playwright/test';

const response = (request: any) => ({
  scenario_id: 'd14-test',
  stages: ['bottom-detection','twtt-range','beam-angle','pose-association','reconstruction','truth-observed'],
  active_stage: request.active_stage,
  stage_index: 0,
  ping_index: request.ping_index,
  beam_index: 17,
  detection_index: 3,
  detection_method: 'amplitude',
  twtt_seconds: request.twtt_seconds,
  reconstructed_range_m: request.sound_speed_mps * request.twtt_seconds / 2,
  detected_across_track_angle_rad: request.detected_across_track_angle_rad,
  associated_pose_position: { x: request.position_x_m, y: request.position_y_m, z: request.position_z_m, unit: 'm' },
  truth_sounding: { x: 0, y: 12, z: 31, unit: 'm' },
  reconstructed_sounding: { x: 0, y: 11.5, z: 30.5, unit: 'm' },
  truth_minus_reconstructed: { x: 0, y: 0.5, z: 0.5, unit: 'm' },
  reconstruction_basis: 'API reconstruction',
  semantics: {},
});

test('D14 stages detection into sounding and withholds truth until Compare', async ({ page }) => {
  let latestRequest: any = null;
  await page.route('**/api/v1/pedagogical/sounding-formation', async route => {
    latestRequest = route.request().postDataJSON();
    await route.fulfill({ contentType: 'application/json', body: JSON.stringify(response(latestRequest)) });
  });

  await page.goto('/#sounding-formation-lab');
  await expect(page.getByText('Observed acoustic detection')).toBeVisible();
  await expect(page.getByRole('button', { name: /Range \/ path/ })).toBeVisible();
  await expect(page.getByText('Truth', { exact: true })).toHaveCount(0);
  await expect.poll(() => latestRequest?.active_stage).toBe('bottom-detection');

  await page.getByRole('button', { name: /Range \/ path/ }).click();
  await expect.poll(() => latestRequest?.active_stage).toBe('twtt-range');
  await expect(page.getByText('Sound speed')).toBeVisible();

  await page.getByRole('button', { name: /Vessel geometry/ }).click();
  await expect(page.getByText('Sensor lever arm')).toBeVisible();

  await page.getByRole('button', { name: /Pose association/ }).click();
  await expect.poll(() => latestRequest?.active_stage).toBe('pose-association');
  await expect(page.getByText('Vessel position')).toBeVisible();
  await expect(page.getByText('Vessel attitude')).toBeVisible();

  await page.getByRole('button', { name: /Compare/ }).click();
  await expect.poll(() => latestRequest?.active_stage).toBe('truth-observed');
  await expect(page.getByText('Truth', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('Truth − reconstructed')).toBeVisible();
});

test('D14 learner flow localizes its primary milestones in PT-BR', async ({ page }) => {
  await page.route('**/api/v1/pedagogical/sounding-formation', async route => {
    const request = route.request().postDataJSON();
    await route.fulfill({ contentType: 'application/json', body: JSON.stringify(response(request)) });
  });
  await page.goto('/#sounding-formation-lab');
  await page.evaluate(() => { sessionStorage.setItem('hydrosim-language', 'pt'); location.reload(); });
  await expect(page.getByText('Detecção acústica observada')).toBeVisible();
  await expect(page.getByRole('button', { name: /Distância \/ caminho/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /Geometria do sensor/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /Associação da pose/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /Comparar/ })).toBeVisible();
});
