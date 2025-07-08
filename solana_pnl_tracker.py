#!/usr/bin/env python3
"""
Solana Wallet P&L Tracker
Tracks profit and loss for all tokens in a Solana wallet and exports to spreadsheet.
"""

import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal

import pandas as pd
import requests
from pycoingecko import CoinGeckoAPI
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.signature import Signature

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TokenTransaction:
    """Represents a token transaction"""
    signature: str
    timestamp: datetime
    token_mint: str
    token_symbol: str
    token_name: str
    amount: float
    transaction_type: str  # 'buy', 'sell', 'transfer_in', 'transfer_out'
    price_usd: Optional[float] = None
    value_usd: Optional[float] = None

@dataclass
class TokenPosition:
    """Represents current token position with P&L"""
    mint: str
    symbol: str
    name: str
    current_balance: float
    total_bought: float
    total_sold: float
    avg_buy_price: float
    total_invested: float
    current_value: float
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    current_price: float

class SolanaPnLTracker:
    """Main class for tracking Solana wallet P&L"""
    
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        """Initialize the tracker with Solana RPC client and CoinGecko API"""
        self.client = Client(rpc_url)
        self.cg = CoinGeckoAPI()
        self.token_cache = {}  # Cache for token metadata
        self.price_cache = {}  # Cache for historical prices
        
        # Common token mints and their CoinGecko IDs
        self.token_mapping = {
            "So11111111111111111111111111111111111111112": {"symbol": "SOL", "name": "Solana", "coingecko_id": "solana"},
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": {"symbol": "USDC", "name": "USD Coin", "coingecko_id": "usd-coin"},
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": {"symbol": "USDT", "name": "Tether", "coingecko_id": "tether"},
            "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E": {"symbol": "BTC", "name": "Bitcoin (Sollet)", "coingecko_id": "bitcoin"},
            "2FPyTwcZLUg1MDrwsyoP4D6s1tM7hAkHYRjkNb5w6Pxk": {"symbol": "ETH", "name": "Ethereum (Sollet)", "coingecko_id": "ethereum"},
            "SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt": {"symbol": "SRM", "name": "Serum", "coingecko_id": "serum"},
            "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R": {"symbol": "RAY", "name": "Raydium", "coingecko_id": "raydium"},
            "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So": {"symbol": "MSOL", "name": "Marinade SOL", "coingecko_id": "marinade-staked-sol"},
            "7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARj": {"symbol": "stSOL", "name": "Lido Staked SOL", "coingecko_id": "lido-staked-sol"},
        }
    
    def get_token_metadata(self, mint: str) -> Dict[str, str]:
        """Get token metadata (symbol, name) for a given mint"""
        if mint in self.token_cache:
            return self.token_cache[mint]
        
        if mint in self.token_mapping:
            metadata = self.token_mapping[mint]
            self.token_cache[mint] = metadata
            return metadata
        
        # Try to fetch from token registry or other sources
        # For simplicity, return unknown token info
        metadata = {
            "symbol": f"TOKEN_{mint[:8]}",
            "name": f"Unknown Token {mint[:8]}",
            "coingecko_id": None
        }
        self.token_cache[mint] = metadata
        return metadata
    
    def get_historical_price(self, coingecko_id: str, date: datetime) -> Optional[float]:
        """Get historical price for a token on a specific date"""
        if not coingecko_id:
            return None
        
        date_str = date.strftime("%d-%m-%Y")
        cache_key = f"{coingecko_id}_{date_str}"
        
        if cache_key in self.price_cache:
            return self.price_cache[cache_key]
        
        try:
            # Get historical data for the specific date
            historical_data = self.cg.get_coin_history_by_id(
                id=coingecko_id,
                date=date_str,
                localization=False
            )
            
            if 'market_data' in historical_data and 'current_price' in historical_data['market_data']:
                price = historical_data['market_data']['current_price'].get('usd', 0)
                self.price_cache[cache_key] = price
                return price
        except Exception as e:
            logger.warning(f"Failed to get historical price for {coingecko_id} on {date_str}: {e}")
        
        return None
    
    def get_current_prices(self, coingecko_ids: List[str]) -> Dict[str, float]:
        """Get current prices for multiple tokens"""
        try:
            # Filter out None values
            valid_ids = [id for id in coingecko_ids if id is not None]
            if not valid_ids:
                return {}
            
            prices = self.cg.get_price(ids=','.join(valid_ids), vs_currencies='usd')
            return {token_id: data['usd'] for token_id, data in prices.items()}
        except Exception as e:
            logger.error(f"Failed to get current prices: {e}")
            return {}
    
    def fetch_wallet_transactions(self, wallet_address: str, limit: int = 1000) -> List[TokenTransaction]:
        """Fetch and parse token transactions for a wallet"""
        try:
            pubkey = Pubkey.from_string(wallet_address)
            logger.info(f"Fetching transactions for wallet: {wallet_address}")
            
            # Get transaction signatures
            signatures_response = self.client.get_signatures_for_address(
                pubkey,
                limit=limit,
                commitment="confirmed"
            )
            
            if not signatures_response.value:
                logger.warning("No transactions found")
                return []
            
            transactions = []
            total_sigs = len(signatures_response.value)
            
            for i, sig_info in enumerate(signatures_response.value):
                logger.info(f"Processing transaction {i+1}/{total_sigs}")
                
                try:
                    # Get transaction details
                    tx_response = self.client.get_transaction(
                        Signature.from_string(sig_info.signature),
                        encoding="jsonParsed",
                        commitment="confirmed"
                    )
                    
                    if not tx_response.value:
                        continue
                    
                    tx_data = tx_response.value
                    timestamp = datetime.fromtimestamp(tx_data.block_time, timezone.utc)
                    
                    # Parse token transfers from the transaction
                    token_txs = self.parse_token_transfers(tx_data, wallet_address, timestamp)
                    transactions.extend(token_txs)
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Failed to process transaction {sig_info.signature}: {e}")
                    continue
            
            logger.info(f"Found {len(transactions)} token transactions")
            return sorted(transactions, key=lambda x: x.timestamp)
            
        except Exception as e:
            logger.error(f"Failed to fetch wallet transactions: {e}")
            return []
    
    def parse_token_transfers(self, tx_data, wallet_address: str, timestamp: datetime) -> List[TokenTransaction]:
        """Parse token transfers from a transaction"""
        transactions = []
        
        try:
            if not tx_data.transaction or not tx_data.transaction.message:
                return transactions
            
            instructions = tx_data.transaction.message.instructions
            
            for instruction in instructions:
                if hasattr(instruction, 'parsed') and instruction.parsed:
                    parsed = instruction.parsed
                    
                    if parsed.get('type') == 'transfer':
                        info = parsed.get('info', {})
                        
                        # Token transfer
                        if 'mint' in info:
                            mint = info['mint']
                            amount = float(info.get('tokenAmount', {}).get('uiAmount', 0))
                            source = info.get('source', '')
                            destination = info.get('destination', '')
                            
                            # Determine transaction type
                            if source == wallet_address:
                                tx_type = 'transfer_out'
                                amount = -amount
                            elif destination == wallet_address:
                                tx_type = 'transfer_in'
                            else:
                                continue
                            
                            metadata = self.get_token_metadata(mint)
                            
                            tx = TokenTransaction(
                                signature=str(tx_data.transaction.signatures[0]),
                                timestamp=timestamp,
                                token_mint=mint,
                                token_symbol=metadata['symbol'],
                                token_name=metadata['name'],
                                amount=amount,
                                transaction_type=tx_type
                            )
                            transactions.append(tx)
                        
                        # SOL transfer
                        elif 'lamports' in info:
                            amount = float(info['lamports']) / 1e9  # Convert lamports to SOL
                            source = info.get('source', '')
                            destination = info.get('destination', '')
                            
                            if source == wallet_address:
                                tx_type = 'transfer_out'
                                amount = -amount
                            elif destination == wallet_address:
                                tx_type = 'transfer_in'
                            else:
                                continue
                            
                            sol_metadata = self.get_token_metadata("So11111111111111111111111111111111111111112")
                            
                            tx = TokenTransaction(
                                signature=str(tx_data.transaction.signatures[0]),
                                timestamp=timestamp,
                                token_mint="So11111111111111111111111111111111111111112",
                                token_symbol=sol_metadata['symbol'],
                                token_name=sol_metadata['name'],
                                amount=amount,
                                transaction_type=tx_type
                            )
                            transactions.append(tx)
        
        except Exception as e:
            logger.warning(f"Failed to parse token transfers: {e}")
        
        return transactions
    
    def calculate_pnl(self, transactions: List[TokenTransaction]) -> List[TokenPosition]:
        """Calculate profit and loss for each token"""
        logger.info("Calculating P&L for tokens...")
        
        # Group transactions by token mint
        token_groups = {}
        for tx in transactions:
            if tx.token_mint not in token_groups:
                token_groups[tx.token_mint] = []
            token_groups[tx.token_mint].append(tx)
        
        positions = []
        
        # Get current prices for all tokens
        coingecko_ids = []
        for mint in token_groups.keys():
            metadata = self.get_token_metadata(mint)
            if metadata.get('coingecko_id'):
                coingecko_ids.append(metadata['coingecko_id'])
        
        current_prices = self.get_current_prices(coingecko_ids)
        
        for mint, txs in token_groups.items():
            metadata = self.get_token_metadata(mint)
            coingecko_id = metadata.get('coingecko_id')
            current_price = current_prices.get(coingecko_id, 0) if coingecko_id else 0
            
            # Calculate position metrics
            total_bought = 0
            total_sold = 0
            total_invested = 0
            total_received = 0
            current_balance = 0
            
            # Add historical prices to transactions
            for tx in txs:
                if tx.price_usd is None and coingecko_id:
                    tx.price_usd = self.get_historical_price(coingecko_id, tx.timestamp)
                    if tx.price_usd:
                        tx.value_usd = abs(tx.amount) * tx.price_usd
                
                current_balance += tx.amount
                
                if tx.amount > 0:  # Buying/receiving
                    total_bought += tx.amount
                    if tx.value_usd:
                        total_invested += tx.value_usd
                else:  # Selling/sending
                    total_sold += abs(tx.amount)
                    if tx.value_usd:
                        total_received += tx.value_usd
            
            # Calculate averages and P&L
            avg_buy_price = total_invested / total_bought if total_bought > 0 else 0
            current_value = current_balance * current_price if current_price > 0 else 0
            unrealized_pnl = current_value - (current_balance * avg_buy_price) if current_balance > 0 else 0
            realized_pnl = total_received - (total_sold * avg_buy_price) if total_sold > 0 else 0
            total_pnl = unrealized_pnl + realized_pnl
            
            position = TokenPosition(
                mint=mint,
                symbol=metadata['symbol'],
                name=metadata['name'],
                current_balance=current_balance,
                total_bought=total_bought,
                total_sold=total_sold,
                avg_buy_price=avg_buy_price,
                total_invested=total_invested,
                current_value=current_value,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl,
                total_pnl=total_pnl,
                current_price=current_price
            )
            
            positions.append(position)
        
        return sorted(positions, key=lambda x: abs(x.total_pnl), reverse=True)
    
    def export_to_spreadsheet(self, positions: List[TokenPosition], transactions: List[TokenTransaction], 
                            wallet_address: str, filename: str = None):
        """Export P&L data to Excel spreadsheet"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"solana_pnl_{wallet_address[:8]}_{timestamp}.xlsx"
        
        logger.info(f"Exporting data to {filename}")
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = []
            total_portfolio_value = 0
            total_invested = 0
            total_pnl = 0
            
            for pos in positions:
                if pos.current_balance > 0:  # Only include tokens with balance
                    summary_data.append({
                        'Token': pos.symbol,
                        'Name': pos.name,
                        'Balance': pos.current_balance,
                        'Current Price': f"${pos.current_price:.6f}",
                        'Current Value': f"${pos.current_value:.2f}",
                        'Avg Buy Price': f"${pos.avg_buy_price:.6f}",
                        'Total Invested': f"${pos.total_invested:.2f}",
                        'Unrealized P&L': f"${pos.unrealized_pnl:.2f}",
                        'Realized P&L': f"${pos.realized_pnl:.2f}",
                        'Total P&L': f"${pos.total_pnl:.2f}",
                        'P&L %': f"{(pos.total_pnl / pos.total_invested * 100) if pos.total_invested > 0 else 0:.2f}%"
                    })
                    total_portfolio_value += pos.current_value
                    total_invested += pos.total_invested
                    total_pnl += pos.total_pnl
            
            # Add portfolio summary
            summary_data.insert(0, {
                'Token': 'TOTAL PORTFOLIO',
                'Name': 'Summary',
                'Balance': '',
                'Current Price': '',
                'Current Value': f"${total_portfolio_value:.2f}",
                'Avg Buy Price': '',
                'Total Invested': f"${total_invested:.2f}",
                'Unrealized P&L': '',
                'Realized P&L': '',
                'Total P&L': f"${total_pnl:.2f}",
                'P&L %': f"{(total_pnl / total_invested * 100) if total_invested > 0 else 0:.2f}%"
            })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Portfolio Summary', index=False)
            
            # Detailed positions sheet
            positions_data = []
            for pos in positions:
                positions_data.append({
                    'Token Mint': pos.mint,
                    'Symbol': pos.symbol,
                    'Name': pos.name,
                    'Current Balance': pos.current_balance,
                    'Total Bought': pos.total_bought,
                    'Total Sold': pos.total_sold,
                    'Current Price': pos.current_price,
                    'Avg Buy Price': pos.avg_buy_price,
                    'Total Invested': pos.total_invested,
                    'Current Value': pos.current_value,
                    'Unrealized P&L': pos.unrealized_pnl,
                    'Realized P&L': pos.realized_pnl,
                    'Total P&L': pos.total_pnl
                })
            
            positions_df = pd.DataFrame(positions_data)
            positions_df.to_excel(writer, sheet_name='Detailed Positions', index=False)
            
            # Transactions sheet
            tx_data = []
            for tx in transactions:
                tx_data.append({
                    'Signature': tx.signature,
                    'Timestamp': tx.timestamp,
                    'Token': tx.token_symbol,
                    'Token Name': tx.token_name,
                    'Token Mint': tx.token_mint,
                    'Amount': tx.amount,
                    'Type': tx.transaction_type,
                    'Price USD': tx.price_usd,
                    'Value USD': tx.value_usd
                })
            
            tx_df = pd.DataFrame(tx_data)
            tx_df.to_excel(writer, sheet_name='All Transactions', index=False)
        
        logger.info(f"Data exported successfully to {filename}")
        return filename

def main():
    """Main function to run the P&L tracker"""
    print("🚀 Solana Wallet P&L Tracker")
    print("=" * 50)
    
    # Get wallet address from user
    wallet_address = input("Enter your Solana wallet address: ").strip()
    
    if not wallet_address:
        print("❌ No wallet address provided")
        return
    
    # Optional: Custom RPC URL
    rpc_url = input("Enter custom RPC URL (or press Enter for default): ").strip()
    if not rpc_url:
        rpc_url = "https://api.mainnet-beta.solana.com"
    
    # Initialize tracker
    print("\n📡 Initializing tracker...")
    tracker = SolanaPnLTracker(rpc_url)
    
    try:
        # Fetch transactions
        print("📈 Fetching wallet transactions...")
        transactions = tracker.fetch_wallet_transactions(wallet_address)
        
        if not transactions:
            print("❌ No transactions found or failed to fetch transactions")
            return
        
        # Calculate P&L
        print("💰 Calculating profit and loss...")
        positions = tracker.calculate_pnl(transactions)
        
        # Export to spreadsheet
        print("📊 Exporting to spreadsheet...")
        filename = tracker.export_to_spreadsheet(positions, transactions, wallet_address)
        
        # Display summary
        print("\n🎉 Analysis Complete!")
        print(f"📁 Data exported to: {filename}")
        print("\n📊 Portfolio Summary:")
        
        total_value = sum(pos.current_value for pos in positions if pos.current_balance > 0)
        total_invested = sum(pos.total_invested for pos in positions)
        total_pnl = sum(pos.total_pnl for pos in positions)
        
        print(f"   Total Portfolio Value: ${total_value:.2f}")
        print(f"   Total Invested: ${total_invested:.2f}")
        print(f"   Total P&L: ${total_pnl:.2f}")
        print(f"   Total P&L %: {(total_pnl / total_invested * 100) if total_invested > 0 else 0:.2f}%")
        
        print("\n🏆 Top Performers:")
        for i, pos in enumerate(positions[:5]):
            if pos.current_balance > 0:
                pnl_pct = (pos.total_pnl / pos.total_invested * 100) if pos.total_invested > 0 else 0
                print(f"   {i+1}. {pos.symbol}: ${pos.total_pnl:.2f} ({pnl_pct:.2f}%)")
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()