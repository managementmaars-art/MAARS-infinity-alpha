# eCDF Field Formulas Reference

## Critical Formulas (MUST Validate)

### Field 409 - Total Services Requiring Reverse Charge
```
409 = 436 + 435 + 463 + 765
```
- **436**: Total EU services base
- **435**: EU services exempt (usually 0)
- **463**: Total non-EU services base
- **765**: Domestic reverse charge base (usually 0)

**For expense-only declarations:** 409 = 436 + 463

---

### Field 410 - Total VAT on Services Received
```
410 = 462 + 464 + 766
```
- **462**: Total EU services VAT
- **464**: Total non-EU services VAT
- **766**: Domestic reverse charge VAT (usually 0)

**For expense-only declarations:** 410 = 462 + 464

⚠️ **ROUNDING TRAP**: Calculate from rounded values!
```python
field_410 = round(field_462, 2) + round(field_464, 2)
```

---

### Field 076 - Total Output VAT
```
076 = 046 + 056 + 407 + 410 + 768 + 227
```

**For expense-only declarations:** 076 = 410

---

### Field 093 - Total Input VAT
```
093 = 458 + 459 + 460 + 090 + 461 + 092 + 228
```
- **458**: Domestic Luxembourg purchases
- **459**: Intracommunity acquisitions deductible
- **460**: Imports deductible
- **090**: Goods allocated to business
- **461**: Reverse charge deductible
- **092**: Solidarity guarantee
- **228**: Special regime adjustments

**For expense-only declarations:** 093 = 458 + 461

---

### Field 461 - Deductible Reverse Charge
```
461 = 464 + 462 + 766
```
Mirror deduction of reverse charge VAT declared.

**For expense-only declarations:** 461 = 464 + 462

---

### Field 463 - Non-EU Services Base
```
463 = 751 + 951 + 753 + 953 + 755 + 955 + 441 + 445
```
Breakdown by rate (17%, 16%, 14%, 13%, 8%, 7%, 3%, exempt)

**Most common:** 463 = 751 (when all at 17%)

---

### Field 464 - Non-EU Services VAT
```
464 = 752 + 952 + 754 + 954 + 756 + 956 + 442
```
VAT amounts corresponding to 463 breakdown.

**Most common:** 464 = 752 (when all at 17%)

---

## Balance Fields

### Field 103 - Total Output VAT
```
103 = 076
```

### Field 104 - Total Deductible VAT
```
104 = 102
102 = 093 - 097
```

### Field 105 - Balance (Negative = Refund)
```
105 = 103 - 104
```

For expense-only companies: 105 should be negative (refund due).

---

## Common Service Company Pattern

```
Revenue: 0
Expenses:
  - Field 458: Sum of Luxembourg VAT (direct deduction)
  - Field 751/752: Non-EU services reverse charge
  - Field 741/742: EU services reverse charge (if any)

Derived:
  - Field 463 = 751
  - Field 464 = 752
  - Field 436 = 741
  - Field 462 = 742
  - Field 461 = 464 + 462
  - Field 409 = 436 + 463
  - Field 410 = 462 + 464
  - Field 076 = 410
  - Field 093 = 458 + 461
  - Field 102 = 093
  - Field 103 = 076
  - Field 104 = 102
  - Field 105 = 103 - 104 (negative = refund)
```
