#!/usr/bin/env node
/**
 * check-budgets.mjs
 *
 * Purpose:
 *   Compare measured size metrics (from report-export-sizes.mjs) to a budgets JSON file.
 *   Fails with non-zero exit code on budget violations.
 */

import fs from 'node:fs';
import path from 'node:path';

function parseArgs(argv) {
  const args = { budgets: null, sizes: null, warnOnly: false };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--budgets') args.budgets = argv[++i];
    else if (a === '--sizes') args.sizes = argv[++i];
    else if (a === '--warn-only') args.warnOnly = true;
    else if (a === '--help' || a === '-h') {
      console.log('Usage: node check-budgets.mjs --budgets perf-budgets.json --sizes .perf/sizes.json [--warn-only]');
      process.exit(0);
    }
  }
  if (!args.budgets || !args.sizes) {
    console.error('Missing required args. Use --help for usage.');
    process.exit(2);
  }
  return args;
}

function readJson(p) {
  const abs = path.resolve(process.cwd(), p);
  const txt = fs.readFileSync(abs, 'utf8');
  return JSON.parse(txt);
}

function formatBytes(n) {
  const units = ['B', 'KB', 'MB', 'GB'];
  let x = n;
  let u = 0;
  while (x >= 1024 && u < units.length - 1) {
    x /= 1024;
    u++;
  }
  return `${x.toFixed(u === 0 ? 0 : 2)} ${units[u]}`;
}

function main() {
  const { budgets: budgetsPath, sizes: sizesPath, warnOnly } = parseArgs(process.argv);
  const budgets = readJson(budgetsPath);
  const sizes = readJson(sizesPath);

  const budgetBundle = budgets.bundle ?? {};
  const maxJs = budgetBundle.maxJsBundleBytes;
  const maxAssets = budgetBundle.maxTotalAssetsBytes;
  const maxOta = budgetBundle.maxOtaUpdateBytes;

  // Approximate OTA/update payload size: everything except sourcemaps.
  const approxOtaBytes = Math.max(0, (sizes.totalBytes ?? 0) - (sizes.sourcemapBytes ?? 0));

  /** @type {{name: string, limit: number, actual: number, fmt: (n:number)=>string}[]} */
  const checks = [];

  if (typeof maxJs === 'number') {
    checks.push({ name: 'JS bundle bytes', limit: maxJs, actual: sizes.jsBytes ?? 0, fmt: formatBytes });
  }
  if (typeof maxAssets === 'number') {
    checks.push({ name: 'Total asset bytes', limit: maxAssets, actual: sizes.assetBytes ?? 0, fmt: formatBytes });
  }
  if (typeof maxOta === 'number') {
    checks.push({ name: 'Approx OTA/update bytes (minus sourcemaps)', limit: maxOta, actual: approxOtaBytes, fmt: formatBytes });
  }

  if (checks.length === 0) {
    console.log('No size budgets found in budgets file (budgets.bundle.*). Nothing to check.');
    process.exit(0);
  }

  console.log(`\nPerf budget check:`);
  console.log(`- Budgets: ${budgetsPath}`);
  console.log(`- Sizes:   ${sizesPath}`);

  let failures = 0;
  for (const c of checks) {
    const ok = c.actual <= c.limit;
    const status = ok ? 'OK ' : 'FAIL';
    const pct = c.limit === 0 ? '∞' : `${((c.actual / c.limit) * 100).toFixed(1)}%`;
    console.log(`- ${status}  ${c.name}: ${c.fmt(c.actual)} / ${c.fmt(c.limit)}  (${pct})`);
    if (!ok) failures++;
  }

  if (failures > 0) {
    const msg = `\nBudget violations: ${failures}`;
    if (warnOnly) {
      console.warn(msg);
      process.exit(0);
    } else {
      console.error(msg);
      process.exit(1);
    }
  }

  console.log('\nAll checked budgets passed.');
}

main();
