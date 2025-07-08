# 🚀 Solana Wallet P&L Tracker

A comprehensive Python tool to track profit and loss for all tokens in your Solana wallet and export the data to a spreadsheet.

## ✨ Features

- **📊 Complete P&L Analysis**: Track unrealized and realized gains/losses for all tokens
- **📈 Historical Price Data**: Automatically fetches historical prices using CoinGecko API
- **💼 Portfolio Overview**: Get a complete summary of your portfolio performance
- **📁 Excel Export**: Export all data to a formatted Excel spreadsheet with multiple sheets
- **🔄 Transaction History**: Detailed transaction history with timestamps and values
- **⚡ Automatic Token Detection**: Recognizes major Solana tokens (SOL, USDC, USDT, etc.)
- **🛡️ Rate Limiting**: Built-in rate limiting to respect API limits

## 📋 What You Get

The tool generates an Excel file with three sheets:

1. **Portfolio Summary**: Overview with current balances, P&L, and percentages
2. **Detailed Positions**: Complete position data for each token
3. **All Transactions**: Every transaction with historical prices and values

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- A Solana wallet address

### Option 1: Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/solana-pnl-tracker.git
cd solana-pnl-tracker

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Install as Package

```bash
# Install the package
pip install -e .

# Run from anywhere
solana-pnl
```

## 🚀 Usage

### Basic Usage

```bash
python solana_pnl_tracker.py
```

The script will prompt you for:
1. Your Solana wallet address
2. Optional: Custom RPC URL (press Enter for default)

### Example Output

```
🚀 Solana Wallet P&L Tracker
==================================================

Enter your Solana wallet address: YourWalletAddressHere
Enter custom RPC URL (or press Enter for default): 

📡 Initializing tracker...
📈 Fetching wallet transactions...
💰 Calculating profit and loss...
📊 Exporting to spreadsheet...

🎉 Analysis Complete!
📁 Data exported to: solana_pnl_YourWall_20250107_143052.xlsx

📊 Portfolio Summary:
   Total Portfolio Value: $12,345.67
   Total Invested: $10,000.00
   Total P&L: $2,345.67
   Total P&L %: 23.46%

🏆 Top Performers:
   1. SOL: $1,234.56 (45.67%)
   2. RAY: $567.89 (23.45%)
   3. MSOL: $234.56 (12.34%)
```

## 📊 Spreadsheet Structure

### Portfolio Summary Sheet
- Token symbol and name
- Current balance
- Current price and value
- Average buy price
- Total invested amount
- Unrealized P&L
- Realized P&L
- Total P&L and percentage

### Detailed Positions Sheet
- Complete position data
- Token mint addresses
- Buying/selling volumes
- Price calculations

### All Transactions Sheet
- Transaction signatures
- Timestamps
- Token details
- Transaction amounts and types
- Historical prices and USD values

## 🔧 Advanced Configuration

### Using Custom RPC

For better performance and reliability, consider using a premium RPC provider:

```python
# In the script or when prompted
rpc_url = "https://your-premium-rpc-url.com"
```

Recommended RPC providers:
- **Alchemy**: https://www.alchemy.com/solana
- **QuickNode**: https://www.quicknode.com/chains/sol
- **Helius**: https://www.helius.dev/
- **GetBlock**: https://getblock.io/nodes/sol/

### Supported Tokens

The tool automatically recognizes these major Solana tokens:

- **SOL** - Solana
- **USDC** - USD Coin
- **USDT** - Tether
- **BTC** - Bitcoin (Sollet)
- **ETH** - Ethereum (Sollet)
- **SRM** - Serum
- **RAY** - Raydium
- **MSOL** - Marinade Staked SOL
- **stSOL** - Lido Staked SOL

Other tokens will be detected as "Unknown Token" but still tracked.

## ⚠️ Important Notes

### Rate Limiting
- The tool includes built-in rate limiting for API calls
- Large wallets with many transactions may take time to process
- Consider using a premium RPC for faster processing

### Price Data Accuracy
- Historical prices are fetched from CoinGecko
- Some tokens may not have historical price data available
- Prices are in USD only

### Transaction Limits
- Default limit is 1000 transactions
- Can be modified in the code for wallets with more transactions

## 🔍 Troubleshooting

### Common Issues

**"No transactions found"**
- Verify your wallet address is correct
- Check if the wallet has any token transactions
- Try using a different RPC URL

**"Failed to get historical price"**
- Some tokens may not be listed on CoinGecko
- Historical data might not be available for very old transactions
- The tool will continue processing other tokens

**Slow Performance**
- Use a premium RPC provider
- Reduce the transaction limit if needed
- Large portfolios naturally take longer to process

### Error Handling
The tool includes comprehensive error handling and will:
- Continue processing even if some transactions fail
- Log warnings for missing price data
- Provide detailed error messages

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Support for more DEXs and transaction types
- Additional price data sources
- Better token metadata detection
- Portfolio analytics and charts
- Support for other blockchains

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for informational purposes only. Always verify the results and consult with a financial advisor for investment decisions. The accuracy of profit/loss calculations depends on the availability of historical price data.

## 🔗 Resources

- [Solana Documentation](https://docs.solana.com/)
- [CoinGecko API](https://www.coingecko.com/en/api)
- [Solana RPC Providers](https://docs.solana.com/cluster/rpc-endpoints)

---

**Happy tracking! 📈💰**