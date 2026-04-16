#!/usr/bin/env node
/**
 * Markdown 字符串 → 完整 HTML 文档字符串（文艺复兴主题样式，与项目 themes.ts 对齐）
 * 用法:
 *   echo '# 标题' | node scripts/md_to_renaissance_html.mjs
 *   node scripts/md_to_renaissance_html.mjs --input ./article.md
 *   node scripts/md_to_renaissance_html.mjs --input ./article.md --title '我的文章'
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { marked } from 'marked';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = path.join(__dirname, '..');
const CSS_PATH = path.join(SKILL_ROOT, 'assets', 'renaissance.css');

function parseArgs(argv) {
  let inputPath = null;
  let title = 'Document';
  let embedImages = true;
  let copyButton = true;
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--input' && argv[i + 1]) {
      inputPath = argv[++i];
    } else if (a === '--title' && argv[i + 1]) {
      title = argv[++i];
    } else if (a === '--no-embed-images') {
      embedImages = false;
    } else if (a === '--no-copy-button') {
      copyButton = false;
    } else if (a === '--help' || a === '-h') {
      console.error(`Usage:
  stdin:  cat file.md | node scripts/md_to_renaissance_html.mjs [--title "标题"] [--no-embed-images] [--no-copy-button]
  file:   node scripts/md_to_renaissance_html.mjs --input file.md [--title "标题"] [--no-embed-images] [--no-copy-button]`);
      process.exit(0);
    }
  }
  return { inputPath, title, embedImages, copyButton };
}

function readMarkdown({ inputPath }) {
  if (inputPath) {
    return fs.readFileSync(path.resolve(inputPath), 'utf8');
  }
  try {
    return fs.readFileSync(0, 'utf8');
  } catch {
    return '';
  }
}

function escapeHtmlText(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function mimeFromPath(imagePath) {
  const ext = path.extname(imagePath).toLowerCase();
  if (ext === '.png') return 'image/png';
  if (ext === '.jpg' || ext === '.jpeg') return 'image/jpeg';
  if (ext === '.webp') return 'image/webp';
  if (ext === '.gif') return 'image/gif';
  if (ext === '.svg') return 'image/svg+xml';
  return 'application/octet-stream';
}

function sanitizeImageUrl(rawUrl) {
  let u = rawUrl.trim();
  if (u.startsWith('<') && u.endsWith('>')) {
    u = u.slice(1, -1).trim();
  }
  const firstSpace = u.search(/\s/);
  if (firstSpace !== -1) {
    u = u.slice(0, firstSpace);
  }
  return u;
}

function normalizeStrongInTextSegment(segment) {
  return segment.replace(/\*\*([^*\n]+?)\*\*/g, '<strong>$1</strong>');
}

