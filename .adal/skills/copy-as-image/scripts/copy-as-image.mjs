#!/usr/bin/env node
/**
 * copy-as-image: Convert markdown text to a beautiful Carbon/Ray.so style PNG and copy to clipboard.
 *
 * Usage:
 *   node copy-as-image.mjs /path/to/text-file.txt
 *   echo "Hello World" | node copy-as-image.mjs
 *
 * Pipeline: text (file or stdin) → markdown parse → SVG (with shadow, gradient, window chrome) → PNG → clipboard
 */

import { Resvg } from "@resvg/resvg-js";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";
import { execSync } from "child_process";

// ═══════════════════════════════════════════════════════════════════════
// One Dark Theme
// ═══════════════════════════════════════════════════════════════════════

const THEME = {
  // Card
  cardBg:    "#282c34",
  titleBar:  "#21252b",
  // Text
  fg:        "#abb2bf",
  heading:   "#61afef",
  bold:      "#e5c07b",
  code:      "#d19a66",
  codeFg:    "#abb2bf",
  codeBg:    "#2c313a",
  bullet:    "#c678dd",
  link:      "#56b6c2",
  dim:       "#5c6370",
  string:    "#98c379",
  keyword:   "#c678dd",
  // Traffic lights
  red:       "#ff5f57",
  yellow:    "#febc2e",
  green:     "#28c840",
  redStroke: "#e0443e",
  yellowStroke: "#dea123",
  greenStroke:  "#14ae46",
};

// Background gradient presets
const GRADIENTS = {
  midnight: { from: "#0f0c29", via: "#302b63", to: "#24243e" },
  breeze:   { from: "#0ea5e9", to: "#6366f1" },
  candy:    { from: "#7928ca", to: "#ff0080" },
  sunset:   { from: "#f97316", via: "#ef4444", to: "#ec4899" },
  meadow:   { from: "#22c55e", to: "#0ea5e9" },
  ocean:    { from: "#667eea", to: "#764ba2" },
  aurora:   { from: "#10b981", via: "#3b82f6", to: "#8b5cf6" },
};

const ACTIVE_BG = GRADIENTS.midnight;

// ═══════════════════════════════════════════════════════════════════════
// Character Width & Word Wrap
// ═══════════════════════════════════════════════════════════════════════

/** Check if a character is a CJK (full-width) character */
function isFullWidth(ch) {
  const code = ch.codePointAt(0);
  if (code === undefined) return false;
  // CJK Unified Ideographs, CJK Extension A/B, CJK Compatibility, Hangul, Katakana, etc.
  return (
    (code >= 0x1100 && code <= 0x115f) ||   // Hangul Jamo
    (code >= 0x2e80 && code <= 0x303e) ||   // CJK Radicals, Kangxi, Symbols
    (code >= 0x3040 && code <= 0x33bf) ||   // Hiragana, Katakana, CJK Compat
    (code >= 0x3400 && code <= 0x4dbf) ||   // CJK Extension A
    (code >= 0x4e00 && code <= 0xa4cf) ||   // CJK Unified + Yi
    (code >= 0xac00 && code <= 0xd7a3) ||   // Hangul Syllables
    (code >= 0xf900 && code <= 0xfaff) ||   // CJK Compat Ideographs
    (code >= 0xfe30 && code <= 0xfe6f) ||   // CJK Compat Forms
    (code >= 0xff01 && code <= 0xff60) ||   // Fullwidth Latin
    (code >= 0xffe0 && code <= 0xffe6) ||   // Fullwidth Signs
    (code >= 0x20000 && code <= 0x2fa1f)    // CJK Extension B-F, Compat Supplement
  );
}

/** Calculate the display width of a string (CJK = 2, others = 1) */
function stringDisplayWidth(str) {
  let w = 0;
  for (const ch of str) {
    w += isFullWidth(ch) ? 2 : 1;
  }
  return w;
}

/** Calculate display width of a line's spans */
function lineDisplayWidth(spans) {
  return spans.reduce((acc, s) => acc + stringDisplayWidth(s.text), 0);
}

/**
 * Wrap a line's spans to fit within maxCols (in character units).
 * Returns an array of span-arrays, one per wrapped line.
 */
