// =============================================================================
// Shixiang Tech (拾象科技) Brand Document Template (docx-js)
// Extracted from: shixiang-brand/shixiang-brand-doc-new/SKILL.md as a reference template.
//
// Brand: 拾象科技 / Shixiang Tech
// Brand Color: #A11F2A (deep red)
// Chinese Font: 楷体 (KaiTi)
// English Font: Times New Roman
// Page: A4
// Special: Mixed CN/EN font rendering via mixedRuns(), QR code footer block
// =============================================================================

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun,
  ImageRun, Header, AlignmentType, LevelFormat,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  VerticalAlign, TabStopType, TabStopPosition,
  Table, TableRow, TableCell
} = require("docx");

const BRAND_COLOR = "A11F2A";
const BRAND_MID   = "D4A0A3";
const BODY_FONT   = "楷体";
const ENG_FONT    = "Times New Roman";
const DARK_GRAY   = "555555";

// 字号常量（half-pts）
const SZ_DOC_TITLE = 36;  // 小二 18pt — 文档大标题（黑色）
const SZ_TITLE  = 32;  // 三号 16pt — H1
const SZ_H2     = 28;  // 四号 14pt — H2
const SZ_H3     = 26;  // 13pt — H3
const SZ_BODY   = 24;  // 小四 12pt — 正文 & 元信息（正文内所有内容统一小四）
const SZ_BULLET = 24;  // 小四 12pt — bullet 正文内容（与正文一致）
// 注：bullet 符号本身（Symbol \uf0b7）使用 SZ_BULLET_MARK=28，在 numberingConfig 中设置

const SKILL_DIR  = path.resolve(__dirname, "..");
const logoBuffer = fs.readFileSync(path.join(SKILL_DIR, "assets", "logo_header.png"));
const qrBuffer   = fs.readFileSync(path.join(SKILL_DIR, "assets", "qrcode.jpg"));  // 内置二维码，无需用户提供

// ── Bullet 符号说明 ──
// 使用 Symbol 字体的实心圆点（\uf0b7），与参考文档一致，视觉上比「·」更粗更醒目。
// bullet 符号字号设为 28 half-pts（比正文 24 稍大），使圆点视觉分量与正文匹配。
// 正文内容仍使用 SZ_BODY=24，仅 bullet 符号本身放大。
const BULLET_CHAR = "\uf0b7";  // Symbol font 实心圆点（对应 U+2022）
const SZ_BULLET_MARK = 28;     // bullet 符号字号（half-pts）；正文内容仍用 SZ_BODY=24

const numberingConfig = [
  {
    reference: "sx-bullets",
    levels: [{ level: 0, format: LevelFormat.BULLET, text: BULLET_CHAR, alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } },
               run: { color: BRAND_COLOR, font: "Symbol", size: SZ_BULLET_MARK } } }]
  },
  {
    reference: "sx-bullets-sub",
    levels: [{ level: 0, format: LevelFormat.BULLET, text: BULLET_CHAR, alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 1080, hanging: 360 } },
               run: { color: BRAND_COLOR, font: "Symbol", size: SZ_BULLET_MARK } } }]
  }
];

// ── Mixed CN/EN font rendering ──
// Splits text into Chinese and English segments, applying the correct font to each.
function mixedRuns(text, bold = false, color = "000000", size = SZ_BODY) {
  const segments = [];
  let cur = "", curType = null;
  for (const ch of text) {
    const isCN = /[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]/.test(ch);
    const type = isCN ? "cn" : "en";
    if (type !== curType) { if (cur) segments.push({ text: cur, type: curType }); cur = ch; curType = type; }
    else { cur += ch; }
  }
  if (cur) segments.push({ text: cur, type: curType });
  return segments.map(seg => new TextRun({ text: seg.text, font: seg.type === "cn" ? BODY_FONT : ENG_FONT, size, color, bold }));
}

// ── 大标题段落（纯文字，不含二维码）──
function titleParagraph(titleText) {
  return new Paragraph({
    spacing: { before: 240, after: 240, line: 360 },
    children: [
      ...mixedRuns(titleText, true, "000000", SZ_DOC_TITLE),
    ]
  });
}

// ── 文末二维码区块（文章最末尾，居中，inline，不遮挡正文）──
function qrFooterBlock() {
  return [
    new Paragraph({
      spacing: { before: 480, after: 80 },
      alignment: AlignmentType.CENTER,
      children: [
        new ImageRun({
          type: "jpg", data: qrBuffer,
          transformation: { width: 120, height: 118 },
          altText: { title: "二维码", description: "扫码关注", name: "qr" }
        })
      ]
    }),
    new Paragraph({
      spacing: { before: 0, after: 240 },
      alignment: AlignmentType.CENTER,
      children: mixedRuns("扫码关注\u201c海外独角兽\u201d，\n解锁更多深度报告", false, "555555", 20)
    })
  ];
}

// ── qrParagraph 已废弃，保留空函数避免旧代码报错 ──
function qrParagraph() {
  return new Paragraph({ spacing: { before: 0, after: 0 }, children: [] });
}

