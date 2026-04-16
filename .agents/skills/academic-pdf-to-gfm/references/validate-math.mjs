#!/usr/bin/env node
// validate-math.mjs — KaTeX + GFM structural validator for GitHub-flavored markdown
// Usage: node validate-math.mjs <file.md> [--fix]
// Exits 1 on errors (CI-friendly)
//
// Two-layer validation:
//   Layer 1 — KaTeX: parse errors in $, $$, ```math blocks
//   Layer 2 — GFM:   structural issues KaTeX passes but GitHub pre-processor breaks
//
// GFM checks:
//   E1: multi-line $$ blocks with \\ → must use ```math (GitHub strips \\ in $$ mode)
//   E2: consecutive $$ blocks without blank line → orphaned delimiter cascade
//   W1: bare ^* in $$ blocks → markdown asterisk pairing eats the *
//   W2: \begin{align} (not supported) → use \begin{aligned}
//   W3: \boxed{} → can cause raw LaTeX passthrough
//   W4: \operatorname{} → inconsistent GitHub support
//
// --fix: auto-corrects E1 ($$→```math), E2 (add blank line), W1 (^*→^{\ast})

import { readFileSync, writeFileSync } from 'fs';
import katex from 'katex';

const args = process.argv.slice(2);
const autoFix = args.includes('--fix');
const filePath = args.find(a => !a.startsWith('--'));

if (!filePath) {
  console.error('Usage: node validate-math.mjs <file.md> [--fix]');
  process.exit(2);
}

let src = readFileSync(filePath, 'utf8');

// Helper: get 1-based line number from a byte offset
const lineOf = (pos) => src.slice(0, pos).split('\n').length;

// Helper: collect ranges that are inside fenced code blocks (```...```)
// so we can skip them in structural checks
function buildCodeBlockRanges(text) {
  const ranges = [];
  const re = /^```[^\n]*\n[\s\S]*?^```/gm;
  for (const m of text.matchAll(re)) {
    ranges.push([m.index, m.index + m[0].length]);
  }
  return ranges;
}

function inCodeBlock(pos, ranges) {
  return ranges.some(([s, e]) => pos >= s && pos < e);
}

const codeRanges = buildCodeBlockRanges(src);

// ═══════════════════════════════════════════════════════
// LAYER 1: KaTeX syntax validation
// ═══════════════════════════════════════════════════════
console.log('── KaTeX Syntax Check ──────────────────────────────────────');

const blockRegex = /```math\n([\s\S]+?)```|\$\$\n?([\s\S]+?)\n?\$\$|\$([^\$\n]+?)\$/g;
let katexErrors = 0;
let checked = 0;

for (const match of src.matchAll(blockRegex)) {
  if (inCodeBlock(match.index, codeRanges)) continue;
  const [full, fence, display, inline] = match;
  const eq = (fence || display || inline).trim();
  if (!eq) continue;
  checked++;
  const ln = lineOf(match.index);
  try {
    katex.renderToString(eq, {
      throwOnError: true,
      displayMode: !inline,
      strict: false,
    });
  } catch (e) {
    console.error(`  [KATEX] Line ~${ln}: ${e.message}`);
    console.error(`    ${eq.slice(0, 100).replace(/\n/g, ' ')}`);
    katexErrors++;
  }
}

console.log(`${katexErrors === 0 ? '✓' : '✗'} ${checked} equations checked, ${katexErrors} KaTeX error(s)\n`);

// ═══════════════════════════════════════════════════════
// LAYER 2: GFM structural checks
// ═══════════════════════════════════════════════════════
console.log('── GFM Structural Checks ───────────────────────────────────');

let gfmErrors = 0;
let gfmWarnings = 0;