function wrapSpans(spans, maxCols) {
  if (lineDisplayWidth(spans) <= maxCols) return [spans];

  const wrappedLines = [];
  let currentLine = [];
  let currentWidth = 0;

  for (const span of spans) {
    const chars = [...span.text];
    let buf = "";
    let bufWidth = 0;

    for (const ch of chars) {
      const chW = isFullWidth(ch) ? 2 : 1;
      if (currentWidth + bufWidth + chW > maxCols) {
        // Flush buffer to current line
        if (buf) currentLine.push({ text: buf, color: span.color, bold: span.bold });
        wrappedLines.push(currentLine);
        currentLine = [];
        currentWidth = 0;
        buf = "";
        bufWidth = 0;
      }
      buf += ch;
      bufWidth += chW;
    }

    if (buf) {
      currentLine.push({ text: buf, color: span.color, bold: span.bold });
      currentWidth += bufWidth;
    }
  }

  if (currentLine.length > 0) wrappedLines.push(currentLine);
  return wrappedLines;
}

// ═══════════════════════════════════════════════════════════════════════
// Markdown Parser
// ═══════════════════════════════════════════════════════════════════════

function escapeXml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}

function parseMarkdown(text) {
  const rawLines = text.split("\n");
  const result = [];
  let inCodeBlock = false;

  for (const line of rawLines) {
    if (line.trimStart().startsWith("```")) {
      inCodeBlock = !inCodeBlock;
      result.push({ spans: [{ text: line, color: THEME.dim, bold: false }], isCode: true });
      continue;
    }

    if (inCodeBlock) {
      result.push({ spans: [{ text: line, color: THEME.codeFg, bold: false }], isCode: true });
      continue;
    }

    const headingMatch = line.match(/^(#{1,6})\s+(.*)/);
    if (headingMatch) {
      result.push({ spans: [{ text: line, color: THEME.heading, bold: true }], isCode: false });
      continue;
    }

    const bulletMatch = line.match(/^(\s*)([-*•])\s+(.*)/);
    if (bulletMatch) {
      const [, indent, bullet, rest] = bulletMatch;
      result.push({
        spans: [{ text: indent + bullet + " ", color: THEME.bullet, bold: false }, ...parseInline(rest)],
        isCode: false,
      });
      continue;
    }

    const numMatch = line.match(/^(\s*)(\d+\.)\s+(.*)/);
    if (numMatch) {
      const [, indent, num, rest] = numMatch;
      result.push({
        spans: [{ text: indent + num + " ", color: THEME.bullet, bold: false }, ...parseInline(rest)],
        isCode: false,
      });
      continue;
    }

    if (line.trim() === "") {
      result.push({ spans: [{ text: "", color: THEME.fg, bold: false }], isCode: false });
    } else {
      result.push({ spans: parseInline(line), isCode: false });
    }
  }
  return result;
}

function parseInline(text) {
  const spans = [];
  let i = 0;
  while (i < text.length) {
    if ((text[i] === "*" && text[i + 1] === "*") || (text[i] === "_" && text[i + 1] === "_")) {
      const marker = text.slice(i, i + 2);
      const end = text.indexOf(marker, i + 2);
      if (end !== -1) { spans.push({ text: text.slice(i + 2, end), color: THEME.bold, bold: true }); i = end + 2; continue; }
    }
    if (text[i] === "`") {
      const end = text.indexOf("`", i + 1);
      if (end !== -1) { spans.push({ text: text.slice(i, end + 1), color: THEME.code, bold: false }); i = end + 1; continue; }
    }
    if (text[i] === "[") {
      const cb = text.indexOf("]", i);
      if (cb !== -1 && text[cb + 1] === "(") {
        const cp = text.indexOf(")", cb + 2);
        if (cp !== -1) { spans.push({ text: text.slice(i + 1, cb), color: THEME.link, bold: false }); i = cp + 1; continue; }
      }
    }
    const start = i;
    while (i < text.length && text[i] !== "*" && text[i] !== "_" && text[i] !== "`" && text[i] !== "[") i++;
    if (i > start) spans.push({ text: text.slice(start, i), color: THEME.fg, bold: false });
  }
  if (spans.length === 0) spans.push({ text, color: THEME.fg, bold: false });
  return spans;
}

// ═══════════════════════════════════════════════════════════════════════
// SVG Renderer (Carbon/Ray.so style)
// ═══════════════════════════════════════════════════════════════════════

function textToSvg(text) {
  const fontSize = 14;
  const lineHeight = 22;
  const codePadX = 24;       // padding inside the card
  const codePadTop = 52;     // below title bar
  const codePadBottom = 24;
  const outerPad = 64;       // gradient background padding around card
  const cardRadius = 12;
  const titleBarH = 40;
  const dotR = 6;
  const dotStartX = 20;
  const dotSpacing = 20;
  const maxCols = 100;       // max characters per line before wrapping
  const charW = fontSize * 0.602;  // width of one character cell in px

  const rawLines = parseMarkdown(text);

  // Trim trailing empty lines
  while (rawLines.length > 0 && rawLines[rawLines.length - 1].spans.every((s) => s.text.trim() === "")) rawLines.pop();

  // Apply word wrap to all lines
  const lines = [];
  for (const line of rawLines) {
    const wrapped = wrapSpans(line.spans, maxCols);
    for (const wrappedSpans of wrapped) {
      lines.push({ spans: wrappedSpans, isCode: line.isCode });
    }
  }

  const maxDisplayW = Math.max(1, ...lines.map((l) => lineDisplayWidth(l.spans)));
  const contentW = Math.ceil(maxDisplayW * charW);

  const cardW = Math.max(400, contentW + codePadX * 2);
  const cardH = lines.length * lineHeight + codePadTop + codePadBottom;
  const totalW = cardW + outerPad * 2;
  const totalH = cardH + outerPad * 2;

  // 2x for retina
  const svgW = totalW * 2;
  const svgH = totalH * 2;

  let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${svgW}" height="${svgH}" viewBox="0 0 ${totalW} ${totalH}">\n`;

  // --- Defs: gradient background + card shadow ---
  svg += `  <defs>\n`;

  // Background gradient
  if (ACTIVE_BG.via) {
    svg += `    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">\n`;
    svg += `      <stop offset="0%" stop-color="${ACTIVE_BG.from}"/>\n`;
    svg += `      <stop offset="50%" stop-color="${ACTIVE_BG.via}"/>\n`;
    svg += `      <stop offset="100%" stop-color="${ACTIVE_BG.to}"/>\n`;
    svg += `    </linearGradient>\n`;
  } else {
    svg += `    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">\n`;
    svg += `      <stop offset="0%" stop-color="${ACTIVE_BG.from}"/>\n`;
    svg += `      <stop offset="100%" stop-color="${ACTIVE_BG.to}"/>\n`;
    svg += `    </linearGradient>\n`;
  }

  // Card drop shadow
  svg += `    <filter id="shadow" x="-15%" y="-10%" width="130%" height="130%">\n`;
  svg += `      <feDropShadow dx="0" dy="16" stdDeviation="28" flood-color="#000000" flood-opacity="0.5"/>\n`;
  svg += `    </filter>\n`;

  svg += `  </defs>\n`;

  // --- Layer 1: Gradient background ---
  svg += `  <rect width="${totalW}" height="${totalH}" fill="url(#bg-grad)"/>\n`;

  // --- Layer 2: Card with shadow ---
  svg += `  <rect x="${outerPad}" y="${outerPad}" width="${cardW}" height="${cardH}" rx="${cardRadius}" ry="${cardRadius}" fill="${THEME.cardBg}" filter="url(#shadow)"/>\n`;

  // --- Layer 3: Title bar ---
  // Title bar bg (top rounded, bottom flat)
  svg += `  <rect x="${outerPad}" y="${outerPad}" width="${cardW}" height="${titleBarH}" rx="${cardRadius}" ry="${cardRadius}" fill="${THEME.titleBar}"/>\n`;
  svg += `  <rect x="${outerPad}" y="${outerPad + cardRadius}" width="${cardW}" height="${titleBarH - cardRadius}" fill="${THEME.titleBar}"/>\n`;

  // Traffic lights
  const dotY = outerPad + titleBarH / 2;
  const dotBaseX = outerPad + dotStartX + dotR;
  svg += `  <circle cx="${dotBaseX}" cy="${dotY}" r="${dotR}" fill="${THEME.red}" stroke="${THEME.redStroke}" stroke-width="0.5"/>\n`;
  svg += `  <circle cx="${dotBaseX + dotSpacing}" cy="${dotY}" r="${dotR}" fill="${THEME.yellow}" stroke="${THEME.yellowStroke}" stroke-width="0.5"/>\n`;
  svg += `  <circle cx="${dotBaseX + dotSpacing * 2}" cy="${dotY}" r="${dotR}" fill="${THEME.green}" stroke="${THEME.greenStroke}" stroke-width="0.5"/>\n`;

  // --- Layer 4: Code/text content ---
  const textBaseX = outerPad + codePadX;
  const textBaseY = outerPad + codePadTop;

  svg += `  <style>\n`;
  svg += `    .code-text { font-family: Menlo, Monaco, 'Courier New', monospace; font-size: ${fontSize}px; white-space: pre; }\n`;
  svg += `    .b { font-weight: bold; }\n`;
  svg += `  </style>\n`;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const y = textBaseY + (i + 1) * lineHeight - (lineHeight - fontSize) / 2;

    svg += `  <text class="code-text" x="${textBaseX}" y="${y}" xml:space="preserve">`;
    for (const span of line.spans) {
      if (!span.text) continue;
      const boldCls = span.bold ? ' class="b"' : "";
      svg += `<tspan fill="${span.color}"${boldCls}>${escapeXml(span.text)}</tspan>`;
    }
    svg += `</text>\n`;
  }

  svg += `</svg>`;
  return svg;
}

// ═══════════════════════════════════════════════════════════════════════
// SVG → PNG
// ═══════════════════════════════════════════════════════════════════════

function findSystemFonts() {
  // Monospace fonts (primary) + CJK fallback fonts
  const candidates = process.platform === "darwin"
    ? [
        // Monospace (English)
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        "/System/Library/Fonts/Courier.ttc",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        // CJK fallback (Chinese/Japanese/Korean)
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
      ]
    : [
        // Monospace (English)
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
        // CJK fallback (Chinese/Japanese/Korean)
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
      ];
  const fontFiles = [];
  for (const p of candidates) { if (existsSync(p)) fontFiles.push(p); }
  return fontFiles;
}

function svgToPng(svg, fontFiles) {
  const resvg = new Resvg(svg, {
    font: {
      loadSystemFonts: false,
      fontFiles: fontFiles,
      defaultFontFamily: "Menlo",
      serifFamily: "Menlo",
      sansSerifFamily: "Menlo",
      monospaceFamily: "Menlo",
    },
  });
  return Buffer.from(resvg.render().asPng());
}

// ═══════════════════════════════════════════════════════════════════════
// Clipboard
// ═══════════════════════════════════════════════════════════════════════

function copyToClipboard(pngFilePath) {
  if (process.platform === "darwin") {
    const script = `set the clipboard to (read (POSIX file "${pngFilePath}") as \u00ABclass PNGf\u00BB)`;
    execSync(`osascript -e '${script}'`, { timeout: 10000 });
  } else if (process.platform === "linux") {
    try { execSync(`xclip -selection clipboard -t image/png -i "${pngFilePath}"`, { timeout: 10000 }); }
    catch { try { execSync(`xsel --clipboard --input < "${pngFilePath}"`, { timeout: 10000 }); }
    catch { throw new Error("No clipboard tool found. Install xclip or xsel:\n  sudo apt install xclip"); } }
  } else {
    throw new Error(`Unsupported platform: ${process.platform}. Only macOS and Linux are supported.`);
  }
}

// ═══════════════════════════════════════════════════════════════════════
// Main
// ═══════════════════════════════════════════════════════════════════════

async function main() {
  let text;
  const filePath = process.argv[2];
  if (filePath) {
    text = readFileSync(filePath, "utf-8");
  } else {
    const chunks = [];
    for await (const chunk of process.stdin) chunks.push(chunk);
    text = Buffer.concat(chunks).toString("utf-8");
  }

  if (!text.trim()) {
    console.error("Error: No input. Usage: node copy-as-image.mjs <file>  OR  echo 'text' | node copy-as-image.mjs");
    process.exit(1);
  }

  const svg = textToSvg(text);
  const fontFiles = findSystemFonts();
  const pngBuffer = svgToPng(svg, fontFiles);

  // Save PNG to a random temp file (kept for later use)
  const rand = Math.random().toString(36).slice(2, 10);
  const pngFile = join(tmpdir(), `claude-screenshot-${rand}.png`);
  writeFileSync(pngFile, pngBuffer);

  // Copy to clipboard
  try {
    copyToClipboard(pngFile);
    console.log(`Image copied to clipboard! (${pngBuffer.length} bytes)`);
    console.log(`PNG saved to: ${pngFile}`);
  } catch (err) {
    console.error(`Failed to copy to clipboard: ${err}`);
    console.log(`PNG saved to: ${pngFile}`);
    process.exit(1);
  }
}

main().catch((err) => { console.error(`Fatal error: ${err}`); process.exit(1); });
