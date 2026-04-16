#!/usr/bin/env node
/**
 * report-export-sizes.mjs
 *
 * Purpose:
 *   Compute size metrics from an `expo export` output directory.
 *   Designed to be dependency-free so it can run in CI.
 *
 * Typical usage:
 *   npx expo export --dump-assetmap --dump-sourcemap
 *   node scripts/perf/report-export-sizes.mjs --export-dir dist --out .perf/sizes.json
 */

import fs from 'node:fs';
import path from 'node:path';

function parseArgs(argv) {
  const args = { exportDir: 'dist', out: null, top: 20 };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--export-dir') args.exportDir = argv[++i];
    else if (a === '--out') args.out = argv[++i];
    else if (a === '--top') args.top = Number(argv[++i] ?? '20');
    else if (a === '--help' || a === '-h') {
      console.log(`Usage: node report-export-sizes.mjs [--export-dir dist] [--out .perf/sizes.json] [--top 20]`);
      process.exit(0);
    }
  }
  return args;
}

function walk(dir) {
  /** @type {string[]} */
  const files = [];
  /** @type {string[]} */
  const stack = [dir];

  while (stack.length) {
    const cur = stack.pop();
    const entries = fs.readdirSync(cur, { withFileTypes: true });
    for (const ent of entries) {
      const p = path.join(cur, ent.name);
      if (ent.isDirectory()) stack.push(p);
      else if (ent.isFile()) files.push(p);
    }
  }

  return files;
}

function bytesOfFile(filePath) {
  const st = fs.statSync(filePath);
  return st.size;
}

function classify(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const base = path.basename(filePath).toLowerCase();

  // JS bundles / bytecode
  if (ext === '.js' || ext === '.bundle' || ext === '.hbc') return 'js';

  // Sourcemaps
  if (ext === '.map') return 'sourcemap';

  // Common assets
  if (['.png', '.jpg', '.jpeg', '.webp', '.gif', '.heic', '.avif', '.svg'].includes(ext)) return 'image';
  if (['.mp4', '.mov', '.m4v', '.webm', '.mkv'].includes(ext)) return 'video';
  if (['.mp3', '.aac', '.wav', '.m4a', '.ogg', '.flac'].includes(ext)) return 'audio';
  if (['.ttf', '.otf', '.woff', '.woff2'].includes(ext)) return 'font';

  // Metadata / configs
  if (ext === '.json') {
    if (base.includes('assetmap')) return 'assetmap';
    if (base.includes('metadata')) return 'metadata';
    return 'json';
  }

  return 'other';
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
  const { exportDir, out, top } = parseArgs(process.argv);
  const abs = path.resolve(process.cwd(), exportDir);

  if (!fs.existsSync(abs) || !fs.statSync(abs).isDirectory()) {
    console.error(`Export dir not found: ${abs}`);
    process.exit(2);
  }

  const files = walk(abs);

  const byType = new Map();
  const fileEntries = [];

  for (const f of files) {
    const size = bytesOfFile(f);
    const type = classify(f);
    byType.set(type, (byType.get(type) ?? 0) + size);
    fileEntries.push({ file: path.relative(abs, f), type, bytes: size });
  }

  fileEntries.sort((a, b) => b.bytes - a.bytes);

  const totalBytes = fileEntries.reduce((acc, x) => acc + x.bytes, 0);
  const jsBytes = (byType.get('js') ?? 0);
  const assetBytes =
    (byType.get('image') ?? 0) +
    (byType.get('video') ?? 0) +
    (byType.get('audio') ?? 0) +
    (byType.get('font') ?? 0);
  const sourcemapBytes = (byType.get('sourcemap') ?? 0);

  const result = {
    exportDir: exportDir,
    totalBytes,
    jsBytes,
    assetBytes,
    sourcemapBytes,
    fileCount: fileEntries.length,
    byType: Object.fromEntries([...byType.entries()].sort((a, b) => b[1] - a[1])),
    topFiles: fileEntries.slice(0, top),
    generatedAt: new Date().toISOString(),
  };

  // Human output
  console.log(`\nExpo export size report: ${exportDir}`);
  console.log(`- Total:      ${formatBytes(totalBytes)}`);
  console.log(`- JS bundles: ${formatBytes(jsBytes)}`);
  console.log(`- Assets:     ${formatBytes(assetBytes)}`);
  console.log(`- Sourcemaps: ${formatBytes(sourcemapBytes)}`);
  console.log(`- Files:      ${fileEntries.length}`);

  console.log(`\nTop ${Math.min(top, fileEntries.length)} files:`);
  for (const e of fileEntries.slice(0, top)) {
    console.log(`- ${formatBytes(e.bytes).padStart(10)}  [${e.type}]  ${e.file}`);
  }

  if (out) {
    const outAbs = path.resolve(process.cwd(), out);
    fs.mkdirSync(path.dirname(outAbs), { recursive: true });
    fs.writeFileSync(outAbs, JSON.stringify(result, null, 2));
    console.log(`\nWrote JSON report: ${out}`);
  }
}

main();
