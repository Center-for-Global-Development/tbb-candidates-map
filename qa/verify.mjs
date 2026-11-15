#!/usr/bin/env node
/* =============================================================================
   CGD interactive QA gate — deterministic, no LLM. Headless Chromium only.

   Runs the SKILL.md §F audits on each figure at phone/tablet/desktop widths and
   exits non-zero on any failure, so CI can block a broken figure from merging.

   Usage:
     node verify.mjs                       # scans ../figure-* /index.html (template layout)
     node verify.mjs path/to/a.html b.html # explicit files (e.g. a repo of top-level *.html)
     node verify.mjs "$(ls *.html)"        # shell-expanded glob

   Requires: node + playwright (see package.json). First run: npx playwright install chromium
   ============================================================================= */
import { chromium } from 'playwright';
import { readdirSync, existsSync, statSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const WIDTHS = [320, 768, 1200];

// ---- resolve the list of figures to check ----
function defaultFigures() {
  const templatesDir = resolve(__dirname, '..');
  return readdirSync(templatesDir)
    .filter(name => name.startsWith('figure-'))
    .map(name => join(templatesDir, name, 'index.html'))
    .filter(p => existsSync(p));
}
const args = process.argv.slice(2).filter(a => a.endsWith('.html'));
const figures = (args.length ? args.map(a => resolve(a)) : defaultFigures())
  .filter(p => existsSync(p) && statSync(p).isFile());

if (!figures.length) {
  console.error('No figures found to verify. Pass .html paths, or run from templates/qa/.');
  process.exit(2);
}

// ---- the audit that runs INSIDE the page (mirrors chart-core.js CGDCore.audit) ----
function inPageAudit(width) {
  const out = { failures: [] };
  const fail = m => out.failures.push(m);

  // 1. marks actually rendered
  const hasChart = document.querySelector('svg *') || document.querySelector('table.matrix tbody td');
  if (!hasChart) fail('no chart marks rendered (empty svg / table)');

  // 2. shared embed loaded (resize + analytics contract present)
  if (typeof window.CGDTracking === 'undefined') fail('cgd-embed.js did not load (window.CGDTracking missing)');

  // 3. control overflow / clipping
  const panel = document.querySelector('.controls');
  if (panel) {
    const pb = panel.getBoundingClientRect();
    const groups = [...panel.children].filter(n => getComputedStyle(n).display !== 'none')
      .map(n => n.getBoundingClientRect());
    if (groups.some(b => b.left < pb.left - 1 || b.right > pb.right + 1 || b.top < pb.top - 1 || b.bottom > pb.bottom + 1))
      fail('a control group overflows the controls panel');
    const clipped = [...panel.querySelectorAll('button, label')]
      .filter(n => n.scrollWidth > n.clientWidth + 1 || n.scrollHeight > n.clientHeight + 1)
      .map(n => n.textContent.trim());
    if (clipped.length) fail('clipped control text: ' + clipped.join(', '));
  }

  // 4. SVG text overlap / clipping (guard non-SVG nodes)
  const nodes = [...document.querySelectorAll('svg text')].filter(n => n.ownerSVGElement && getComputedStyle(n).visibility !== 'hidden');
  const boxes = nodes.map(n => {
    const r = n.getBoundingClientRect(), s = n.ownerSVGElement.getBoundingClientRect();
    return { t: n.textContent.trim(), l: r.left, r: r.right, tp: r.top, b: r.bottom, sl: s.left, sr: s.right, st: s.top, sb: s.bottom };
  });
  if (boxes.some(x => x.l < x.sl - 1 || x.r > x.sr + 1 || x.tp < x.st - 1 || x.b > x.sb + 1))
    fail('svg text clipped outside its viewBox');
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i], b = boxes[j];
    if (a.l < b.r - 1 && a.r > b.l + 1 && a.tp < b.b - 1 && a.b > b.tp + 1) { fail(`svg text overlap: "${a.t}" / "${b.t}"`); i = boxes.length; break; }
  }

  // 5. no page-level horizontal scroll
  const overflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
  if (overflow > 1) fail('page-level horizontal overflow: ' + overflow + 'px');

  // 6. iOS zoom guard: editable inputs >= 16px at phone widths
  if (width <= 520) {
    const small = [...document.querySelectorAll('input:not([type=checkbox]):not([type=radio]):not([type=range]), textarea, [role="combobox"] input, .search-select input')]
      .filter(n => parseFloat(getComputedStyle(n).fontSize) < 16)
      .map(n => n.id || n.name || n.className);
    if (small.length) fail('editable input < 16px on phone (iOS zoom): ' + small.join(', '));
  }
  return out;
}

// ---- driver ----
const browser = await chromium.launch();
let failed = 0;
for (const file of figures) {
  const url = pathToFileURL(file).href;
  const label = file.split(/[\\/]/).slice(-2).join('/');
  for (const width of WIDTHS) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    const consoleErrors = [];
    page.on('pageerror', e => consoleErrors.push('pageerror: ' + e.message));
    page.on('console', m => { if (m.type() === 'error') consoleErrors.push('console: ' + m.text()); });
    try {
      await page.goto(url, { waitUntil: 'load' });
      await page.waitForFunction(() => window.CGDCore && (document.querySelector('svg') || document.querySelector('table.matrix')), { timeout: 5000 });
      await page.evaluate(() => document.fonts && document.fonts.ready);
      await page.waitForTimeout(120); // let one render frame settle
      const result = await page.evaluate(inPageAudit, width);
      const errs = [...result.failures, ...consoleErrors];
      if (errs.length) { failed++; console.log(`✗ ${label} @ ${width}px`); errs.forEach(e => console.log('    - ' + e)); }
      else console.log(`✓ ${label} @ ${width}px`);
    } catch (e) {
      failed++;
      console.log(`✗ ${label} @ ${width}px`);
      console.log('    - ' + e.message.split('\n')[0]);
      consoleErrors.forEach(x => console.log('    - ' + x));
    } finally {
      await page.close();
    }
  }
}
await browser.close();
console.log(failed ? `\nFAILED: ${failed} figure/width check(s) failed.` : `\nPASS: all figures clean at ${WIDTHS.join('/')}px.`);
process.exit(failed ? 1 : 0);
