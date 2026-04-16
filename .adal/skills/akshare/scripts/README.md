# AkShare Tool 使用指南

## 概述

`akshare_tool.py` 是一个功能强大的命令行工具，用于获取中国金融市场数据。支持A股、港股、美股、期货、基金、宏观经济指标和指数数据。

## 安装依赖

```bash
pip install akshare pandas pyarrow
```

## 快速开始

### 基本用法

```bash
# 显示帮助信息
python3 akshare_tool.py --help

# 获取所有A股实时行情
python3 akshare_tool.py stock-realtime
```

## 功能详解

### 1. A股实时行情

获取A股市场的实时行情数据，支持全部股票或单只股票查询，支持字段筛选。

```bash
# 获取所有A股实时行情
python3 akshare_tool.py stock-realtime

# 获取单只股票实时行情
python3 akshare_tool.py stock-realtime --symbol 000001

# 筛选特定行业的股票
python3 akshare_tool.py stock-realtime --filter-field 行业 --filter-value 银行

# 不使用缓存（强制从网络获取）
python3 akshare_tool.py stock-realtime --no-cache

# 输出为JSON格式
python3 akshare_tool.py stock-realtime --format json

# 保存到CSV文件
python3 akshare_tool.py stock-realtime --output stocks.csv
```

### 2. 股票历史数据

获取股票的历史K线数据，支持日线、周线、月线，支持前复权、后复权、不复权。

```bash
# 获取股票日线数据（默认前复权）
python3 akshare_tool.py stock-history --symbol 000001 --period daily

# 获取周线数据
python3 akshare_tool.py stock-history --symbol 000001 --period weekly

# 获取月线数据
python3 akshare_tool.py stock-history --symbol 000001 --period monthly

# 指定日期范围
python3 akshare_tool.py stock-history --symbol 000001 --start-date 20240101 --end-date 20241231

# 后复权数据
python3 akshare_tool.py stock-history --symbol 000001 --adjust hfq

# 不复权数据
python3 akshare_tool.py stock-history --symbol 000001 --adjust ""
```

### 3. 港股数据

```bash
# 港股实时行情
python3 akshare_tool.py hk-realtime

# 港股历史数据
python3 akshare_tool.py hk-history --symbol 00700 --period daily

# 港股周线数据
python3 akshare_tool.py hk-history --symbol 00700 --period weekly
```

### 4. 美股数据

```bash
# 美股实时行情
python3 akshare_tool.py us-realtime
```

### 5. 期货数据

```bash
# 期货实时行情（全部）
python3 akshare_tool.py futures-realtime

# 特定期货品种
python3 akshare_tool.py futures-realtime --symbol IF

# 期货历史数据
python3 akshare_tool.py futures-history --symbol IF0 --start-date 20240101
```

### 6. 基金数据

```bash
# 获取基金列表
python3 akshare_tool.py fund-list

# 筛选特定类型的基金
python3 akshare_tool.py fund-list --type 股票型

# 获取基金历史净值数据
python3 akshare_tool.py fund-history --code 000001

# 获取累计净值走势
python3 akshare_tool.py fund-history --code 000001 --indicator "累计净值走势"
```

### 7. 宏观经济数据

```bash
# GDP数据
python3 akshare_tool.py macro-gdp

# CPI数据
python3 akshare_tool.py macro-cpi

# PMI数据
python3 akshare_tool.py macro-pmi
```

### 8. 指数数据

```bash
# 指数实时行情
python3 akshare_tool.py index-realtime

# 深证指数
python3 akshare_tool.py index-realtime --type sz

# 上证指数
python3 akshare_tool.py index-realtime --type sh

# 指数历史数据
python3 akshare_tool.py index-history --symbol 000001 --period daily
```

## 高级功能

### 缓存控制

```bash
# 禁用缓存
python3 akshare_tool.py stock-realtime --no-cache

# 自定义缓存过期时间（默认24小时）
python3 akshare_tool.py stock-realtime --cache-expiry 12

# 清除所有缓存
python3 akshare_tool.py clear-cache
```

