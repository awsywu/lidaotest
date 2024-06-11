from watchlist_parser import WatchlistParser
from ticker_bullish_bearish import StockAnalyzer
from duandi import DuanDi

def main():
    # Initialize WatchlistParser with the path to the file
    watchlist_file = 'watchlist.txt'  # Replace with your actual file path
    parser = WatchlistParser(watchlist_file)
    
    # Read and extract tickers from the watchlist
    watchlist_text = parser.read_watchlist()
    tickers = parser.extract_tickers(watchlist_text)
    
    # Initialize TickerAnalyzer with the extracted tickers
    analyzer = StockAnalyzer(tickers)
    
    # Analyze the tickers
    bullish_list, bearish_list, reduce_position_list, clear_position_list = analyzer.analyze()
    
    # Print the results
    print("多头排列 (Bullish Alignment):", bullish_list)
    print("强烈空头趋势 (Strong Bearish Trend):", bearish_list)
    print("减仓(破ma10): ", reduce_position_list)
    print("清仓(破ma20): ", clear_position_list)
    # Initialize DuanDi and check for short bottom formation
    checker = DuanDi(watchlist_file)
    short_bottom_tickers = checker.get_duandi()
    
    # Print the results for short bottom formation
    print("短底成型 (Short Bottom Formation):", short_bottom_tickers)

if __name__ == "__main__":
    main()