// E0: $$ and $...$ blocks containing CommonMark escape sequences:
//     \! \, \; \: (spacing) and \{ \} (delimiter escapes)
//     GitHub's markdown pre-processor strips these BEFORE the math renderer runs:
//       \, → ,  \! → !  \{ → {  \} → }
//     \!\left( → !\left( triggers a KaTeX parse error → cascades all subsequent equations.
//     \left\{ → \left{ triggers "Missing or unrecognized delimiter for \left" parse error.
//     Fix: use \lbrace/\rbrace instead of \{/\}; remove \! \, \; (cosmetic spacing only).
for (const m of src.matchAll(/^\$\$(.+)\$\$$/gm)) {
  if (inCodeBlock(m.index, codeRanges)) continue;
  const inner = m[1];
  const badSeqs = (inner.match(/\\[!,;:{}\|]/g) || []);
  if (badSeqs.length > 0) {
    const ln = lineOf(m.index);
    const uniq = [...new Set(badSeqs)].join(' ');
    console.error(`  [E0 ERROR] Line ~${ln}: $$ block contains ${uniq} — pre-processor strips backslash → parse error + cascade`);
    if (badSeqs.some(s => s === '\\{' || s === '\\}')) {
      console.error(`    Fix \\{/\\}: replace \\left\\{ → \\left\\lbrace, \\right\\} → \\right\\rbrace, \\{ → \\lbrace, \\} → \\rbrace`);
    } else {
      console.error(`    Fix: remove spacing commands (cosmetic only). Use \`\`\`math\`\`\` if you need them.`);
    }
    gfmErrors++;
  }
}

// E0b: Inline $...$ blocks containing \{ \} or \, (CommonMark strips backslash)
for (const m of src.matchAll(/\$([^\$\n]+?)\$/g)) {
  if (inCodeBlock(m.index, codeRanges)) continue;
  const inner = m[1];
  const badSeqs = (inner.match(/\\[{},]/g) || []).filter(s => s !== '\\\\');
  if (badSeqs.length > 0) {
    const ln = lineOf(m.index);
    const uniq = [...new Set(badSeqs)].join(' ');
    console.warn(`  [W5 WARN]  Line ~${ln}: inline $...$ contains ${uniq} — pre-processor strips → invisible braces or commas`);
    console.warn(`    Fix: replace \\{ → \\lbrace, \\} → \\rbrace, \\, → (remove)`);
    gfmWarnings++;
  }
}

// E1: Standalone $$ blocks (own-line $$) containing \\
//     GitHub's pre-processor strips \\ before the math renderer sees it
//     Fix: convert to ```math blocks
const standaloneDisplayRe = /\n\$\$\n([\s\S]+?)\n\$\$\n/g;
for (const m of src.matchAll(standaloneDisplayRe)) {
  if (inCodeBlock(m.index, codeRanges)) continue;
  if (m[1].includes('\\\\')) {
    const ln = lineOf(m.index);
    console.error(`  [E1 ERROR] Line ~${ln}: $$ block with \\\\ will break on GitHub — use \`\`\`math instead`);
    console.error(`    ${m[1].split('\n')[0].slice(0, 80)}`);
    gfmErrors++;
  }
}

// E2: Consecutive $$ blocks without a blank line between them
//     The closing $$ of block N and opening $$ of block N+1 on adjacent lines
//     creates an orphaned $ that shifts all subsequent equation delimiters
const lines = src.split('\n');
let prevCloseLine = -2;
let inDollarBlock = false;
for (let i = 0; i < lines.length; i++) {
  const t = lines[i].trim();
  if (!inDollarBlock && t === '$$') {
    // Check if previous close was on the immediately preceding line
    if (i - prevCloseLine === 1) {
      console.error(`  [E2 ERROR] Line ${i + 1}: consecutive $$ block missing blank line (causes orphaned delimiter cascade)`);
      gfmErrors++;
    }
    inDollarBlock = true;
  } else if (inDollarBlock && t === '$$') {
    prevCloseLine = i;
    inDollarBlock = false;
  }
}

