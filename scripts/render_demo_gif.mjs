#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import puppeteer from 'puppeteer-core';

const __filename = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(__filename), '..');
const htmlPath = path.join(root, 'scripts', 'demo_sketch.html');
const outGif = path.join(root, 'assets', 'spotlight-surgeon-demo.gif');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'spotlight-surgeon-gif-'));
const chromeCandidates = [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
];
const executablePath = chromeCandidates.find((p) => fs.existsSync(p));
if (!executablePath) {
  console.error('No Chromium-based browser found. Install Google Chrome or adjust chromeCandidates.');
  process.exit(1);
}

function run(cmd, args) {
  const res = spawnSync(cmd, args, { stdio: 'inherit' });
  if (res.status !== 0) process.exit(res.status ?? 1);
}

const browser = await puppeteer.launch({
  executablePath,
  headless: 'new',
  args: ['--disable-gpu', '--no-sandbox'],
});

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 960, height: 540, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'networkidle0' });
  await page.waitForFunction('window._p5Ready === true');
  const totalFrames = await page.evaluate('window._totalFrames || 135');
  const canvas = await page.$('canvas');
  if (!canvas) throw new Error('Canvas not found');

  for (let i = 0; i < totalFrames; i++) {
    await page.evaluate(() => redraw());
    const frame = path.join(tmp, `frame-${String(i).padStart(4, '0')}.png`);
    await canvas.screenshot({ path: frame });
  }
} finally {
  await browser.close();
}

fs.mkdirSync(path.dirname(outGif), { recursive: true });
const palette = path.join(tmp, 'palette.png');
run('ffmpeg', [
  '-y',
  '-framerate', '15',
  '-i', path.join(tmp, 'frame-%04d.png'),
  '-vf', 'palettegen=max_colors=192:stats_mode=diff',
  '-frames:v', '1',
  '-update', '1',
  palette,
]);
run('ffmpeg', [
  '-y',
  '-framerate', '15',
  '-i', path.join(tmp, 'frame-%04d.png'),
  '-i', palette,
  '-lavfi', 'fps=15 [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle',
  '-loop', '0',
  outGif,
]);

const bytes = fs.statSync(outGif).size;
console.log(`${outGif}\nframes=135 bytes=${bytes}`);
fs.rmSync(tmp, { recursive: true, force: true });
