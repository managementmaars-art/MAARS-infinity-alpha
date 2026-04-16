# CSV Format for VAT Declarations

## Required Columns

| Column | Description | Example |
|--------|-------------|---------|
| `Quarter` | Q1, Q2, Q3, or Q4 | Q1 |
| `Provider` | Supplier name | The Office City |
| `Address` | Full address | 1 Rue Example L-1234 Luxembourg, Luxembourg |
| `Invoice Date` | YYYY-MM-DD | 2024-01-05 |
| `Invoice Number` | Invoice ID | INV-240017 |
| `Description` | Service description | Coworking + Business Address |
| `Total Amount (EUR)` | Gross amount including VAT | 406.93 |
| `VAT Rate` | Percentage with % symbol | 17% |
| `VAT Amount` | VAT in EUR | 59.13 |
| `Net Amount` | Amount without VAT | 347.80 |
| `Currency` | EUR or USD | EUR |
| `File Path` | Path to PDF | Q1/The Office City/INV-240017.pdf |
| `Notes` | Category/Context | Luxembourg VAT |

## Example Rows

### Luxembourg Supplier (Direct VAT)
```csv
Q1,The Office City,"1 Rue Example",2024-01-05,INV-240017,Coworking January,406.93,17%,59.13,347.80,EUR,Q1/Office/INV.pdf,Luxembourg VAT
```

### Non-EU Service (Reverse Charge)
```csv
Q1,Midjourney,"270 University Ave",2024-01-10,52C526D7-0003,AI Subscription,9.46,0%,0.00,9.46,USD,Q1/Midjourney/inv.pdf,Outside EU - No VAT
```

### EU Service (Reverse Charge)
```csv
Q1,Scaleway,"11 rue de Bilbes",2024-01-05,2445511,Cloud Services,8.27,20%,1.38,6.89,EUR,Q1/Scaleway/inv.pdf,EU - French VAT
```

### Exempt Service
```csv
Q4,Luxair,"7 Rue Gabriel",2024-11-26,LUXAIR-001,Flight tickets,420.00,0%,0.00,420.00,EUR,Q4/Luxair/ticket.pdf,Transport exempt
```

## Important Notes

1. **Use dot (.) as decimal separator in CSV** - Even though Luxembourg uses comma
2. **USD amounts will be converted** using exchange rate (default: 0.923)
3. **Negative amounts for credit notes** - Will be subtracted automatically
4. **Verify VAT amounts** - Script uses invoice VAT, doesn't calculate
5. **Notes field is critical** - Used to categorize expenses (Luxembourg VAT, Outside EU, etc.)
