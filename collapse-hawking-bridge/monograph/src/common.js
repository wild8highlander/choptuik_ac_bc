// common.js — shared builder for the monograph volumes (RU/EN).
// Ink & Gold identity (IG-1), R2 double-rule cover, 3-section page
// numbering (cover / front matter Roman / body Arabic), TOC field,
// zebra tables, PNG embedding with exact aspect ratio.
"use strict";
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, PageBreak, Header, Footer, PageNumber, NumberFormat,
  AlignmentType, HeadingLevel, WidthType, BorderStyle, ShadingType,
  TableLayoutType, SectionType, TableOfContents, LevelFormat,
  Math: OoxmlMath, MathRun, MathFraction, MathSuperScript, MathSubScript,
  MathSubSuperScript, MathRadical,
} = require("docx");

// ---- palette: IG-1 Ink Gold -------------------------------------------------
const PAL = {
  bg: "1A1A1A", accent: "C9A84C",
  cover: { titleColor: "FFFFFF", subtitleColor: "B0B8C0", metaColor: "90989F", footerColor: "687078" },
  table: { headerBg: "C9A84C", headerText: "1A1A1A", accentLine: "C9A84C", innerLine: "DDD5C0", surface: "F5F2E8" },
  ink: "1A1A1A", secondary: "505050",
};

const FONT = "Times New Roman";
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const allNoBorders = {
  top: noBorder, bottom: noBorder, left: noBorder, right: noBorder,
  insideHorizontal: noBorder, insideVertical: noBorder,
};

// ---- cover title layout (design-system.md, word-boundary variant) -----------
function splitTitleLines(title, charsPerLine) {
  if (title.length <= charsPerLine) return [title];
  const words = title.split(" ");
  const lines = [];
  let cur = "";
  for (const w of words) {
    if ((cur + (cur ? " " : "") + w).length > charsPerLine && cur) {
      lines.push(cur); cur = w;
    } else {
      cur += (cur ? " " : "") + w;
    }
  }
  if (cur) lines.push(cur);
  if (lines.length > 1 && lines[lines.length - 1].length <= 4) {
    const last = lines.pop();
    lines[lines.length - 1] += " " + last;
  }
  return lines;
}

function calcTitleLayout(title, maxWidthTwips, preferredPt = 40, minPt = 24) {
  // Latin/Cyrillic chars are ~0.55x CJK width; use pt*11 per char
  const charWidth = (pt) => pt * 11;
  const charsPerLine = (pt) => Math.floor(maxWidthTwips / charWidth(pt));
  let titlePt = preferredPt, lines;
  while (titlePt >= minPt) {
    const cpl = charsPerLine(titlePt);
    if (cpl < 2) { titlePt -= 2; continue; }
    lines = splitTitleLines(title, cpl);
    if (lines.length <= 3) break;
    titlePt -= 2;
  }
  if (!lines || lines.length > 3) {
    lines = splitTitleLines(title, charsPerLine(minPt));
    titlePt = minPt;
  }
  return { titlePt, titleLines: lines };
}

function calcCoverSpacing(params) {
  const { titleLineCount = 1, titlePt = 36, hasSubtitle = false,
          hasEnglishLabel = false, metaLineCount = 0,
          fixedHeight = 800, pageHeight = 16838,
          marginTop = 0, marginBottom = 0 } = params;
  const SAFETY = 1200;
  const usableHeight = pageHeight - marginTop - marginBottom - SAFETY;
  const titleHeight = titleLineCount * (titlePt * 23 + 200);
  const subtitleHeight = hasSubtitle ? (12 * 23 + 600) : 0;
  const englishLabelHeight = hasEnglishLabel ? (9 * 23 + 600) : 0;
  const metaHeight = metaLineCount * (10 * 23 + 100);
  const implicitParaHeight = 3 * 300;
  const contentHeight = titleHeight + subtitleHeight + englishLabelHeight +
                        metaHeight + fixedHeight + implicitParaHeight;
  const remainingSpace = usableHeight - contentHeight;
  const safeRemaining = Math.max(remainingSpace, 400);
  const FOOTER_MIN = 800;
  const rawTop = Math.floor(safeRemaining * 0.45);
  const rawBottom = Math.floor(safeRemaining * 0.45);
  const bottomSpacing = Math.max(rawBottom, FOOTER_MIN);
  const topSpacing = Math.max(rawTop - Math.max(0, FOOTER_MIN - rawBottom), 400);
  const midSpacing = Math.max(safeRemaining - topSpacing - bottomSpacing, 0);
  return { topSpacing, midSpacing, bottomSpacing };
}

