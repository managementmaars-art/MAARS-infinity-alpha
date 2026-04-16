// =============================================================================
// Etna Labs Brand Document Template (docx-js)
// Extracted from: etna-memo/etna-brand-doc/SKILL.md as a reference template.
//
// Brand: Etna Labs
// Brand Color: #C45A48 (warm terracotta red)
// Slogan: Deep Conviction. Long View.
// Body Font: Times New Roman, 12pt
// Title Font: Anonymous Pro
// Page: US Letter, English only
// =============================================================================

const fs = require("fs");
const path = require("path");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        ImageRun, Header, Footer, AlignmentType, LevelFormat,
        HeadingLevel, BorderStyle, WidthType, ShadingType,
        VerticalAlign, PageNumber, TabStopType, TabStopPosition,
        PageBreak } = require("docx");

// ── Brand constants ──
const BRAND_COLOR = "C45A48";
const BRAND_LIGHT = "F5EFEE";
const BRAND_MID   = "D4A59E";
const BODY_FONT   = "Times New Roman";
const TITLE_FONT  = "Anonymous Pro";
const SLOGAN      = "Deep Conviction. Long View.";
const DARK_GRAY   = "555555";

// ── Load logo ──
const SKILL_DIR = path.resolve(__dirname, "..");  // adjust if script location differs
const logoPath = path.join(SKILL_DIR, "assets", "logo_header.png");
const logoBuffer = fs.readFileSync(logoPath);

// ── Date string ──
const now = new Date();
const months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
const dateStr = `${months[now.getMonth()]} ${now.getDate()}, ${now.getFullYear()}`;

// ── H2 Roman numeral counter ──
function h2(text) {
  h2._count = (h2._count || 0) + 1;
  const romans = ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV"];
  const prefix = romans[h2._count - 1] || h2._count;
  return new Paragraph({ heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text: `${prefix}. ${text}`, bold: true, font: TITLE_FONT, size: 32, color: BRAND_COLOR })]
  });
}

// ── Numbering config (brand-colored bullets and numbers) ──
const numberingConfig = [
  {
    reference: "etna-bullets",
    levels: [{
      level: 0,
      format: LevelFormat.BULLET,
      text: "\u2022",
      alignment: AlignmentType.LEFT,
      style: {
        paragraph: { indent: { left: 720, hanging: 360 } },
        run: { color: BRAND_COLOR }
      }
    }]
  },
  {
    reference: "etna-numbers",
    levels: [{
      level: 0,
      format: LevelFormat.DECIMAL,
      text: "%1.",
      alignment: AlignmentType.LEFT,
      style: {
        paragraph: { indent: { left: 720, hanging: 360 } },
        run: { color: BRAND_COLOR }
      }
    }]
  }
];

// ── Branded table builder ──
function createBrandedTable(headers, rows, columnWidths) {
  const border = { style: BorderStyle.SINGLE, size: 1, color: BRAND_MID };
  const borders = { top: border, bottom: border, left: border, right: border };
  const totalWidth = columnWidths.reduce((a,b) => a+b, 0);

  const headerRow = new TableRow({
    children: headers.map((h, i) => new TableCell({
      borders,
      width: { size: columnWidths[i], type: WidthType.DXA },
      shading: { fill: BRAND_COLOR, type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      verticalAlign: VerticalAlign.CENTER,
      children: [new Paragraph({
        children: [new TextRun({ text: h, bold: true, color: "FFFFFF", font: BODY_FONT, size: 22 })]
      })]
    }))
  });

  const bodyRows = rows.map((row, ri) => new TableRow({
    children: row.map((cell, ci) => new TableCell({
      borders,
      width: { size: columnWidths[ci], type: WidthType.DXA },
      shading: ri % 2 === 1 ? { fill: BRAND_LIGHT, type: ShadingType.CLEAR } : undefined,
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({
        children: [new TextRun({ text: String(cell), font: BODY_FONT, size: 22 })]
      })]
    }))
  }));

  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths,
    rows: [headerRow, ...bodyRows]
  });
}

// ── Build document ──
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: BODY_FONT, size: 24, color: "000000" }
      }
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1",
        basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 44, bold: true, font: TITLE_FONT, color: BRAND_COLOR },
        paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2",
        basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: TITLE_FONT, color: BRAND_COLOR },
        paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 1 }
      },
      {
        id: "Heading3", name: "Heading 3",
        basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: BODY_FONT, color: BRAND_COLOR },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 2 }
      },
    ]
  },
  numbering: { config: numberingConfig },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },  // US Letter
        margin: { top: 1800, bottom: 1440, left: 1440, right: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            children: [
              new TextRun({ text: SLOGAN, font: BODY_FONT, size: 16, color: DARK_GRAY, italics: true }),
              new TextRun({ text: "  |  etnalabs.co", font: BODY_FONT, size: 16, color: DARK_GRAY }),
              new TextRun("\t"),
              new ImageRun({
                type: "png",
                data: logoBuffer,
                transformation: { width: 109, height: 30 },
                altText: { title: "Etna Labs", description: "Etna Labs Logo", name: "logo" }
              })
            ],
            tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
            border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: BRAND_COLOR, space: 6 } }
          })
        ]
      })
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            border: { top: { style: BorderStyle.SINGLE, size: 4, color: BRAND_COLOR, space: 6 } },
            children: [
              new TextRun({ text: dateStr, font: BODY_FONT, size: 16, color: DARK_GRAY }),
              new TextRun("\t"),
              new TextRun({ text: "Confidential", font: BODY_FONT, size: 16, color: DARK_GRAY })
            ],
            tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }]
          })
        ]
      })
    },
    children: [
      // ── Main title ──
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 100, after: 120 },
        children: [new TextRun({ text: "Document Title", bold: true, font: TITLE_FONT, size: 44, color: BRAND_COLOR })]
      }),
      // ── From block ──
      new Paragraph({
        spacing: { after: 300 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: "D4A59E", space: 8 } },
        children: [
          new TextRun({ text: "From: ", bold: true, font: BODY_FONT, size: 22, color: DARK_GRAY }),
          new TextRun({ text: "Etna Labs", font: BODY_FONT, size: 22, color: DARK_GRAY }),
        ]
      }),
      // ── Body content goes here ──
      new Paragraph({
        spacing: { after: 200, line: 360 },
        children: [new TextRun({ text: "Body content...", font: BODY_FONT, size: 24 })]
      }),
    ]
  }]
});

// ── Write file ──
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/claude/output.docx", buffer);
  console.log("DOCX created successfully");
});