// ── To 行（无边框）──
function toLine(recipient = "Investment Team") {
  return new Paragraph({
    spacing: { before: 200, after: 200, line: 360 },
    children: [new TextRun({ text: `To:  ${recipient}`, font: ENG_FONT, size: SZ_BODY, color: "000000" })]
  });
}

// ── Date 行（底部黑色横线）──
function dateLine(dateStr) {
  return new Paragraph({
    spacing: { before: 200, after: 200, line: 360 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: "auto", space: 1 } },
    children: [new TextRun({ text: `Date: ${dateStr}`, font: ENG_FONT, size: SZ_BODY, color: "000000" })]
  });
}

function bodyPara(text, bold = false) {
  return new Paragraph({ spacing: { before: 80, after: 120, line: 390 }, children: mixedRuns(text, bold) });
}

function imageBlock(buf, origW, origH, type = "png", maxWidth = 460) {
  const scale = Math.min(maxWidth / origW, 1);
  return new Paragraph({
    spacing: { before: 100, after: 100 }, alignment: AlignmentType.CENTER,
    children: [new ImageRun({ type, data: buf,
      transformation: { width: Math.round(origW * scale), height: Math.round(origH * scale) },
      altText: { title: "figure", description: "figure", name: "figure" } })]
  });
}

// ── 品牌表格（第一行红底白字，其余所有行白底黑字）──
function brandedTable(headers, rows, colWidths) {
  const border = { style: BorderStyle.SINGLE, size: 1, color: BRAND_MID };
  const borders = { top: border, bottom: border, left: border, right: border };
  const headerRow = new TableRow({
    children: headers.map((h, i) => new TableCell({
      borders, width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: BRAND_COLOR, type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 120, right: 120 }, verticalAlign: VerticalAlign.CENTER,
      children: [new Paragraph({ children: mixedRuns(h, true, "FFFFFF", SZ_BODY) })]
    }))
  });
  const bodyRows = rows.map(row => new TableRow({
    children: row.map((cell, ci) => new TableCell({
      borders, width: { size: colWidths[ci], type: WidthType.DXA },
      shading: { fill: "FFFFFF", type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({ spacing: { line: 360 }, children: mixedRuns(String(cell), false, "000000", SZ_BODY) })]
    }))
  }));
  return new Table({
    width: { size: colWidths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: colWidths, rows: [headerRow, ...bodyRows]
  });
}

// ── Heading helpers ──
function h1(num, text) {
  // num: Roman numeral string, e.g. "I", "II", "III"...
  return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 480, after: 280 },
    children: mixedRuns(`${num}.  ${text}`, true, BRAND_COLOR, SZ_TITLE) });
}
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 360, after: 200 },
    children: mixedRuns(text, true, BRAND_COLOR, SZ_H2) });
}
function h3(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 260, after: 160 },
    children: mixedRuns(text, true, BRAND_COLOR, SZ_H3) });
}
function bulletPara(text, bold = false, sub = false) {
  return new Paragraph({ numbering: { reference: sub ? "sx-bullets-sub" : "sx-bullets", level: 0 },
    spacing: { before: 80, after: 80, line: 390 }, children: mixedRuns(text, bold, "000000", SZ_BULLET) });
}
function highlightPara(text) {
  return new Paragraph({ spacing: { before: 100, after: 100, line: 390 }, indent: { left: 400 },
    border: { left: { style: BorderStyle.SINGLE, size: 8, color: BRAND_COLOR, space: 12 } },
    children: mixedRuns(text, false, DARK_GRAY) });
}

// ── Build document ──
const doc = new Document({
  styles: {
    default: { document: { run: { font: BODY_FONT, size: SZ_BODY, color: "000000" } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: SZ_TITLE, bold: true, font: BODY_FONT, color: BRAND_COLOR },
        paragraph: { spacing: { before: 480, after: 280 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: SZ_H2, bold: true, font: BODY_FONT, color: BRAND_COLOR },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: SZ_H3, bold: true, font: BODY_FONT, color: BRAND_COLOR },
        paragraph: { spacing: { before: 260, after: 160 }, outlineLevel: 2 } },
    ]
  },
  numbering: { config: numberingConfig },
  sections: [{
    properties: {
      page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1829, right: 1829 } }
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            // No border -- header has no underline
            children: [
              new TextRun("\t"),
              new ImageRun({ type: "png", data: logoBuffer, transformation: { width: 110, height: 35 },
                altText: { title: "拾象科技", description: "Shixiang Tech Logo", name: "logo" } })
            ],
            tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
          })
        ]
      })
    },
    children: [
      titleParagraph("文档标题"),   // Large title (plain text, no QR code)
      toLine("Investment Team"),
      dateLine("2026-Mar."),
      // ... body content goes here ...
      // QR code block at the very end
      ...qrFooterBlock(),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/claude/output.docx", buffer);
  console.log("Document generated successfully");
});
