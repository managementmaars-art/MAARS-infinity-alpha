# OpenClaw AkShare Skill

Chinese financial data access using AkShare library for OpenClaw.

## Overview

This skill provides easy access to Chinese financial market data through the [AkShare](https://akshare.akfamily.xyz/) library. It supports real-time and historical data for:

- **A-shares (A股)**: Shanghai and Shenzhen stock exchanges
- **Hong Kong stocks (港股)**: HKEX
- **US stocks (美股)**: US market data
- **Futures (期货)**: Commodity and index futures
- **Funds (基金)**: Open-end and ETF funds
- **Macroeconomic indicators (宏观)**: GDP, CPI, PMI, and more

## Installation

### Prerequisites

- Python 3.7+
- OpenClaw framework

### Install AkShare

```bash
pip install akshare
```

Or use the provided installation script:

```bash
bash scripts/install_akshare.sh
```

### Install the Skill

Copy this skill to your OpenClaw workspace:

```bash
cp -r openclaw-akshare-skill /path/to/openclaw/workspace/skills/akshare
```

## Quick Start

### Basic Stock Quote

```python
import akshare as ak

# Get all A-shares real-time data
df = ak.stock_zh_a_spot_em()
print(df.head())
```

### Historical Stock Data

```python
# Get historical daily data for a specific stock
df = ak.stock_zh_a_hist(
    symbol="000001",
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="qfq"  # Forward adjustment
)
print(df.tail())
```

## Features

### Stock Data

- **Real-time quotes**: All A-shares, Hong Kong stocks, US stocks
- **Historical data**: Daily, weekly, monthly periods with price adjustment
- **Stock list**: Complete stock code and name information

### Futures Data

- Commodity futures real-time data
- Historical futures data from major exchanges

### Fund Data

- Open-end fund information
- Fund historical net value trends

### Macroeconomic Indicators

- GDP, CPI, PPI, PMI
- Economic calendar and indicators

## Common Parameters

### Period (周期)

- `daily` - Daily (日线)
- `weekly` - Weekly (周线)
- `monthly` - Monthly (月线)

### Price Adjustment (复权)

- `qfq` - Forward adjustment (前复权)
- `hfq` - Backward adjustment (后复权)
- `""` - No adjustment (不复权)

## Examples

See the `scripts/` directory for more examples:

- `example_usage.py` - Common usage examples
- `test_basic.py` - Basic functionality tests
- `test_quick.py` - Quick start examples

## Documentation

- [SKILL.md](SKILL.md) - Complete skill documentation
- [references/akshare_api.md](references/akshare_api.md) - Detailed API reference
- [references/common_functions.md](references/common_functions.md) - Commonly used functions
- [Official AkShare Docs](https://akshare.akfamily.xyz/)

## Tips

1. **Data caching**: AkShare doesn't cache data by default. Implement your own caching if needed
2. **Rate limiting**: Be mindful of request frequency to avoid being blocked
3. **Data format**: Returns pandas DataFrame, can be easily processed
4. **Error handling**: Network errors may occur, implement retry logic

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Acknowledgments

- [AkShare](https://akshare.akfamily.xyz/) - The underlying Python library for Chinese financial data
- [OpenClaw](https://github.com/openclaw/openclaw) - The AI assistant framework

## Support

For issues and questions:
- Open an issue on GitHub
- Check [AkShare documentation](https://akshare.akfamily.xyz/)
- Review the examples in the `scripts/` directory