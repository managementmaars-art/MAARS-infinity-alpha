# Common AkShare Functions

## Most Frequently Used Functions

### Stock Data

```python
# Get all A-share real-time quotes
ak.stock_zh_a_spot_em()

# Get single stock historical data
ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20240101", end_date="20241231", adjust="qfq")

# Get stock list
ak.stock_info_a_code_name()

# Get stock real-time quote
ak.stock_zh_a_spot()
```

### Index Data

```python
# Get index historical data
ak.index_zh_a_hist(symbol="sh000001", period="daily", start_date="20240101", end_date="20241231")

# Get index real-time data
ak.index_zh_a_spot()
```

### Fund Data

```python
# Get all funds
ak.fund_open_fund_info_em()

# Get specific fund data
ak.fund_open_fund_info_em(fund="000001", indicator="单位净值走势")
```

### Futures Data

```python
# Get futures real-time data
ak.futures_zh_spot()

# Get futures historical data
ak.futures_zh_hist_sina(symbol="IF0", start_date="20240101", end_date="20241231")
```

### Macro Data

```python
# GDP
ak.macro_china_gdp()

# CPI
ak.macro_china_cpi()

# PMI
ak.macro_china_pmi()
```

## Quick Reference by Use Case

### "Get stock price"
```python
# Real-time
df = ak.stock_zh_a_spot_em()
print(df[df['代码'] == '000001'])

# Historical
df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20240101", end_date="20241231")
```

### "Get market overview"
```python
# All stocks
df = ak.stock_zh_a_spot_em()

# Top gainers
df.sort_values('涨跌幅', ascending=False).head(10)

# Top losers
df.sort_values('涨跌幅', ascending=True).head(10)

# Most active
df.sort_values('成交量', ascending=False).head(10)
```

### "Get index data"
```python
# Shanghai Composite
df = ak.index_zh_a_hist(symbol="sh000001", period="daily", start_date="20240101", end_date="20241231")

# CSI 300
df = ak.index_zh_a_hist(symbol="sh000300", period="daily", start_date="20240101", end_date="20241231")
```

### "Get fund info"
```python
# All funds
df = ak.fund_open_fund_info_em()

# Search by name
df[df['基金简称'].str.contains('科技')]
```

## Common Patterns

### Pattern 1: Get stock data for analysis
```python
import akshare as ak

# Get historical data
df = ak.stock_zh_a_hist(
    symbol="000001",
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="qfq"
)

# Calculate indicators
df['MA5'] = df['收盘'].rolling(5).mean()
df['MA10'] = df['收盘'].rolling(10).mean()

# Export
df.to_csv('000001.csv', index=False)
```

### Pattern 2: Market screening
```python
import akshare as ak

# Get all stocks
df = ak.stock_zh_a_spot_em()

# Filter conditions
filtered = df[
    (df['涨跌幅'] > 0) &  # Positive change
    (df['成交量'] > 100000) &  # High volume
    (df['市盈率-动态'] > 0) &  # Positive PE
    (df['市盈率-动态'] < 50)  # Reasonable PE
]

print(filtered)
```

### Pattern 3: Get multiple stocks
```python
import akshare as ak

stock_codes = ['000001', '000002', '600000']

for code in stock_codes:
    df = ak.stock_zh_a_hist(
        symbol=code,
        period="daily",
        start_date="20240101",
        end_date="20241231",
        adjust="qfq"
    )
    df.to_csv(f'{code}.csv', index=False)
```

## Data Format Notes

### Common DataFrame Columns

**Stock data:**
- 日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 振幅, 涨跌幅, 涨跌额, 换手率

**Real-time data:**
- 代码, 名称, 最新价, 涨跌幅, 涨跌额, 成交量, 成交额, 振幅, 最高, 最低, 今开, 昨收, 量比, 换手率, 市盈率-动态, 市净率

### Date Format

AkShare uses `YYYYMMDD` format:
- Start date: "20240101"
- End date: "20241231"

### Stock Code Format

- A-Shares: "000001", "600000", "300001"
- Hong Kong: "00700"
- US: "AAPL", "MSFT"

## Performance Tips

1. **Batch requests**: Get all data at once when possible
2. **Cache results**: Store data locally to avoid repeated requests
3. **Filter early**: Apply filters before processing large datasets
4. **Use appropriate periods**: Daily data is sufficient for most analysis

## Troubleshooting

**"Module not found" error:**
```bash
pip install akshare
```

**"Connection error":**
- Check internet connection
- Implement retry logic
- Check if data source is accessible

**"Empty DataFrame":**
- Check if stock code is correct
- Check if date range is valid
- Check if data is available for that period

**"Invalid parameter":**
- Check parameter format (date format: YYYYMMDD)
- Check if stock code exists
- Check if period type is valid