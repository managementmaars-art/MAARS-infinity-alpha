---
name: luxembourg-vat-xml
description: Generate Luxembourg quarterly VAT declarations (TVA_DECT) in eCDF XML format for AED submission. Use when working with Luxembourg VAT returns, eCDF XML generation, or fixing VAT declaration validation errors for Luxembourg businesses.
---

# Luxembourg VAT Declarations (eCDF)

Generate Luxembourg quarterly VAT declarations (TVA_DECT) in eCDF XML format for AED submission.

## Quick Start

1. **Copy the example config:**
   ```bash
   cp vat_config.example.json vat_config.json
   ```

2. **Edit `vat_config.json`** with your company details:
   - `MatrNbr`: Your matricule number
   - `RCSNbr`: Your RCS number  
   - `VATNbr`: Your VAT number
   - `eCDFPrefix`: Your eCDF prefix

3. **Prepare your CSV file** with expenses (see `example_csv_format.md`)

4. **Run the generator:**
   ```bash
   python3 generate_vat_declarations.py
   ```

## Files

- `generate_vat_declarations.py` - Main script
- `vat_config.example.json` - Configuration template
- `example_csv_format.md` - CSV format documentation
- `FIELD_FORMULAS.md` - eCDF field formulas reference

---

## Critical Lessons Learned

> **⚠️ CRITICAL**: This skill documents hard-learned lessons from fixing VAT declaration errors. Read completely before generating XML.

## Overview

Generate Luxembourg quarterly VAT declarations (TVA_DECT) in eCDF XML format for AED submission. Based on painful real-world debugging of validation errors.

---

## Critical Lessons Learned (READ FIRST)

### 1. Field Order is CRITICAL

The eCDF validator checks **exact field sequence**, not just presence. One field out of order = rejection.

**Correct Order:**
```
Numeric 012-105 → Choice 204/205/491/492/493 → Numeric 403/418/453 → Numeric 042/416/417/451/452
```

**Common Mistake:**
```xml
<!-- WRONG - 042 at wrong position -->
<NumericField id="042">0,00</NumericField>
<Choice id="204">1</Choice>

<!-- CORRECT -->
<Choice id="204">1</Choice>
<Choice id="205">0</Choice>
<Choice id="491">0</Choice>
<Choice id="492">0</Choice>
<Choice id="493">0</Choice>
<NumericField id="403">0</NumericField>
<NumericField id="418">0</NumericField>
<NumericField id="453">0</NumericField>
<NumericField id="042">0,00</NumericField>
<NumericField id="416">0,00</NumericField>
<NumericField id="417">0,00</NumericField>
<NumericField id="451">0,00</NumericField>
<NumericField id="452">0,00</NumericField>
```

### 2. Fields 491/492/493 - Year Dependent

⚠️ **Important**: These fields may or may not be required depending on the declaration year:

**For 2024 declarations:** Only 204 and 205 are needed
```xml
<Choice id="204">1</Choice>
<Choice id="205">0</Choice>
```

**For 2025+ declarations:** All 5 Choice fields may be required
```xml
<Choice id="204">1</Choice>
<Choice id="205">0</Choice>
<Choice id="491">0</Choice>
<Choice id="492">0</Choice>
<Choice id="493">0</Choice>
```

**Error if wrong:** `"Les champs suivants ne sont pas autorisés, ou mal placés: 491, 492, 493"`

**Solution:** Try without 491/492/493 first. If you get this error, add them.

### 3. Rounding is a Trap

The validator adds **rounded XML values** to check formulas, not raw float values.

**Example of failure:**
```
462 = 3.513900 → XML shows "3,51"
464 = 11.281427 → XML shows "11,28"
Validator computes: 3,51 + 11,28 = 14,79

But if you calculate from unrounded:
410 = 3.513900 + 11.281427 = 14.795327 → XML shows "14,80"

14,80 ≠ 14,79 → VALIDATION ERROR!
```

**Solution:** Calculate derived fields from **already-rounded** components:
```python
field_410 = round(field_462, 2) + round(field_464, 2)
```

