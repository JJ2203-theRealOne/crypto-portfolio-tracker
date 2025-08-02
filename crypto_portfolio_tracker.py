import requests
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import csv

class CryptoPortfolioTracker:
    """Comprehensive cryptocurrency portfolio performance tracking system"""
    
    def __init__(self, config_file='portfolio_config.json'):
        self.api_url = "https://api.coingecko.com/api/v3/simple/price"
        self.history_url = "https://api.coingecko.com/api/v3/coins/{}/market_chart"
        self.config_file = config_file
        self.portfolio_file = 'portfolio_holdings.json'
        self.transactions_file = 'transactions_history.csv'
        self.performance_file = 'portfolio_performance.json'
        
        # Load configuration and portfolio
        self.config = self.load_config()
        self.portfolio = self.load_portfolio()
        self.performance_history = self.load_performance_history()
        
        # Current market data
        self.current_prices = {}
        self.price_history = {}
    
    def load_config(self) -> dict:
        """Load portfolio tracking configuration"""
        default_config = {
            'update_interval': 300,  # 5 minutes
            'display_currency': 'USD',
            'performance_tracking': {
                'track_24h_change': True,
                'track_7d_change': True,
                'track_30d_change': True,
                'track_all_time': True
            },
            'alerts': {
                'portfolio_drop_threshold': -10.0,  # Alert if portfolio drops 10%
                'portfolio_gain_threshold': 15.0,   # Alert if portfolio gains 15%
                'individual_coin_threshold': 20.0   # Alert if any coin moves 20%
            },
            'export_settings': {
                'auto_export_csv': True,
                'export_interval_hours': 24,
                'keep_history_days': 90
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    for key, value in loaded_config.items():
                        if isinstance(value, dict) and key in default_config and isinstance(default_config[key], dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                print(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
        else:
            print(f"Config file {self.config_file} not found, using defaults")
        
        return default_config
    
    def load_portfolio(self) -> dict:
        """Load portfolio holdings"""
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r') as f:
                    portfolio = json.load(f)
                    # Validate portfolio structure
                    if 'holdings' not in portfolio:
                        portfolio['holdings'] = {}
                    if 'total_invested' not in portfolio:
                        portfolio['total_invested'] = 0.0
                    return portfolio
            except Exception as e:
                print(f"Error loading portfolio: {e}, creating new portfolio")
        
        # Default empty portfolio
        return {
            'holdings': {},
            'total_invested': 0.0,
            'creation_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
    
    def load_performance_history(self) -> list:
        """Load historical performance data"""
        if os.path.exists(self.performance_file):
            try:
                with open(self.performance_file, 'r') as f:
                    history = json.load(f)
                    # Ensure it's a list
                    if isinstance(history, list):
                        return history
                    else:
                        print("Performance history file corrupted, starting fresh")
                        return []
            except Exception as e:
                print(f"Error loading performance history: {e}")
        return []
    
    def save_portfolio(self):
        """Save portfolio holdings"""
        try:
            self.portfolio['last_updated'] = datetime.now().isoformat()
            with open(self.portfolio_file, 'w') as f:
                json.dump(self.portfolio, f, indent=2)
        except Exception as e:
            print(f"Error saving portfolio: {e}")
    
    def save_performance_history(self):
        """Save performance history"""
        try:
            with open(self.performance_file, 'w') as f:
                json.dump(self.performance_history, f, indent=2)
        except Exception as e:
            print(f"Error saving performance history: {e}")
    
    def add_transaction(self, coin_symbol: str, coin_id: str, quantity: float, 
                       price_per_coin: float, transaction_type: str = 'buy'):
        """Add a buy/sell transaction to portfolio"""
        # Validate inputs
        if quantity <= 0:
            print(f"Error: Quantity must be positive, got {quantity}")
            return False
        
        if price_per_coin <= 0:
            print(f"Error: Price must be positive, got {price_per_coin}")
            return False
        
        timestamp = datetime.now().isoformat()
        
        # Update holdings
        if coin_symbol not in self.portfolio['holdings']:
            self.portfolio['holdings'][coin_symbol] = {
                'coin_id': coin_id,
                'total_quantity': 0.0,
                'average_buy_price': 0.0,
                'total_invested': 0.0,
                'transactions': []
            }
        
        holding = self.portfolio['holdings'][coin_symbol]
        transaction_value = quantity * price_per_coin
        
        if transaction_type.lower() == 'buy':
            # Calculate new average buy price
            old_total_value = holding['total_invested']
            old_quantity = holding['total_quantity']
            
            new_total_value = old_total_value + transaction_value
            new_quantity = old_quantity + quantity
            
            if new_quantity > 0:
                holding['average_buy_price'] = new_total_value / new_quantity
            
            holding['total_quantity'] = new_quantity
            holding['total_invested'] = new_total_value
            self.portfolio['total_invested'] += transaction_value
            
        elif transaction_type.lower() == 'sell':
            if holding['total_quantity'] >= quantity:
                # Proportional reduction in invested amount
                if holding['total_quantity'] > 0:
                    sell_ratio = quantity / holding['total_quantity']
                    invested_reduction = holding['total_invested'] * sell_ratio
                    
                    holding['total_quantity'] -= quantity
                    holding['total_invested'] -= invested_reduction
                    self.portfolio['total_invested'] -= invested_reduction
                    
                    # Remove holding if quantity becomes zero
                    if holding['total_quantity'] <= 0.0001:  # Account for floating point precision
                        holding['total_quantity'] = 0.0
                        holding['total_invested'] = 0.0
                else:
                    print(f"Error: No {coin_symbol} to sell")
                    return False
            else:
                print(f"Error: Cannot sell {quantity} {coin_symbol}, only have {holding['total_quantity']}")
                return False
        else:
            print(f"Error: Invalid transaction type '{transaction_type}'. Use 'buy' or 'sell'")
            return False
        
        # Record transaction
        transaction = {
            'timestamp': timestamp,
            'type': transaction_type,
            'quantity': quantity,
            'price_per_coin': price_per_coin,
            'total_value': transaction_value
        }
        
        holding['transactions'].append(transaction)
        
        # Save to CSV
        self.save_transaction_to_csv(coin_symbol, transaction)
        self.save_portfolio()
        
        print(f"Transaction recorded: {transaction_type.upper()} {quantity} {coin_symbol} at ${price_per_coin:.2f}")
        return True
    
    def save_transaction_to_csv(self, coin_symbol: str, transaction: dict):
        """Save transaction to CSV file"""
        file_exists = os.path.exists(self.transactions_file)
        
        try:
            with open(self.transactions_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                if not file_exists:
                    writer.writerow(['timestamp', 'coin', 'type', 'quantity', 'price_per_coin', 'total_value'])
                
                writer.writerow([
                    transaction['timestamp'],
                    coin_symbol,
                    transaction['type'],
                    transaction['quantity'],
                    transaction['price_per_coin'],
                    transaction['total_value']
                ])
        except Exception as e:
            print(f"Error saving transaction to CSV: {e}")
    
    def get_current_prices(self) -> bool:
        """Fetch current prices for all coins in portfolio"""
        if not self.portfolio['holdings']:
            print("No holdings in portfolio")
            return False
        
        # Filter out holdings with zero quantity
        active_holdings = {k: v for k, v in self.portfolio['holdings'].items() if v['total_quantity'] > 0}
        
        if not active_holdings:
            print("No active holdings in portfolio")
            return False
        
        try:
            coin_ids = [holding['coin_id'] for holding in active_holdings.values()]
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
            
            print(f"Fetching prices for {len(coin_ids)} coins...")
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Map prices to symbols
            self.current_prices = {}
            for symbol, holding in active_holdings.items():
                coin_id = holding['coin_id']
                if coin_id in data and 'usd' in data[coin_id]:
                    self.current_prices[symbol] = {
                        'current_price': data[coin_id]['usd'],
                        'price_change_24h': data[coin_id].get('usd_24h_change', 0)
                    }
                else:
                    print(f"Warning: Could not get price for {coin_id}")
            
            print(f"Successfully fetched prices for {len(self.current_prices)} coins")
            return len(self.current_prices) > 0
            
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching prices: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error fetching prices: {e}")
            return False
    
    def calculate_portfolio_performance(self) -> dict:
        """Calculate comprehensive portfolio performance metrics"""
        if not self.get_current_prices():
            return {}
        
        total_current_value = 0.0
        total_invested = self.portfolio['total_invested']
        portfolio_breakdown = []
        
        for symbol, holding in self.portfolio['holdings'].items():
            # Only process holdings with quantity > 0
            if symbol in self.current_prices and holding['total_quantity'] > 0:
                current_price = self.current_prices[symbol]['current_price']
                current_value = holding['total_quantity'] * current_price
                invested_value = holding['total_invested']
                
                pnl = current_value - invested_value
                pnl_percentage = (pnl / invested_value * 100) if invested_value > 0 else 0
                
                price_change_24h = self.current_prices[symbol]['price_change_24h']
                
                coin_performance = {
                    'symbol': symbol,
                    'quantity': holding['total_quantity'],
                    'average_buy_price': holding['average_buy_price'],
                    'current_price': current_price,
                    'invested_value': invested_value,
                    'current_value': current_value,
                    'unrealized_pnl': pnl,
                    'pnl_percentage': pnl_percentage,
                    'price_change_24h': price_change_24h,
                    'allocation_percentage': 0  # Will calculate after total
                }
                
                portfolio_breakdown.append(coin_performance)
                total_current_value += current_value
        
        # Calculate allocation percentages
        for coin in portfolio_breakdown:
            if total_current_value > 0:
                coin['allocation_percentage'] = (coin['current_value'] / total_current_value) * 100
        
        # Overall portfolio metrics
        total_pnl = total_current_value - total_invested
        total_pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        performance = {
            'timestamp': datetime.now().isoformat(),
            'total_invested': total_invested,
            'total_current_value': total_current_value,
            'total_unrealized_pnl': total_pnl,
            'total_pnl_percentage': total_pnl_percentage,
            'portfolio_breakdown': portfolio_breakdown,
            'number_of_holdings': len(portfolio_breakdown)
        }
        
        # Save performance snapshot
        self.performance_history.append(performance)
        
        # Keep only recent history to prevent file from growing too large
        max_history_entries = 1000  # Reasonable limit
        if len(self.performance_history) > max_history_entries:
            self.performance_history = self.performance_history[-max_history_entries:]
        
        # Also keep by date
        cutoff_date = datetime.now() - timedelta(days=self.config['export_settings']['keep_history_days'])
        self.performance_history = [
            p for p in self.performance_history 
            if datetime.fromisoformat(p['timestamp']) > cutoff_date
        ]
        
        self.save_performance_history()
        return performance
    
    def display_portfolio_summary(self, performance: dict):
        """Display comprehensive portfolio summary"""
        if not performance:
            print("No performance data to display")
            return
            
        print(f"\n{'='*80}")
        print(f"CRYPTO PORTFOLIO PERFORMANCE TRACKER")
        print(f"{'='*80}")
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Holdings: {performance['number_of_holdings']} cryptocurrencies")
        
        # Overall Performance
        print(f"\n{'='*50}")
        print(f"OVERALL PORTFOLIO PERFORMANCE")
        print(f"{'='*50}")
        print(f"Total Invested:      ${performance['total_invested']:,.2f}")
        print(f"Current Value:       ${performance['total_current_value']:,.2f}")
        
        pnl = performance['total_unrealized_pnl']
        pnl_pct = performance['total_pnl_percentage']
        pnl_color = "PROFIT" if pnl >= 0 else "LOSS"
        print(f"Unrealized P&L:      ${pnl:,.2f} ({pnl_pct:+.2f}%) [{pnl_color}]")
        
        # Individual Holdings
        if performance['portfolio_breakdown']:
            print(f"\n{'='*120}")
            print(f"INDIVIDUAL HOLDINGS BREAKDOWN")
            print(f"{'='*120}")
            print(f"{'Symbol':<8} {'Quantity':<12} {'Avg Buy':<10} {'Current':<10} {'Value':<12} {'P&L':<12} {'P&L %':<8} {'24h %':<8} {'Alloc %':<8}")
            print(f"{'-'*120}")
            
            # Sort by allocation percentage
            sorted_holdings = sorted(performance['portfolio_breakdown'], 
                                   key=lambda x: x['allocation_percentage'], reverse=True)
            
            for holding in sorted_holdings:
                pnl_sign = "+" if holding['unrealized_pnl'] >= 0 else ""
                print(f"{holding['symbol']:<8} "
                      f"{holding['quantity']:<12.4f} "
                      f"${holding['average_buy_price']:<9.2f} "
                      f"${holding['current_price']:<9.2f} "
                      f"${holding['current_value']:<11.2f} "
                      f"{pnl_sign}${holding['unrealized_pnl']:<11.2f} "
                      f"{holding['pnl_percentage']:+7.2f}% "
                      f"{holding['price_change_24h']:+7.2f}% "
                      f"{holding['allocation_percentage']:7.2f}%")
            
            print(f"{'-'*120}")
        else:
            print("\nNo active holdings to display")
    
    def display_allocation_chart(self, performance: dict):
        """Display simple text-based allocation chart"""
        if not performance or not performance['portfolio_breakdown']:
            return
            
        print(f"\n{'='*50}")
        print(f"PORTFOLIO ALLOCATION")
        print(f"{'='*50}")
        
        sorted_holdings = sorted(performance['portfolio_breakdown'], 
                               key=lambda x: x['allocation_percentage'], reverse=True)
        
        for holding in sorted_holdings:
            percentage = holding['allocation_percentage']
            bar_length = max(1, int(percentage / 2))  # Ensure at least 1 character
            bar_length = min(bar_length, 50)  # Cap at 50 characters
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"{holding['symbol']:<8} {percentage:6.2f}% |{bar}| ${holding['current_value']:,.0f}")
    
    def check_alerts(self, performance: dict):
        """Check for portfolio alerts"""
        if not performance:
            return
            
        alerts = []
        
        # Portfolio-wide alerts
        total_pnl_pct = performance['total_pnl_percentage']
        
        if total_pnl_pct <= self.config['alerts']['portfolio_drop_threshold']:
            alerts.append({
                'type': 'PORTFOLIO_DROP',
                'message': f"Portfolio down {abs(total_pnl_pct):.2f}%",
                'severity': 'HIGH'
            })
        
        if total_pnl_pct >= self.config['alerts']['portfolio_gain_threshold']:
            alerts.append({
                'type': 'PORTFOLIO_GAIN',
                'message': f"Portfolio up {total_pnl_pct:.2f}%",
                'severity': 'MEDIUM'
            })
        
        # Individual coin alerts
        for holding in performance['portfolio_breakdown']:
            price_change = holding['price_change_24h']
            threshold = self.config['alerts']['individual_coin_threshold']
            
            if abs(price_change) >= threshold:
                direction = "surged" if price_change > 0 else "dropped"
                alerts.append({
                    'type': 'COIN_MOVEMENT',
                    'message': f"{holding['symbol']} {direction} {abs(price_change):.2f}% in 24h",
                    'severity': 'MEDIUM'
                })
        
        # Display alerts
        if alerts:
            print(f"\n{'!'*60}")
            print(f"PORTFOLIO ALERTS")
            print(f"{'!'*60}")
            for alert in alerts:
                print(f"[{alert['severity']}] {alert['message']}")
            print(f"{'!'*60}")
    
    def export_performance_csv(self):
        """Export portfolio performance to CSV"""
        try:
            filename = f"portfolio_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write headers
                writer.writerow([
                    'timestamp', 'symbol', 'quantity', 'avg_buy_price', 'current_price',
                    'invested_value', 'current_value', 'unrealized_pnl', 'pnl_percentage',
                    'price_change_24h', 'allocation_percentage'
                ])
                
                # Write latest performance data
                if self.performance_history:
                    latest = self.performance_history[-1]
                    for holding in latest['portfolio_breakdown']:
                        writer.writerow([
                            latest['timestamp'],
                            holding['symbol'],
                            holding['quantity'],
                            holding['average_buy_price'],
                            holding['current_price'],
                            holding['invested_value'],
                            holding['current_value'],
                            holding['unrealized_pnl'],
                            holding['pnl_percentage'],
                            holding['price_change_24h'],
                            holding['allocation_percentage']
                        ])
            
            print(f"Performance exported to {filename}")
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
    
    def run_portfolio_tracker(self):
        """Main portfolio tracking loop"""
        print("Crypto Portfolio Performance Tracker Starting...")
        print(f"Update interval: {self.config['update_interval']} seconds")
        print(f"Portfolio holdings: {len(self.portfolio['holdings'])} coins")
        print("Press Ctrl+C to stop\n")
        
        # Check if portfolio is empty
        active_holdings = {k: v for k, v in self.portfolio['holdings'].items() if v['total_quantity'] > 0}
        if not active_holdings:
            print("No active holdings found. Add some transactions first!")
            print("Example: tracker.add_transaction('BTC', 'bitcoin', 0.1, 50000, 'buy')")
            return
        
        try:
            update_counter = 0
            while True:
                # Calculate and display performance
                performance = self.calculate_portfolio_performance()
                
                if performance:
                    self.display_portfolio_summary(performance)
                    self.display_allocation_chart(performance)
                    self.check_alerts(performance)
                    
                    # Auto-export if enabled
                    if self.config['export_settings']['auto_export_csv']:
                        export_interval = self.config['export_settings']['export_interval_hours'] * 3600
                        update_interval = self.config['update_interval']
                        if update_counter > 0 and (update_counter * update_interval) % export_interval == 0:
                            self.export_performance_csv()
                else:
                    print("Failed to calculate performance - will retry next cycle")
                
                print(f"\nNext update in {self.config['update_interval']} seconds...")
                time.sleep(self.config['update_interval'])
                update_counter += 1
                
        except KeyboardInterrupt:
            print("\n\nPortfolio tracker stopped")
            print(f"Total performance snapshots: {len(self.performance_history)}")
            
            # Final export
            if self.performance_history:
                self.export_performance_csv()
                print("Final performance data exported")
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")
            self.save_portfolio()
            self.save_performance_history()


def setup_demo_portfolio():
    """Setup a demo portfolio for testing"""
    tracker = CryptoPortfolioTracker()
    
    print("Setting up demo portfolio...")
    
    # Add some sample transactions
    transactions = [
        ('BTC', 'bitcoin', 0.5, 45000, 'buy'),
        ('ETH', 'ethereum', 2.0, 3000, 'buy'),
        ('SOL', 'solana', 10.0, 150, 'buy'),
        ('ADA', 'cardano', 1000.0, 0.50, 'buy'),
        ('BTC', 'bitcoin', 0.1, 50000, 'buy'),  # Additional BTC buy
    ]
    
    for symbol, coin_id, quantity, price, tx_type in transactions:
        success = tracker.add_transaction(symbol, coin_id, quantity, price, tx_type)
        if not success:
            print(f"Failed to add transaction: {symbol}")
    
    print("Demo portfolio created!")
    print(f"Total invested: ${tracker.portfolio['total_invested']:,.2f}")
    return tracker


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        # Setup demo portfolio
        tracker = setup_demo_portfolio()
    else:
        # Load existing portfolio
        tracker = CryptoPortfolioTracker()
    
    # Run the tracker
    tracker.run_portfolio_tracker()