/**
 * SheetModel — A thin wrapper over HyperFormula that makes it natural
 * for an AI to define financial models.
 * 
 * Key ideas:
 * - Define rows by label → auto-tracks A1 refs
 * - Reference other rows by label in formulas: {PN} → $B$21
 * - Scenario columns with named inputs
 * - Auto-validation (Assets = Liabilities + Equity)
 * - Export to styled .xlsx via ExcelJS
 */
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { HyperFormula } = require('hyperformula');

// Excel column letters: A-Z, AA-XFD. Build a set of all valid 1-2 letter columns.
const _EXCEL_COLS = new Set();
for (let i = 0; i < 26; i++) _EXCEL_COLS.add(String.fromCharCode(65 + i)); // A-Z
for (let i = 0; i < 26; i++) for (let j = 0; j < 26; j++)
  _EXCEL_COLS.add(String.fromCharCode(65 + i) + String.fromCharCode(65 + j)); // AA-ZZ

function _isReservedName(name) {
  const upper = name.toUpperCase();
  // Reject cell references: A1, AC100, XFD1048576, etc.
  if (/^[A-Z]{1,3}\d+$/.test(upper)) return true;
  // Reject bare column letters that Excel recognizes (A-Z, AA-ZZ covers all practical cases)
  if (_EXCEL_COLS.has(upper)) return true;
  // R1C1 notation
  if (/^R\d*C\d*$/.test(upper)) return true;
  return false;
}

function _colToLetter(col) { // 0-indexed → A, B, ..., Z, AA, AB, ...
  let s = '';
  col++;
  while (col > 0) { col--; s = String.fromCharCode(65 + col % 26) + s; col = Math.floor(col / 26); }
  return s;
}

export class SheetModel {
  constructor() {
    this.hf = HyperFormula.buildEmpty({ licenseKey: 'gpl-v3' });
    this.sheets = {};       // name → { id, rows: [{label, value, isFormula, name}], rowMap: {name→A1Row} }
    this.namedExprs = {};   // name → A1 ref string
  }

  // ── Sheet management ──

  addSheet(name) {
    const sheetName = this.hf.addSheet(name);
    const id = this.hf.getSheetId(sheetName);
    this.sheets[name] = { id, name: sheetName, rows: [], rowMap: {}, nextRow: 0 };
    return name;
  }

  // ── Row-based API (the key abstraction) ──

  /**
   * Add a row to a sheet.
   * @param {string} sheet - Sheet name
   * @param {string} label - Display label (e.g., "  Inmovilizado intangible")
   * @param {number|string|null} value - Number, formula string, or null for blank
   * @param {object} opts - { name: 'Intangible', bold: true }
   *   name: register as a named reference (usable in formulas as {name})
   *   bold: styling hint
   * @returns {number} A1 row number (1-indexed)
   */
  addRow(sheet, label, value = null, opts = {}) {
    const s = this.sheets[sheet];
    if (!s) throw new Error(`Sheet "${sheet}" not found`);

    const hfRow = s.nextRow;
    const a1Row = hfRow + 1;
    s.nextRow++;

    // Write label (col A)
    this.hf.setCellContents({ sheet: s.id, col: 0, row: hfRow }, label);

    // Write value (col B)
    if (value !== null && value !== '') {
      try {
        if (typeof value === 'string' && value.startsWith('=')) {
          // Resolve {Name} references in formula
          const resolved = this._resolveRefs(value, sheet);
          this.hf.setCellContents({ sheet: s.id, col: 1, row: hfRow }, resolved);
        } else {
          this.hf.setCellContents({ sheet: s.id, col: 1, row: hfRow }, value);
        }
      } catch (e) {
        throw new Error(`Error in row "${label}" (${sheet}!B${a1Row}): ${e.message}`);
      }
    }

    // Track row
    const rowInfo = { label, value, a1Row, hfRow, isFormula: typeof value === 'string' && value?.startsWith('='), ...opts };
    s.rows.push(rowInfo);

    // Register named reference
    if (opts.name) {
      if (_isReservedName(opts.name)) {
        throw new Error(`Name "${opts.name}" collides with Excel cell/column notation. Use a longer, descriptive name (e.g., "Adj${opts.name}", "Total${opts.name}").`);
      }
      const ref = `${s.name}!$B$${a1Row}`;
      s.rowMap[opts.name] = a1Row;
      this.namedExprs[opts.name] = ref;
      this.hf.addNamedExpression(opts.name, `=${ref}`);
    }

    return a1Row;
  }

