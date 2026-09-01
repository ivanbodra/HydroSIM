import { chromium } from '@playwright/test';
import { mkdir } from 'node:fs/promises';

const output = 'assets/screenshots/signal-waveform-lab.png';
await mkdir('assets/screenshots', { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 });
await page.goto('http://127.0.0.1:4173/#signal-lab', { waitUntil: 'networkidle' });
await page.waitForTimeout(700);
await page.screenshot({ path: output, fullPage: true });
await browser.close();
console.log(`Captured ${output}`);