// W1: Bare ^* in $$ display blocks — markdown pairs the asterisks as italic markers
for (const m of src.matchAll(/\n\$\$\n([\s\S]+?)\n\$\$\n/g)) {
  if (inCodeBlock(m.index, codeRanges)) continue;
  if (/\^\*(?!\{)/.test(m[1])) {
    const ln = lineOf(m.index);
    console.warn(`  [W1 WARN]  Line ~${ln}: bare ^* in $$ block — use ^{\\ast} to prevent markdown italic pairing`);
    gfmWarnings++;
  }
}
// Also check inline $ blocks
for (const m of src.matchAll(/\$([^\$\n]+?)\$/g)) {
  if (inCodeBlock(m.index, codeRanges)) continue;
  if (/\^\*(?!\{)/.test(m[1])) {
    const ln = lineOf(m.index);
    console.warn(`  [W1 WARN]  Line ~${ln}: bare ^* in inline $...$ — use ^{\\ast}`);
    gfmWarnings++;
  }
}

// W2: \begin{align} (not aligned) — not supported on GitHub
for (const m of src.matchAll(/\\begin\{align\}(?!ed)/g)) {
  if (inCodeBlock(m.index, codeRanges)) continue;
  const ln = lineOf(m.index);
  console.warn(`  [W2 WARN]  Line ~${ln}: \\begin{align} is NOT supported on GitHub — use \\begin{aligned}`);
  gfmWarnings++;
}

// W3: \boxed{} — can cause raw LaTeX passthrough on GitHub
for (const m of src.matchAll(/\\boxed\{/g)) {
  if (inCodeBlock(m.index, codeRanges)) continue;
  const ln = lineOf(m.index);
  console.warn(`  [W3 WARN]  Line ~${ln}: \\boxed{} can cause raw LaTeX passthrough — consider \\mathbf{} or a blockquote`);
  gfmWarnings++;
}

// W4: \operatorname{} — inconsistent GitHub support (active bug)
for (const m of src.matchAll(/\\operatorname\{/g)) {
  if (inCodeBlock(m.index, codeRanges)) continue;
  const ln = lineOf(m.index);
  console.warn(`  [W4 WARN]  Line ~${ln}: \\operatorname{} has inconsistent GitHub support — use \\text{} or \\mathrm{}`);
  gfmWarnings++;
}

// W6: GitLab.com hard limit — 50 total math spans per page
//     After the 50th span (display + inline combined), rendering silently stops.
//     Confirmed 2026-03-15 against GitLab CE 18.9.2 / gitlab.com (issue #368009).
//     Self-hosted GitLab CE: disable with `math_rendering_limits_enabled: false`.
//     GitHub: no such limit.
const GITLAB_COM_LIMIT = 50;
if (checked > GITLAB_COM_LIMIT) {
  console.warn(`  [W6 WARN]  ${checked} total math spans — exceeds GitLab.com's ${GITLAB_COM_LIMIT}-span per-page limit`);
  console.warn(`    Spans ${GITLAB_COM_LIMIT + 1}–${checked} will NOT render on gitlab.com (raw text fallback).`);
  console.warn(`    OK for: self-hosted GitLab CE (disable limit), GitHub (no limit).`);
  gfmWarnings++;
}

const gfmStatus = gfmErrors === 0 ? '✓' : '✗';
console.log(`${gfmStatus} GFM structural: ${gfmErrors} error(s), ${gfmWarnings} warning(s)`);

// ═══════════════════════════════════════════════════════
// LAYER 3: Auto-fix (--fix flag)
// ═══════════════════════════════════════════════════════
if (autoFix) {
  console.log('\n── Auto-Fix ────────────────────────────────────────────────');
  let fixed = src;
  let fixCount = 0;

  // Fix E0: Fix CommonMark escape sequences in single-line $$ blocks
  //   - Remove spacing: \! \, \; \: (cosmetic only)
  //   - Replace delimiters: \{ → \lbrace, \} → \rbrace (prevents \left{ parse error)
  fixed = fixed.replace(/^\$\$(.+)\$\$$/gm, (match, inner) => {
    if (!/\\[!,;:{}\|]/.test(inner)) return match;
    let cleaned = inner;
    // Fix \left\{ and \right\} first
    cleaned = cleaned.replace(/\\left\\{/g, '\\left\\lbrace');
    cleaned = cleaned.replace(/\\right\\}/g, '\\right\\rbrace');
    // Fix remaining \{ and \} — add space if followed by letter
    cleaned = cleaned.replace(/\\{(?=[a-zA-Z0-9])/g, '\\lbrace ');
    cleaned = cleaned.replace(/\\{/g, '\\lbrace');
    cleaned = cleaned.replace(/\\}/g, '\\rbrace');
    // Remove spacing commands
    cleaned = cleaned.replace(/\\!/g, '').replace(/\\,/g, '').replace(/\\;/g, ' ').replace(/\\:/g, ' ');
    if (cleaned !== inner) fixCount++;
    return '$$' + cleaned + '$$';
  });

  // Fix E0b: Fix \{ \} in inline $...$ blocks
  fixed = fixed.replace(/\$([^\$\n]+?)\$/g, (match, inner) => {
    if (!/\\[{}]/.test(inner)) return match;
    let cleaned = inner;
    cleaned = cleaned.replace(/\\left\\{/g, '\\left\\lbrace');
    cleaned = cleaned.replace(/\\right\\}/g, '\\right\\rbrace');
    cleaned = cleaned.replace(/\\{(?=[a-zA-Z0-9])/g, '\\lbrace ');
    cleaned = cleaned.replace(/\\{/g, '\\lbrace');
    cleaned = cleaned.replace(/\\}/g, '\\rbrace');
    cleaned = cleaned.replace(/\\,/g, '');
    if (cleaned !== inner) { fixCount++; return '$' + cleaned + '$'; }
    return match;
  });

  // Fix E1: Convert standalone $$ blocks containing \\ to ```math blocks
  fixed = fixed.replace(/\n\$\$\n([\s\S]+?)\n\$\$\n/g, (match, inner) => {
    if (!inner.includes('\\\\')) return match;
    fixCount++;
    return '\n```math\n' + inner + '\n```\n';
  });

  // Fix E2: Add blank line between consecutive $$ blocks
  // Pattern: closing \n$$\n immediately followed by opening $$\n
  const beforeE2 = fixed;
  fixed = fixed.replace(/\n\$\$\n(\$\$\n)/g, '\n$$\n\n$1');
  if (fixed !== beforeE2) {
    const n = (beforeE2.match(/\n\$\$\n\$\$\n/g) || []).length;
    fixCount += n;
  }

  // Fix W1: Replace bare ^* with ^{\ast} in $$ display blocks
  fixed = fixed.replace(/(\n\$\$\n[\s\S]+?\n\$\$\n)/g, (block) => {
    const r = block.replace(/\^\*(?!\{)/g, '^{\\ast}');
    if (r !== block) fixCount++;
    return r;
  });
  // And in inline $ blocks
  fixed = fixed.replace(/\$([^\$\n]+?)\$/g, (match, inner) => {
    const r = inner.replace(/\^\*(?!\{)/g, '^{\\ast}');
    if (r !== inner) { fixCount++; return '$' + r + '$'; }
    return match;
  });

  if (fixed !== src) {
    writeFileSync(filePath, fixed, 'utf8');
    console.log(`✓ Applied ${fixCount} auto-fix(es) — file updated`);
    console.log('  Fixed: E1 ($$ → ```math for \\\\ blocks), E2 (blank lines), W1 (^* → ^{\\ast})');
  } else {
    console.log('  No auto-fixes needed.');
  }
}

// ═══════════════════════════════════════════════════════
// Summary
// ═══════════════════════════════════════════════════════
const totalErrors = katexErrors + gfmErrors;
console.log('\n── Summary ─────────────────────────────────────────────────');
console.log(`  Equations checked : ${checked} (gitlab.com limit: ${GITLAB_COM_LIMIT})`);
console.log(`  KaTeX errors      : ${katexErrors}`);
console.log(`  GFM errors        : ${gfmErrors}`);
console.log(`  GFM warnings      : ${gfmWarnings}`);
if (autoFix) console.log('  --fix was applied');
console.log('');
if (totalErrors > 0) {
  console.log('Fix errors before pushing to GitHub.');
} else if (gfmWarnings > 0) {
  console.log('No blocking errors. Review warnings before pushing.');
} else {
  console.log('All checks passed — safe to push.');
}

process.exit(totalErrors > 0 ? 1 : 0);