// ---- Recipe R2: Double-Rule Frame (centered) --------------------------------
function buildCoverR2(config) {
  const P = PAL.cover;
  const padL = 1400, padR = 1400;
  const { titlePt, titleLines } = calcTitleLayout(config.title, 11906 - padL - padR, 40, 24);
  const titleSize = titlePt * 2;
  const thickBorder = { style: BorderStyle.SINGLE, size: 18, color: PAL.accent, space: 20 };
  const children = [];
  children.push(new Paragraph({
    indent: { left: padL - 400, right: padR - 400 }, spacing: { before: 1200, after: 200 },
    border: { top: thickBorder }, children: [],
  }));
  children.push(new Paragraph({ spacing: { before: 1800 } }));
  if (config.englishLabel) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 500 },
      children: [new TextRun({ text: config.englishLabel.split("").join("  "),
        size: 18, color: PAL.accent, font: { ascii: "Calibri", hAnsi: "Calibri" }, characterSpacing: 40 })],
    }));
  }
  for (let i = 0; i < titleLines.length; i++) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: i < titleLines.length - 1 ? 80 : 300,
                 line: Math.ceil(titlePt * 23), lineRule: "atLeast" },
      children: [new TextRun({ text: titleLines[i], size: titleSize, bold: true,
        color: P.titleColor, font: { ascii: FONT, hAnsi: FONT } })],
    }));
  }
  if (config.subtitle) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 800, line: 340, lineRule: "atLeast" },
      children: [new TextRun({ text: config.subtitle, size: 24, color: P.subtitleColor,
        font: { ascii: FONT, hAnsi: FONT } })],
    }));
  }
  children.push(new Paragraph({ spacing: { before: 600 } }));
  for (const line of (config.metaLines || [])) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 120 },
      children: [new TextRun({ text: line, size: 26, color: P.metaColor,
        font: { ascii: FONT, hAnsi: FONT } })],
    }));
  }
  children.push(new Paragraph({ spacing: { before: 1400 } }));
  children.push(new Paragraph({
    indent: { left: padL - 400, right: padR - 400 },
    border: { bottom: thickBorder }, spacing: { before: 200, after: 120 },
    children: [],
  }));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 120 },
    children: [new TextRun({ text: config.footerLine || "", size: 18, color: P.footerColor,
      font: { ascii: FONT, hAnsi: FONT } })],
  }));
  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      height: { value: 16838, rule: "exact" },
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: PAL.bg }, borders: allNoBorders,
        children,
      })],
    })],
  })];
}

