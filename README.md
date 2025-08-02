# Crypto Portfolio Performance Tracker

A comprehensive cryptocurrency portfolio tracking system that provides real-time performance analysis, profit/loss calculations, and automated alerts for traders and investors.

## Features

### Real-time Portfolio Tracking
- Live profit/loss calculations with percentage changes
- Portfolio allocation breakdown and visualization
- Individual coin performance metrics
- 24-hour price change tracking
- Historical performance analysis

### Transaction Management
- Buy/sell transaction recording with CSV export
- Automatic average cost basis calculation
- Complete transaction history tracking
- Portfolio rebalancing calculations

### Smart Alert System
- Customizable portfolio drop/gain thresholds
- Individual coin movement alerts
- Real-time notification system
- Anti-spam cooldown protection

### Advanced Analytics
- Visual allocation charts
- Unrealized P&L tracking
- Performance history over time
- Exportable performance reports

## Quick Start

### Prerequisites
- Python 3.7+
- `requests` library

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crypto-portfolio-tracker.git
cd crypto-portfolio-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run with demo data:
```bash
python crypto_portfolio_tracker.py demo
```

4. Or start with your own portfolio:
```bash
python crypto_portfolio_tracker.py
```

## Configuration

Edit `portfolio_config.json` to customize:

### Alert Settings
```json
{
  "alerts": {
    "portfolio_drop_threshold": -10.0,
    "portfolio_gain_threshold": 15.0,
    "individual_coin_threshold": 20.0
  }
}
```

### Update Frequency
```json
{
  "update_interval": 300,
  "export_settings": {
    "auto_export_csv": true,
    "export_interval_hours": 24
  }
}
```

## Usage Examples

### Adding Transactions
```python
from crypto_portfolio_tracker import CryptoPortfolioTracker

tracker = CryptoPortfolioTracker()

# Buy Bitcoin
tracker.add_transaction('BTC', 'bitcoin', 0.5, 45000, 'buy')

# Buy Ethereum
tracker.add_transaction('ETH', 'ethereum', 2.0, 3000, 'buy')

# Sell some Bitcoin
tracker.add_transaction('BTC', 'bitcoin', 0.1, 50000, 'sell')
```

### Sample Output
```
================================================================================
CRYPTO PORTFOLIO PERFORMANCE TRACKER
================================================================================
Last Updated: 2025-08-02 15:30:45
Total Holdings: 7 cryptocurrencies

==================================================
OVERALL PORTFOLIO PERFORMANCE
==================================================
Total Invested:      $52,500.00
Current Value:       $64,750.00
Unrealized P&L:      +$12,250.00 (+23.33%) [PROFIT]

========================================================================================================================
INDIVIDUAL HOLDINGS BREAKDOWN
========================================================================================================================
Symbol   Quantity     Avg Buy    Current    Value        P&L          P&L %    24h %    Alloc %
BTC      0.6000       $46,667.00 $115,550.00 $69,330.00  +$22,330.00  +47.50%  +2.15%   55.25%
ETH      3.5000       $3,142.86  $3,627.00   $12,694.50  +$1,694.50   +15.40%  +1.85%   23.15%
XRP      2500.0000    $1.20      $3.45       $8,625.00   +$5,625.00   +187.50% +12.30%  15.75%
```

## Files Structure

```
crypto-portfolio-tracker/
├── crypto_portfolio_tracker.py     # Main application
├── portfolio_config.json           # Configuration settings
├── portfolio_config.example.json   # Example configuration
├── demo_portfolio.json             # Demo portfolio data
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── .gitignore                       # Git ignore rules
└── screenshots/                     # Demo screenshots
    ├── portfolio_overview.png
    └── allocation_chart.png
```

## Commercial Applications

### For Individual Traders
- **Real-time P&L tracking** - See profits/losses instantly
- **Portfolio rebalancing** - Optimize allocation automatically  
- **Tax reporting** - Complete transaction history export
- **Risk management** - Alert-based monitoring system

### Integration Opportunities
- **Trading platforms** - Portfolio overlay service
- **Tax software** - Automated reporting integration
- **Mobile apps** - Real-time portfolio widgets
- **Investment advisors** - Client portfolio monitoring

## Technical Features

- **Event-driven architecture** - Efficient resource usage
- **Robust error handling** - Graceful API failure recovery
- **Data persistence** - State maintained across restarts
- **Configurable alerts** - Customizable notification thresholds
- **Export capabilities** - CSV and JSON data formats

## API Integration

Uses CoinGecko API for real-time cryptocurrency data:
- Price feeds for 7 major cryptocurrencies
- 24-hour change calculations
- Historical price analysis
- Rate limit compliance

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Roadmap

- [ ] Support for additional exchanges (Binance, Coinbase Pro)
- [ ] Technical indicator integration (RSI, MACD, Moving Averages)
- [ ] Web dashboard interface with real-time charts
- [ ] Mobile app notifications via push notifications
- [ ] DeFi protocol integration (staking rewards, liquidity pools)
- [ ] Machine learning price prediction module
- [ ] Multi-currency support (EUR, GBP, JPY)
- [ ] Portfolio comparison and benchmarking

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, feature requests, or bug reports, please open an issue on GitHub.

## Author

Built as part of autonomous system development research, demonstrating real-time monitoring and alert capabilities applicable to financial surveillance and trading systems.