### 输出格式

```bash
# 表格格式（默认）
python3 akshare_tool.py stock-realtime --format table

# JSON格式
python3 akshare_tool.py stock-realtime --format json

# CSV格式
python3 akshare_tool.py stock-realtime --format csv

# 保存到文件
python3 akshare_tool.py stock-realtime --output data.csv
python3 akshare_tool.py stock-realtime --output data.json
```

## 错误处理和重试

工具内置了错误处理和自动重试机制：

- **最大重试次数**: 3次
- **重试延迟**: 指数退避（1秒、2秒、4秒）
- **自动缓存**: 成功获取的数据会自动缓存

遇到网络错误时，工具会自动重试，并在控制台显示重试进度。

## 缓存机制

工具使用文件系统缓存数据：

- **缓存位置**: `~/.akshare_cache/`
- **缓存格式**: Parquet格式
- **默认过期时间**: 24小时
- **缓存键**: 基于函数名和参数的MD5哈希

使用缓存可以：
- 减少网络请求
- 提高响应速度
- 降低被限流的风险

## 常见问题

### 1. 导入错误

```
错误: 缺少必要的依赖库
请运行: pip install akshare pandas
```

解决方法：
```bash
pip install akshare pandas pyarrow
```

### 2. 网络超时

如果遇到网络超时，工具会自动重试。如果持续失败，请检查：
- 网络连接是否正常
- 是否被防火墙拦截
- AkShare服务是否可用

### 3. 数据为空

某些数据源可能暂时不可用，或者参数不正确。请检查：
- 股票代码是否正确
- 日期格式是否为YYYYMMDD
- 参数是否在有效范围内

## 性能优化建议

1. **使用缓存**: 对于不常变化的数据，使用缓存可以显著提高速度
2. **批量操作**: 避免频繁的小请求，尽量批量获取数据
3. **合理设置缓存时间**: 根据数据更新频率设置合适的缓存过期时间
4. **限制数据量**: 使用日期范围限制获取的数据量

## 示例脚本

### 每日数据更新脚本

```bash
#!/bin/bash
# update_daily.sh

# 获取主要指数实时行情
python3 akshare_tool.py index-realtime --output indices.csv

# 获取银行股实时行情
python3 akshare_tool.py stock-realtime --filter-field 行业 --filter-value 银行 --output banks.csv

# 获取热门基金净值
python3 akshare_tool.py fund-history --code 000001 --output fund_000001.csv
```

### 数据分析示例

```python
import pandas as pd
from akshare_tool import AkShareTool

# 初始化工具
tool = AkShareTool()

# 获取股票历史数据
df = tool.get_stock_history(symbol="000001", period="daily", adjust="qfq")

# 计算移动平均线
df['MA5'] = df['收盘'].rolling(window=5).mean()
df['MA20'] = df['收盘'].rolling(window=20).mean()

# 显示最近20天数据
print(df.tail(20))
```

## 技术特性

- ✅ 完整的错误处理和重试机制
- ✅ 智能数据缓存（Parquet格式）
- ✅ 灵活的命令行参数
- ✅ 多种输出格式（表格/JSON/CSV）
- ✅ 支持所有主要金融市场数据
- ✅ 详细的帮助信息和示例
- ✅ 类型提示和文档字符串

## 版本信息

- Python: 3.6+
- AkShare: 1.18.22+
- Pandas: 1.0+
- PyArrow: 0.17+

## 许可证

本工具遵循 AkShare 的开源许可证。

## 相关链接

- [AkShare 官方文档](https://akshare.akfamily.xyz/)
- [AkShare GitHub](https://github.com/akfamily/akshare)
- [Pandas 文档](https://pandas.pydata.org/)

## 更新日志

### v1.0.0 (2026-02-08)

- 初始版本发布
- 支持A股、港股、美股、期货、基金、宏观经济数据
- 实现缓存机制
- 实现错误处理和重试
- 支持多种输出格式