// ---- body builders -----------------------------------------------------------
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 400, after: 180, line: 400, lineRule: "atLeast" },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: PAL.accent, space: 6 } },
    children: [new TextRun({ text, bold: true, size: 32, color: PAL.ink, font: FONT })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 120, line: 360, lineRule: "atLeast" },
    children: [new TextRun({ text, bold: true, size: 28, color: PAL.ink, font: FONT })],
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 220, after: 100, line: 330, lineRule: "atLeast" },
    children: [new TextRun({ text, bold: true, size: 24, color: PAL.ink, font: FONT })],
  });
}
// body paragraph; parts: string or {t, b(old), i(talic), sup, sub}
function body(parts, opts = {}) {
  const arr = Array.isArray(parts) ? parts : [parts];
  const runs = arr.map((p) => {
    if (typeof p === "string") {
      return new TextRun({ text: p, size: 24, color: "000000", font: FONT });
    }
    return new TextRun({
      text: p.t, bold: !!p.b, italics: !!p.i, size: p.size || 24,
      superScript: !!p.sup, subScript: !!p.sub,
      color: p.color || "000000", font: FONT,
    });
  });
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    indent: opts.noIndent ? undefined : { firstLine: opts.firstLine ?? 0 },
    spacing: { line: 312, after: opts.after ?? 120 },
    children: runs,
  });
}
function bullet(text, level = 0) {
  return new Paragraph({
    bullet: { level },
    alignment: AlignmentType.LEFT,
    spacing: { line: 312, after: 60 },
    children: [new TextRun({ text, size: 24, color: "000000", font: FONT })],
  });
}
// statement box (theorem statement) — gold left bar, surface fill
function statementBox(label, runsOrText) {
  const arr = Array.isArray(runsOrText) ? runsOrText : [runsOrText];
  const runs = [new TextRun({ text: label + "  ", bold: true, size: 24, color: PAL.ink, font: FONT })]
    .concat(arr.map((p) => typeof p === "string"
      ? new TextRun({ text: p, size: 24, color: "000000", font: FONT, italics: true })
      : new TextRun({ text: p.t, bold: !!p.b, italics: p.i !== false, size: 24,
                      superScript: !!p.sup, subScript: !!p.sub, color: "000000", font: FONT })));
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    shading: { type: ShadingType.CLEAR, fill: PAL.table.surface },
    border: {
      left: { style: BorderStyle.SINGLE, size: 12, color: PAL.accent, space: 10 },
      top: { style: BorderStyle.SINGLE, size: 1, color: PAL.table.innerLine, space: 4 },
      bottom: { style: BorderStyle.SINGLE, size: 1, color: PAL.table.innerLine, space: 4 },
    },
    spacing: { line: 312, before: 160, after: 160 },
    indent: { left: 200, right: 120 },
    children: runs,
  });
}
function caption(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 60, after: 200 },
    children: [new TextRun({ text, size: 20, color: PAL.secondary, italics: true, font: FONT })],
  });
}
function pngSize(p) {
  const b = fs.readFileSync(p);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
function figure(absPath, widthPx = 580) {
  const { w, h } = pngSize(absPath);
  const height = Math.round(widthPx * h / w);
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 160, after: 40 },
    children: [new ImageRun({
      data: fs.readFileSync(absPath),
      transformation: { width: widthPx, height },
      type: "png",
    })],
  });
}
function dataTable({ headers, rows, widths, fontSize = 20, alignRight = [] }) {
  const n = headers.length;
  const w = widths || Array(n).fill(Math.floor(100 / n));
  const mkCell = (content, isHeader, colIdx, rowIdx) => new TableCell({
    width: { size: w[colIdx], type: WidthType.PERCENTAGE },
    shading: isHeader
      ? { type: ShadingType.CLEAR, fill: PAL.table.headerBg }
      : (rowIdx % 2 === 1 ? { type: ShadingType.CLEAR, fill: PAL.table.surface } : undefined),
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({
      alignment: (!isHeader && alignRight.includes(colIdx)) ? AlignmentType.RIGHT
               : AlignmentType.CENTER,
      spacing: { line: 276 },
      children: [new TextRun({
        text: String(content), bold: isHeader, size: fontSize,
        color: isHeader ? PAL.table.headerText : "000000", font: FONT,
      })],
    })],
  });
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 6, color: PAL.table.accentLine },
      bottom: { style: BorderStyle.SINGLE, size: 6, color: PAL.table.accentLine },
      left: noBorder, right: noBorder,
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: PAL.table.innerLine },
      insideVertical: noBorder,
    },
    rows: [
      new TableRow({ tableHeader: true, cantSplit: true,
        children: headers.map((h, j) => mkCell(h, true, j, -1)) }),
      ...rows.map((r, i) => new TableRow({ cantSplit: true,
        children: r.map((cell, j) => mkCell(cell, false, j, i)) })),
    ],
  });
}
function tableTitle(text) {
  return new Paragraph({
    keepNext: true,
    spacing: { before: 200, after: 80 },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text, bold: true, size: 21, color: PAL.ink, font: FONT })],
  });
}
// math helpers
const mR = (t) => new MathRun(t);
function mathPara(children, numbered = null) {
  const kids = [new OoxmlMath({ children })];
  if (numbered) kids.push(new TextRun({ text: "   " + numbered, size: 20, color: PAL.secondary, font: FONT }));
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 140, line: 360, lineRule: "atLeast" },
    children: kids,
  });
}
const mFrac = (num, den) => new MathFraction({ numerator: num, denominator: den });
const mSup = (base, s) => new MathSuperScript({ children: base, superScript: s });
const mSub = (base, s) => new MathSubScript({ children: base, subScript: s });

