import { chromium } from '@playwright/test';
import { mkdir } from 'node:fs/promises';

await mkdir('assets/screenshots', { recursive: true });
const browser = await chromium.launch({ headless: true });

const captures = [
  ['system-map.png', ''],
  ['signal-waveform-lab.png', '#signal-lab'],
  ['beam-directivity-lab.png', '#beam-lab'],
  ['propagation-water-column-lab.png', '#propagation-lab'],
  ['vessel-sensors-lab.png', '#vessel-lab'],
  ['motion-platform-lab.png', '#motion-lab'],
  ['integrated-survey-lab.png', '#integrated-lab'],
];

for (const [filename, hash] of captures) {
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 });
  await page.goto(`http://127.0.0.1:4173/${hash}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(900);
  const output = `assets/screenshots/${filename}`;
  await page.screenshot({ path: output, fullPage: true });
  await page.close();
  console.log(`Captured ${output}`);
}

await browser.close();