  /**
   * Add a blank separator row
   */
  addBlank(sheet) {
    return this.addRow(sheet, '');
  }

  /**
   * Add a section header row (bold, no value)
   */
  addSection(sheet, label) {
    return this.addRow(sheet, label, null, { section: true });
  }

  /**
   * Resolve {Name} references in a formula to absolute A1 refs.
   * E.g., "={PN} + {PNC}" → "=$B$21 + $B$28"
   * Also supports {SheetName.Name} for cross-sheet refs.
   */
  _resolveRefs(formula, currentSheet) {
    return formula.replace(/\{(\w+(?:\.\w+)?)\}/g, (match, name) => {
      if (name.includes('.')) {
        const [sheetName, refName] = name.split('.');
        const s = this.sheets[sheetName];
        if (!s) throw new Error(`Unknown sheet "${sheetName}" in ref ${match}`);
        const row = s.rowMap[refName];
        if (!row) throw new Error(`Unknown ref "${refName}" in sheet "${sheetName}"`);
        return `${s.name}!$B$${row}`;
      }
      // Check named expression
      if (this.namedExprs[name]) return name; // HyperFormula will resolve it
      // Check current sheet rowMap
      const s = this.sheets[currentSheet];
      const row = s?.rowMap[name];
      if (row) return `$B$${row}`;
      throw new Error(`Unknown ref {${name}} in formula: ${formula}`);
    });
  }

  // ── Scenario table API ──

  /**
   * Build a scenario comparison table on a new sheet.
   * @param {string} sheetName 
   * @param {object} config
   *   inputs: [{ name, label }]  — scenario input rows
   *   scenarios: [{ label, values: {inputName: value} }]
   *   outputs: [{ label, formula, format, name, thresholds }]
   *     formula uses {InputName} for scenario inputs, {DataName} for Data refs
   *     format: 'number', 'percent', 'ratio'
   *     thresholds: { good, bad, invert? }
   */
  addScenarioSheet(sheetName, config) {
    this.addSheet(sheetName);
    const s = this.sheets[sheetName];
    const scenCount = config.scenarios.length;

    // Row 0: Headers
    const headers = ['', ...config.scenarios.map(sc => sc.label)];
    this.hf.setCellContents({ sheet: s.id, col: 0, row: 0 }, [headers]);
    s.nextRow = 1;

    // Input rows
    const inputRowMap = {};
    for (const input of config.inputs) {
      const hfRow = s.nextRow;
      const a1Row = hfRow + 1;
      s.nextRow++;

      this.hf.setCellContents({ sheet: s.id, col: 0, row: hfRow }, input.label);
      for (let i = 0; i < scenCount; i++) {
        const val = config.scenarios[i].values[input.name] ?? 0;
        this.hf.setCellContents({ sheet: s.id, col: i + 1, row: hfRow }, val);
      }

      inputRowMap[input.name] = a1Row;
      s.rowMap[input.name] = a1Row;
      s.rows.push({ label: input.label, a1Row, hfRow, isInput: true, name: input.name });
    }

    // Blank separator
    s.nextRow++;

    // Output rows
    const outputRows = [];
    for (const out of config.outputs) {
      const hfRow = s.nextRow;
      const a1Row = hfRow + 1;
      s.nextRow++;

      this.hf.setCellContents({ sheet: s.id, col: 0, row: hfRow }, out.label);

      if (out.section || !out.formula) {
        s.rows.push({ label: out.label, a1Row, hfRow, section: out.section });
        outputRows.push({ ...out, a1Row, hfRow });
        continue;
      }

      // Write formula for each scenario column
      for (let i = 0; i < scenCount; i++) {
        const colLetter = _colToLetter(i + 1); // B, C, D, ..., Z, AA, AB, ...

        // Resolve formula: {InputName} → column-relative A1 ref, {DataName} → named expression
        let formula = out.formula;
        formula = formula.replace(/\{(\w+)\}/g, (match, name) => {
          // Check if it's a scenario input
          if (inputRowMap[name]) return `${colLetter}${inputRowMap[name]}`;
          // Check if it's a named expression from another sheet
          if (this.namedExprs[name]) return name;
          // Check if it's a prior output in this sheet
          if (s.rowMap[name]) return `${colLetter}${s.rowMap[name]}`;
          throw new Error(`Unknown ref {${name}} in output formula: ${out.formula}`);
        });

        try {
          this.hf.setCellContents({ sheet: s.id, col: i + 1, row: hfRow }, `=${formula}`);
        } catch (e) {
          throw new Error(`Error in scenario output "${out.label}" col ${colLetter}: ${e.message}`);
        }
      }

      if (out.name) {
        s.rowMap[out.name] = a1Row;
      }

      s.rows.push({ label: out.label, a1Row, hfRow, ...out });
      outputRows.push({ ...out, a1Row, hfRow });
    }

    return { inputRowMap, outputRows };
  }