function normalizeStrongMarkdown(markdown) {
  const lines = markdown.split('\n');
  let inFence = false;
  const out = [];

  for (const line of lines) {
    if (/^\s*```/.test(line)) {
      inFence = !inFence;
      out.push(line);
      continue;
    }
    if (inFence || !line.includes('**')) {
      out.push(line);
      continue;
    }

    // Avoid touching inline code: only normalize segments outside `...`
    const parts = line.split('`');
    for (let i = 0; i < parts.length; i += 2) {
      parts[i] = normalizeStrongInTextSegment(parts[i]);
    }
    out.push(parts.join('`'));
  }
  return out.join('\n');
}

async function toDataUrl(imageUrl, baseDir) {
  if (imageUrl.startsWith('data:')) {
    return imageUrl;
  }
  if (/^https?:\/\//i.test(imageUrl)) {
    const res = await fetch(imageUrl);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const arrayBuffer = await res.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    const contentType = res.headers.get('content-type') || '';
    const mime = contentType.split(';')[0].trim() || mimeFromPath(imageUrl);
    return `data:${mime};base64,${buffer.toString('base64')}`;
  }

  const localPath = path.isAbsolute(imageUrl)
    ? imageUrl
    : path.resolve(baseDir, imageUrl);
  const buffer = fs.readFileSync(localPath);
  const mime = mimeFromPath(localPath);
  return `data:${mime};base64,${buffer.toString('base64')}`;
}

async function embedImagesInMarkdown(markdown, inputPath) {
  const baseDir = inputPath
    ? path.dirname(path.resolve(inputPath))
    : process.cwd();
  const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
  const matches = [...markdown.matchAll(imageRegex)];
  if (matches.length === 0) {
    return markdown;
  }

  let output = markdown;
  for (const m of matches) {
    const alt = m[1];
    const rawUrl = m[2];
    const imageUrl = sanitizeImageUrl(rawUrl);
    try {
      const dataUrl = await toDataUrl(imageUrl, baseDir);
      const before = `![${alt}](${rawUrl})`;
      const after = `![${alt}](${dataUrl})`;
      output = output.replace(before, after);
    } catch (err) {
      console.error(`renaissance-md-html: 图片内嵌失败，保留原链接 -> ${imageUrl} (${err.message})`);
    }
  }
  return output;
}

function copyButtonStyles() {
  return `
.wmr-copy-btn {
  position: fixed;
  right: 16px;
  top: 16px;
  z-index: 9999;
  border: 0;
  border-radius: 999px;
  background: #6f4a2b;
  color: #fff8e8;
  padding: 8px 14px;
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.wmr-copy-btn:hover {
  background: #5d3d22;
}
`;
}

function addInlineStyleToTag(html, tag, styleText) {
  const openTagWithAttrs = new RegExp(`<${tag}(\\s+[^>]*?)>`, 'gi');
  const openTagNoAttrs = new RegExp(`<${tag}>`, 'gi');

  let output = html.replace(openTagWithAttrs, (m, attrs) => {
    if (/style\s*=/i.test(attrs)) {
      return m;
    }
    return `<${tag}${attrs} style="${styleText}">`;
  });
  output = output.replace(openTagNoAttrs, `<${tag} style="${styleText}">`);
  return output;
}

function applyWechatInlineStyles(html) {
  let output = html;
  output = addInlineStyleToTag(output, 'h1', 'font-size:1.5em;font-weight:800;color:#2c2c2c;margin:1.5em 0;line-height:1.4;text-align:center;');
  output = addInlineStyleToTag(output, 'h2', 'font-size:1.3em;font-weight:800;color:#2c2c2c;margin:1.4em 0 1em;line-height:1.4;padding-bottom:0.3em;text-align:left;');
  output = addInlineStyleToTag(output, 'h3', 'font-size:1.1em;font-weight:800;color:#4a4a4a;margin:1.2em 0 0.8em;line-height:1.4;');
  output = addInlineStyleToTag(output, 'h4', 'font-size:1em;font-weight:700;color:#444;margin:1em 0 0.5em;line-height:1.4;');
  output = addInlineStyleToTag(output, 'p', 'margin:0 0 1.2em;padding:0 12px;font-size:16px;line-height:1.75;color:#4a4a4a;');
  output = addInlineStyleToTag(output, 'a', 'color:#8b5a2b;text-decoration:none;font-size:12px;font-style:italic;');
  output = addInlineStyleToTag(output, 'strong', 'font-weight:700;color:#2c2c2c;');
  output = addInlineStyleToTag(output, 'blockquote', 'margin:1.5em 0;padding:0.8em 1em;border-left:3px solid #8b5a2b;background:#f8f5ef;color:#555;');
  output = addInlineStyleToTag(output, 'ul', 'margin:1em 0;padding-left:1.5em;');
  output = addInlineStyleToTag(output, 'ol', 'margin:1em 0;padding-left:1.5em;');
  output = addInlineStyleToTag(output, 'li', 'margin:0.4em 0;line-height:1.7;');
  output = addInlineStyleToTag(output, 'code', 'font-family:Menlo,Monaco,Consolas,"Courier New",monospace;background:#f6f2e9;color:#7a3e1d;padding:0.08em 0.3em;border-radius:3px;font-size:0.92em;');
  output = addInlineStyleToTag(output, 'pre', 'overflow-x:auto;padding:12px;background:#f6f2e9;border-radius:6px;line-height:1.5;');
  output = addInlineStyleToTag(output, 'img', 'display:block;max-width:100%;height:auto;margin:1.2em auto;border-radius:4px;');
  output = addInlineStyleToTag(output, 'hr', 'border:0;border-top:1px solid #d9c9a6;margin:2em 0;');
  output = addInlineStyleToTag(output, 'table', 'width:100%;border-collapse:collapse;margin:1em 0;font-size:14px;');
  output = addInlineStyleToTag(output, 'th', 'border:1px solid #d9c9a6;padding:8px;background:#f3ead9;text-align:left;');
  output = addInlineStyleToTag(output, 'td', 'border:1px solid #e4d8bf;padding:8px;');
  return output;
}

function copyButtonMarkup() {
  return `
  <button id="wmr-copy-btn" class="wmr-copy-btn" type="button">复制全文</button>
  <script>
    (function () {
      const btn = document.getElementById('wmr-copy-btn');
      const article = document.querySelector('article.wmr-renaissance');
      if (!btn || !article) return;
      const toPlainText = (html) => {
        const div = document.createElement('div');
        div.innerHTML = html;
        return div.innerText || div.textContent || '';
      };
      const copyBySelection = (node) => {
        const selection = window.getSelection();
        if (!selection) return false;
        const range = document.createRange();
        range.selectNodeContents(node);
        selection.removeAllRanges();
        selection.addRange(range);
        let ok = false;
        try {
          ok = document.execCommand('copy');
        } catch (_) {
          ok = false;
        }
        selection.removeAllRanges();
        return ok;
      };
      btn.addEventListener('click', async function () {
        if (copyBySelection(article)) {
          btn.textContent = '已复制';
          setTimeout(() => { btn.textContent = '复制全文'; }, 1200);
          return;
        }

        const html = article.outerHTML;
        const plain = toPlainText(html);
        try {
          if (window.ClipboardItem && navigator.clipboard && navigator.clipboard.write) {
            await navigator.clipboard.write([
              new ClipboardItem({
                'text/html': new Blob([html], { type: 'text/html' }),
                'text/plain': new Blob([plain], { type: 'text/plain' })
              })
            ]);
            btn.textContent = '已复制';
            setTimeout(() => { btn.textContent = '复制全文'; }, 1200);
            return;
          }
        } catch (_) {
          // continue to plain text fallback
        }
        const ta = document.createElement('textarea');
        ta.value = plain;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        btn.textContent = '已复制(纯文本)';
        setTimeout(() => { btn.textContent = '复制全文'; }, 1500);
      });
    })();
  </script>
`;
}

function buildDocument(markdown, title, options = {}) {
  const { copyButton = true } = options;
  const css = fs.readFileSync(CSS_PATH, 'utf8');
  marked.setOptions({
    gfm: true,
    breaks: false,
  });
  const normalizedMarkdown = normalizeStrongMarkdown(markdown);
  const bodyHtml = applyWechatInlineStyles(marked.parse(normalizedMarkdown));
  const safeTitle = escapeHtmlText(title);
  const articleInlineStyle = 'font-size:15px;color:#4a4a4a;line-height:1.6;letter-spacing:0.1em;word-wrap:break-word;box-sizing:border-box;text-align:justify;max-width:680px;margin:0 auto;padding:24px 16px;';

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${safeTitle}</title>
  <style>
${css}
${copyButton ? copyButtonStyles() : ''}
  </style>
</head>
<body>
  <article class="wmr-renaissance" style="${articleInlineStyle}">
${bodyHtml}
  </article>
${copyButton ? copyButtonMarkup() : ''}
</body>
</html>
`;
}

async function main() {
  const args = parseArgs(process.argv);
  const md = readMarkdown(args);
  if (!md.trim()) {
    console.error('renaissance-md-html: 未收到 Markdown（请通过 stdin 或 --input 传入）');
    process.exit(1);
  }

  const markdownForRender = args.embedImages
    ? await embedImagesInMarkdown(md, args.inputPath)
    : md;
  process.stdout.write(buildDocument(markdownForRender, args.title, { copyButton: args.copyButton }));
}

main().catch((err) => {
  console.error(`renaissance-md-html: 生成失败 (${err.message})`);
  process.exit(1);
});