// ---- assembly ----------------------------------------------------------------
function pageNumFooter() {
  return new Footer({ children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: PAL.secondary, font: FONT })],
  })] });
}
function runningHeader(text) {
  return new Header({ children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: PAL.table.innerLine, space: 4 } },
    children: [new TextRun({ text, size: 18, color: PAL.secondary, italics: true, font: FONT })],
  })] });
}

async function assemble({ coverConfig, tocTitle, refreshHint, headerText, bodyChildren, outPath }) {
  const pgSize = { width: 11906, height: 16838 };
  const pgMargin = { top: 1440, bottom: 1440, left: 1701, right: 1417 };
  const doc = new Document({
    creator: "Z.ai",
    title: coverConfig.title,
    description: coverConfig.subtitle,
    styles: {
      default: {
        document: {
          run: { font: { ascii: FONT, hAnsi: FONT }, size: 24, color: "000000" },
          paragraph: { spacing: { line: 312 } },
        },
        heading1: { run: { font: { ascii: FONT, hAnsi: FONT }, size: 32, bold: true, color: PAL.ink },
                    paragraph: { spacing: { before: 400, after: 180 }, outlineLevel: 0 } },
        heading2: { run: { font: { ascii: FONT, hAnsi: FONT }, size: 28, bold: true, color: PAL.ink },
                    paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
        heading3: { run: { font: { ascii: FONT, hAnsi: FONT }, size: 24, bold: true, color: PAL.ink },
                    paragraph: { spacing: { before: 220, after: 100 }, outlineLevel: 2 } },
      },
    },
    sections: [
      { // 1. cover — margin 0, no footer/header
        properties: { page: { size: pgSize, margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
        children: buildCoverR2(coverConfig),
      },
      { // 2. front matter — Roman numerals
        properties: {
          type: SectionType.NEXT_PAGE,
          page: { size: pgSize, margin: pgMargin,
                  pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN } },
        },
        headers: { default: runningHeader(headerText) },
        footers: { default: pageNumFooter() },
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 480, after: 360, line: 400, lineRule: "atLeast" },
            children: [new TextRun({ text: tocTitle, bold: true, size: 32, font: FONT, color: PAL.ink })],
          }),
          new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
          new Paragraph({
            spacing: { before: 200 },
            children: [new TextRun({ text: refreshHint, italics: true, size: 18, color: "888888", font: FONT })],
          }),
          new Paragraph({ children: [new PageBreak()] }),
        ],
      },
      { // 3. body — Arabic from 1
        properties: {
          type: SectionType.NEXT_PAGE,
          page: { size: pgSize, margin: pgMargin,
                  pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } },
        },
        headers: { default: runningHeader(headerText) },
        footers: { default: pageNumFooter() },
        children: bodyChildren,
      },
    ],
  });
  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(outPath, buf);
  console.log("wrote", outPath, Math.round(buf.length / 1024) + " KB");
}

module.exports = {
  PAL, FONT, allNoBorders,
  h1, h2, h3, body, bullet, statementBox, caption, figure, pngSize,
  dataTable, tableTitle, mathPara, mR, mFrac, mSup, mSub,
  assemble, buildCoverR2,
};