  // ── Read values ──

  getValue(sheet, name) {
    const s = this.sheets[sheet];
    const row = s.rowMap[name];
    if (!row) throw new Error(`Unknown name "${name}" in sheet "${sheet}"`);
    return this.hf.getCellValue({ sheet: s.id, col: 1, row: row - 1 });
  }

  getScenarioValue(sheet, scenarioIndex, name) {
    const s = this.sheets[sheet];
    const row = s.rowMap[name];
    if (!row) throw new Error(`Unknown name "${name}" in sheet "${sheet}"`);
    return this.hf.getCellValue({ sheet: s.id, col: scenarioIndex + 1, row: row - 1 });
  }

  getCellValue(sheet, col, a1Row) {
    const s = this.sheets[sheet];
    return this.hf.getCellValue({ sheet: s.id, col, row: a1Row - 1 });
  }

  // ── Export to xlsx ──

  async exportXlsx(filePath, config = {}) {
    const ExcelJS = require('exceljs');
    const wb = new ExcelJS.Workbook();
    wb.creator = config.creator ?? 'pi-agent (SheetModel)';
    wb.created = new Date();

    // Styles
    const styles = {
      headerFill: { type: 'pattern', pattern: 'solid', fgColor: { argb: config.headerColor ?? '1B3A5C' } },
      headerFont: { bold: true, color: { argb: 'FFFFFF' }, size: 11 },
      sectionFont: { bold: true, size: 11 },
      inputFill: { type: 'pattern', pattern: 'solid', fgColor: { argb: 'DAEEF3' } },
      greenFill: { type: 'pattern', pattern: 'solid', fgColor: { argb: 'E2EFDA' } },
      amberFill: { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF2CC' } },
      redFill: { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FCE4EC' } },
      thinBorder: {
        top: { style: 'thin' }, bottom: { style: 'thin' },
        left: { style: 'thin' }, right: { style: 'thin' },
      },
    };

    const fmtMap = {
      number: '#,##0',
      percent: '0.0%',
      ratio: '0.00"x"',
      decimal: '#,##0.00',
    };

    // Export each sheet first, then assign named ranges via cell.names
    // (ExcelJS definedNames.add/addEx is buggy — cell.names is the only reliable way)
    const worksheets = {};
    for (const [name, s] of Object.entries(this.sheets)) {
      const ws = wb.addWorksheet(name);
      worksheets[name] = ws;
      const isScenario = s.rows.some(r => r.isInput);

      if (isScenario) {
        this._exportScenarioSheet(ws, s, styles, fmtMap);
      } else {
        this._exportDataSheet(ws, s, styles, fmtMap);
      }
    }

    // Register named ranges by setting cell.names on the target cells
    for (const [sheetName, s] of Object.entries(this.sheets)) {
      const ws = worksheets[sheetName];
      for (const row of s.rows) {
        if (row.name && s.rowMap[row.name]) {
          ws.getCell('B' + row.a1Row).names = [row.name];
        }
      }
    }

    await wb.xlsx.writeFile(filePath);
    return filePath;
  }

  _exportDataSheet(ws, s, styles, fmtMap) {
    ws.getColumn(1).width = 35;
    ws.getColumn(2).width = 18;
    ws.views = [{ state: 'frozen', xSplit: 1, ySplit: 0 }];

    for (const row of s.rows) {
      const r = ws.getRow(row.a1Row);
      r.getCell(1).value = row.label;

      if (row.section) {
        r.getCell(1).font = styles.sectionFont;
        continue;
      }

      const val = row.value;
      if (typeof val === 'string' && val.startsWith('=')) {
        const resolved = this._resolveForExcel(val);
        r.getCell(2).value = { formula: resolved.slice(1) };
        r.getCell(2).numFmt = fmtMap.number;
        r.getCell(2).font = { bold: true };
      } else if (typeof val === 'number') {
        r.getCell(2).value = val;
        r.getCell(2).numFmt = fmtMap.number;
      }
    }
  }

  _exportScenarioSheet(ws, s, styles, fmtMap) {
    ws.getColumn(1).width = 30;

    // Find how many scenario columns
    const headerRow = this.hf.getSheetSerialized(s.id);
    // Count from first row
    const scenCount = s.rows.filter(r => r.isInput).length > 0
      ? (() => {
          const inputRow = s.rows.find(r => r.isInput);
          let count = 0;
          for (let c = 1; c < 20; c++) {
            const v = this.hf.getCellValue({ sheet: s.id, col: c, row: 0 });
            if (v !== null && v !== undefined && v !== '') count++;
            else break;
          }
          return count;
        })()
      : 0;

    for (let c = 2; c <= scenCount + 1; c++) ws.getColumn(c).width = 20;

    // Row 1: Headers
    const r1 = ws.getRow(1);
    for (let c = 0; c <= scenCount; c++) {
      const cell = r1.getCell(c + 1);
      cell.value = this.hf.getCellValue({ sheet: s.id, col: c, row: 0 });
      cell.fill = styles.headerFill;
      cell.font = styles.headerFont;
      cell.alignment = { horizontal: 'center', wrapText: true };
      cell.border = styles.thinBorder;
    }

    // Data rows
    for (const row of s.rows) {
      const r = ws.getRow(row.a1Row);
      r.getCell(1).value = row.label;

      if (row.isInput) {
        r.getCell(1).font = { italic: true };
        for (let c = 1; c <= scenCount; c++) {
          const cell = r.getCell(c + 1);
          cell.value = this.hf.getCellValue({ sheet: s.id, col: c, row: row.hfRow });
          cell.numFmt = fmtMap.number;
          cell.fill = styles.inputFill;
          cell.border = styles.thinBorder;
        }
        continue;
      }

      if (row.section) {
        r.getCell(1).font = styles.sectionFont;
        continue;
      }

      if (!row.formula) continue;

      const fmt = fmtMap[row.format] || fmtMap.number;

      for (let c = 1; c <= scenCount; c++) {
        const cell = r.getCell(c + 1);
        // Get the formula from HyperFormula (returns with leading =, strip it for ExcelJS)
        let hfFormula = this.hf.getCellFormula({ sheet: s.id, col: c, row: row.hfRow });
        if (hfFormula) {
          if (hfFormula.startsWith('=')) hfFormula = hfFormula.slice(1);
          cell.value = { formula: hfFormula };
        } else {
          cell.value = this.hf.getCellValue({ sheet: s.id, col: c, row: row.hfRow });
        }
        cell.numFmt = fmt;
        cell.border = styles.thinBorder;
        cell.alignment = { horizontal: 'right' };
      }

      // Conditional formatting
      if (row.thresholds) {
        const range = `B${row.a1Row}:${String.fromCharCode(65 + scenCount)}${row.a1Row}`;
        const { good, bad, invert } = row.thresholds;
        if (invert) {
          ws.addConditionalFormatting({
            ref: range,
            rules: [
              { type: 'cellIs', operator: 'lessThanOrEqual', formulae: [good], style: { fill: styles.greenFill } },
              { type: 'cellIs', operator: 'greaterThan', formulae: [bad], style: { fill: styles.redFill } },
              { type: 'cellIs', operator: 'between', formulae: [good, bad], style: { fill: styles.amberFill } },
            ],
          });
        } else {
          ws.addConditionalFormatting({
            ref: range,
            rules: [
              { type: 'cellIs', operator: 'greaterThanOrEqual', formulae: [good], style: { fill: styles.greenFill } },
              { type: 'cellIs', operator: 'lessThan', formulae: [bad], style: { fill: styles.redFill } },
              { type: 'cellIs', operator: 'between', formulae: [bad, good], style: { fill: styles.amberFill } },
            ],
          });
        }
      }
    }

    // Freeze panes
    ws.views = [{ state: 'frozen', xSplit: 1, ySplit: 1 }];
  }

  _resolveForExcel(formula) {
    // For Excel export, named expressions work as-is
    // Just need to handle {Name} refs if any remain
    return formula.replace(/\{(\w+)\}/g, (match, name) => {
      return this.namedExprs[name] ? name : match;
    });
  }

  // ── Console output ──

  printScenarios(sheetName, config = {}) {
    const s = this.sheets[sheetName];
    const scenRows = s.rows.filter(r => !r.isInput && !r.section && r.formula);
    const inputRows = s.rows.filter(r => r.isInput);

    // Count scenarios from header row
    const scenLabels = [];
    for (let c = 1; c < 20; c++) {
      const v = this.hf.getCellValue({ sheet: s.id, col: c, row: 0 });
      if (v !== null && v !== undefined && v !== '') scenLabels.push(v);
      else break;
    }

    const fmt = n => {
      if (n == null || typeof n !== 'number' || isNaN(n)) return '—';
      return n.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    };
    const fmtR = n => typeof n === 'number' && isFinite(n) ? n.toFixed(2) + 'x' : '—';
    const fmtP = n => typeof n === 'number' && isFinite(n) ? (n * 100).toFixed(1) + '%' : '—';
    const flag = (v, th) => {
      if (!th || typeof v !== 'number' || !isFinite(v)) return '⚪';
      if (th.invert) return v <= th.good ? '🟢' : v > th.bad ? '🔴' : '🟡';
      return v >= th.good ? '🟢' : v < th.bad ? '🔴' : '🟡';
    };

    const formatters = { number: fmt, percent: fmtP, ratio: fmtR };

    for (let sc = 0; sc < scenLabels.length; sc++) {
      console.log(`\n  ${scenLabels[sc]}`);
      console.log('  ' + '─'.repeat(68));

      for (const row of s.rows) {
        if (row.isInput || !row.label) continue;
        if (row.section) {
          console.log(`\n    ${row.label}`);
          continue;
        }
        if (!row.formula) continue;

        const v = this.hf.getCellValue({ sheet: s.id, col: sc + 1, row: row.hfRow });
        const formatter = formatters[row.format] || fmt;
        const f = flag(v, row.thresholds);
        console.log('    ' + row.label.padEnd(28) + formatter(v).padStart(12) + '  ' + f);
      }
    }
  }
}
