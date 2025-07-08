#!/usr/bin/env python3
"""
Example configuration file for Solana P&L Tracker
Copy this file to config.py and customize the settings
"""

# RPC Configuration
# For better performance, use a premium RPC provider
DEFAULT_RPC_URL = "https://api.mainnet-beta.solana.com"

# Premium RPC options (uncomment to use):
# DEFAULT_RPC_URL = "https://solana-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
# DEFAULT_RPC_URL = "https://YOUR_ENDPOINT.solana.quiknode.pro/YOUR_TOKEN"
# DEFAULT_RPC_URL = "https://rpc.helius.xyz/?api-key=YOUR_API_KEY"

# Transaction Limits
MAX_TRANSACTIONS = 1000  # Increase for wallets with more history

# Price Data Configuration
ENABLE_HISTORICAL_PRICES = True
PRICE_CACHE_ENABLED = True

# Export Settings
DEFAULT_EXPORT_FORMAT = "xlsx"  # xlsx or csv
INCLUDE_ZERO_BALANCES = False  # Include tokens with zero balance
INCLUDE_DUST = True  # Include very small amounts

# Rate Limiting (seconds between API calls)
RPC_DELAY = 0.1
COINGECKO_DELAY = 0.2

# Additional Token Mappings
# Add custom token mappings here for tokens not in the default list
CUSTOM_TOKEN_MAPPING = {
    # "TOKEN_MINT_ADDRESS": {
    #     "symbol": "TOKEN_SYMBOL", 
    #     "name": "Token Name", 
    #     "coingecko_id": "coingecko-token-id"
    # },
    # Example:
    # "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": {
    #     "symbol": "BONK", 
    #     "name": "Bonk", 
    #     "coingecko_id": "bonk"
    # }
}

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_FILENAME = "solana_pnl.log"

# Display Settings
SHOW_PROGRESS = True
DISPLAY_CURRENCY = "USD"
DECIMAL_PLACES = 6