# AkShare API Reference

## Stock Data APIs

### A-Share Real-time Data

#### stock_zh_a_spot_em()
获取东方财富网-沪深京 A 股实时行情数据

**Parameters:** None

**Returns:** DataFrame with columns:
- 代码: Stock code
- 名称: Stock name
- 最新价: Latest price
- 涨跌幅: Price change percentage
- 涨跌额: Price change amount
- 成交量: Volume
- 成交额: Turnover
- 振幅: Amplitude
- 最高: Highest price
- 最低: Lowest price
- 今开: Opening price
- 昨收: Previous close
- 量比: Volume ratio
- 换手率: Turnover rate
- 市盈率-动态: PE ratio
- 市净率: PB ratio

**Example:**
```python
df = ak.stock_zh_a_spot_em()
print(df.head())
```

#### stock_zh_a_hist()
获取东方财富网-沪深京 A 股个股历史行情数据

**Parameters:**
- `symbol`: Stock code (e.g., "000001")
- `period`: Period type - "daily", "weekly", "monthly"
- `start_date`: Start date (format: "20240101")
- `end_date`: End date (format: "20241231")
- `adjust`: Adjustment type - "qfq" (前复权), "hfq" (后复权), "" (不复权)

**Returns:** DataFrame with OHLCV data

**Example:**
```python
df = ak.stock_zh_a_hist(
    symbol="000001",
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="qfq"
)
```

#### stock_info_a_code_name()
获取东方财富网-沪深京 A 股代码和名称

**Parameters:** None

**Returns:** DataFrame with stock codes and names

**Example:**
```python
df = ak.stock_info_a_code_name()
print(df.head())
```

### Hong Kong Stocks

#### stock_hk_spot_em()
获取东方财富网-港股实时行情数据

**Parameters:** None

**Returns:** DataFrame with HK stock real-time data

#### stock_hk_hist()
获取东方财富网-港股个股历史行情数据

**Parameters:**
- `symbol`: HK stock code (e.g., "00700")
- `period`: Period type
- `adjust`: Adjustment type

**Example:**
```python
df = ak.stock_hk_hist(symbol="00700", period="daily", adjust="qfq")
```

### US Stocks

#### stock_us_spot_em()
获取东方财富网-美股实时行情数据

**Parameters:** None

**Returns:** DataFrame with US stock real-time data

## Futures Data APIs

#### futures_zh_spot()
获取东方财富网-中国商品期货实时行情数据

**Parameters:** None

**Returns:** DataFrame with futures real-time data

#### futures_zh_hist_sina()
获取新浪财经-中国商品期货历史行情数据

**Parameters:**
- `symbol`: Futures code (e.g., "IF0")
- `start_date`: Start date
- `end_date`: End date

**Example:**
```python
df = ak.futures_zh_hist_sina(symbol="IF0", start_date="20240101", end_date="20241231")
```

## Fund Data APIs

#### fund_open_fund_info_em()
获取天天基金网-开放式基金数据

**Parameters:**
- `fund`: Fund code (optional)
- `indicator`: Indicator type (optional, e.g., "单位净值走势")

**Returns:** DataFrame with fund information

**Example:**
```python
# Get all funds
df = ak.fund_open_fund_info_em()

# Get specific fund
df = ak.fund_open_fund_info_em(fund="000001", indicator="单位净值走势")
```

## Macroeconomic Data APIs

#### macro_china_gdp()
获取中国宏观经济数据-国内生产总值

**Parameters:** None

**Returns:** DataFrame with GDP data

**Example:**
```python
df = ak.macro_china_gdp()
print(df)
```

#### macro_china_cpi()
获取中国宏观经济数据-居民消费价格指数

**Parameters:** None

**Returns:** DataFrame with CPI data

**Example:**
```python
df = ak.macro_china_cpi()
print(df)
```

#### macro_china_pmi()
获取中国宏观经济数据-采购经理指数

**Parameters:** None

**Returns:** DataFrame with PMI data

**Example:**
```python
df = ak.macro_china_pmi()
print(df)
```

## Index Data APIs

#### index_zh_a_hist()
获取东方财富网-沪深京 A 股指数历史行情数据

**Parameters:**
- `symbol`: Index code (e.g., "sh000001" for Shanghai Composite)
- `period`: Period type
- `start_date`: Start date
- `end_date`: End date

**Example:**
```python
df = ak.index_zh_a_hist(symbol="sh000001", period="daily", start_date="20240101", end_date="20241231")
```

#### index_zh_a_spot()
获取东方财富网-沪深京 A 股指数实时行情数据

**Parameters:** None

**Returns:** DataFrame with index real-time data

## Common Stock Codes

### Major A-Share Indices
- `sh000001` - 上证指数
- `sz399001` - 深证成指
- `sz399006` - 创业板指
- `sh000300` - 沪深300
- `sz399905` - 中证500

### Major HK Stocks
- `00700` - 腾讯控股
- `00941` - 中国移动
- `02318` - 中国平安
- `03690` - 美团
- `00388` - 港交所

### Major US Stocks
- `AAPL` - Apple
- `MSFT` - Microsoft
- `GOOGL` - Google
- `TSLA` - Tesla
- `AMZN` - Amazon

## Error Handling

**Common errors:**
1. **Network errors**: Implement retry logic
2. **Invalid parameters**: Check parameter format
3. **Data not available**: Check if data source is accessible

**Example error handling:**
```python
import akshare as ak
import time

def fetch_with_retry(func, max_retries=3, delay=1):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(delay)
            else:
                raise e

df = fetch_with_retry(lambda: ak.stock_zh_a_spot_em())
```

## Data Processing Tips

**Common operations:**
```python
# Filter by price change
df = df[df['涨跌幅'] > 5]

# Sort by volume
df = df.sort_values('成交量', ascending=False)

# Calculate moving average
df['MA5'] = df['收盘'].rolling(window=5).mean()

# Export to CSV
df.to_csv('stock_data.csv', index=False)
```

## Official Documentation

For complete API documentation, visit:
- https://akshare.akfamily.xyz/
- https://github.com/akfamily/akshare