### 4. Formula Reference (eCDF Requirements)

| Field | Formula | Notes |
|-------|---------|-------|
| **409** | 436 + 435 + 463 + 765 | Total services requiring reverse charge |
| **410** | 462 + 464 + 766 | Total VAT on services received |
| **076** | 046 + 056 + 407 + 410 + 768 + 227 | Total output VAT |
| **093** | 458 + 459 + 460 + 090 + 461 + 092 + 228 | Total input VAT |
| **461** | 464 + 462 + 766 | Deductible reverse charge |
| **463** | 751 + 951 + 753 + 953 + 755 + 955 + 441 + 445 | Non-EU base |
| **464** | 752 + 952 + 754 + 954 + 756 + 956 + 442 | Non-EU VAT |

### 5. Invoice Categorization Matters

**Common mistake**: Labeling coworking as "Rent - No VAT" when it's actually **services with 17% VAT**.

**Real example:**
- The Office City invoices said "Rent" but were actually "Coworking + Business Address"
- Difference: €59.13/month × 12 months = **€709.56 in claimable VAT nearly lost!**

Always verify actual VAT amount on PDF, don't rely on description.

---

## Usage

### Quick Start

```python
# See generate_vat_declarations.py for full implementation
python3 generate_vat_declarations.py
```

### Required Files

1. **CSV file** with columns:
   - Quarter, Provider, Total Amount (EUR), VAT Rate, VAT Amount, Net Amount, Currency, Notes

2. **Company config** (vat_config.json):
```json
{
  "company": {
    "MatrNbr": "YOUR_MATRICULE_NUMBER",
    "RCSNbr": "YOUR_RCS_NUMBER",
    "VATNbr": "YOUR_VAT_NUMBER",
    "eCDFPrefix": "YOUR_ECDF_PREFIX"
  }
}
```

### VAT Categories

| Provider Type | Fields | Treatment |
|---------------|--------|-----------|
| Luxembourg suppliers | 458 | Direct VAT deduction |
| Non-EU services (USA) | 751/752/463/464/461 | Reverse charge at 17% |
| EU services (France, etc) | 741/742/436/462/461 | Reverse charge at 17% |

---

## Validation Checklist

Before submitting, verify:

- [ ] All 5 Choice fields present (204, 205, 491, 492, 493)
- [ ] Choice fields in correct position (after 105, before 403)
- [ ] Fields 042/416/417/451/452 at very end
- [ ] Fields 403/418/453 as integers ("0" not "0,00")
- [ ] Formulas validate with rounded values
- [ ] No negative values where not expected
- [ ] Exchange rates applied for USD invoices

---

## Error Messages Decoded

| Error | Meaning | Fix |
|-------|---------|-----|
| "Champs 491, 492, 493 non autorisés ou mal placés" | Choice fields missing/wrong position | Add all 5 Choice fields in correct order |
| "Champ 409 = champs (436 + 435 + 463 + 765)" | Formula error for field 409 | Calculate from rounded components |
| "Champ 410 = champs (462 + 464 + 766)" | Formula error for field 410 | Calculate from rounded components |
| "Champ 076 = champs (046 + 056 + 407 + 410 + 768 + 227)" | Formula error for field 076 | Set 076 = 410 for expense-only declarations |

---

## Files in This Skill

- `generate_vat_declarations.py` - Working script with all fixes
- `vat_config.json` - Company configuration template
- `example_csv_format.md` - CSV column requirements

---

## Real-World Debugging Tips

1. **Test one quarter first** - Don't generate all 4 until one passes
2. **Check exact error message** - It tells you which field and expected formula
3. **Compare with working reference** - Line-by-line diff of XML structure
4. **Watch for floating point** - Python float math can cause 0.01 rounding errors
5. **Verify invoice PDFs** - Don't trust descriptions, check actual VAT amounts

---

## Generated With

- Date: 2024-01-29
- Tested: Successfully validated all 4 quarters 2024
- Total VAT recovered: €1,154.29 (was €372.85 before fixes)
