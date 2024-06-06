from watchlist_parser import WatchlistParser
from ticker_bullish_bearish import TickerAnalyzer

def main():
    # Initialize WatchlistParser with the path to the file
    watchlist_file = 'watchlist.txt'  # Replace with your actual file path
    parser = WatchlistParser(watchlist_file)
    
    # Read and extract tickers from the watchlist
    watchlist_text = parser.read_watchlist()
    tickers = parser.extract_tickers(watchlist_text)
    
    # Initialize TickerAnalyzer with the extracted tickers
    analyzer = TickerAnalyzer(tickers)
    
    # Analyze the tickers
    bullish_list, bearish_list = analyzer.analyze()
    
    # Print the results
    print("多头排列 (Bullish Alignment):", bullish_list)
    print("强烈空头趋势 (Strong Bearish Trend):", bearish_list)

if __name__ == "__main__":
    main()
