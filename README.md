# Bitcoin Blockchain Monitor ⚡

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Async](https://img.shields.io/badge/Async-Await-orange)](https://docs.python.org/3/library/asyncio.html)

Real-time monitoring and analytics platform for Bitcoin blockchain with advanced anomaly detection capabilities.

## ⚠️ API Rate Limiting Warning

**Important**: This project uses the Blockstream API, which has aggressive rate limiting policies:

- 🚫 **Strict rate limits**: ~1 request per second
- 🔄 **429 Errors**: Frequent "Too Many Requests" errors
- 💀 **Temporary bans**: Excessive requests can lead to temporary IP bans
- 📉 **Performance impact**: Monitoring may be interrupted due to API limitations

### Recommended Workarounds:
- Use `MIN_DELAY=2.0` in config (2+ seconds between requests)
- Implement retry logic with exponential backoff
- Consider using multiple API providers as fallback
- For production use, consider running your own Bitcoin node

## 📊 Features

- **Real-time Monitoring** - Live tracking of new blocks and transactions
- **Fee Analytics** - Comprehensive fee analysis using coinbase transactions  
- **Anomaly Detection** - Statistical IQR-based detection of unusual activity
- **Reorg Handling** - Robust handling of blockchain reorganizations
- **Async Architecture** - High-performance asynchronous implementation
- **Rate Limit Handling** - Built-in retry mechanisms for API limitations

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/bitcoin-monitor.git
cd bitcoin-monitor
pip install -r requirements.txt