import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class StockAnalyzer:
    def __init__(self, tickers):
        self.tickers = tickers

    def calculate_kdj(self, data, n=9, k_period=3, d_period=3):
        low_min = data['Low'].rolling(window=n, min_periods=1).min()
        high_max = data['High'].rolling(window=n, min_periods=1).max()
        rsv = (data['Close'] - low_min) / (high_max - low_min) * 100

        k = rsv.ewm(com=(k_period - 1), min_periods=1).mean()
        d = k.ewm(com=(d_period - 1), min_periods=1).mean()
        j = 3 * k - 2 * d

        return k, d, j

    def analyze_ticker(self, ticker):
        data = yf.download(ticker, period='6mo', interval='1d')

        # Check if the latest available data is for today
        latest_date = data.index[-1].date()
        today_date = datetime.now().date()

        if latest_date < today_date:
            print(f"Data for {ticker} is not yet updated for today ({today_date}). Latest available data is for {latest_date}.")
        else:
            print(f"***Data for {ticker} is updated for today ({today_date})")

        data['MA5'] = data['Close'].rolling(window=5).mean()
        data['MA10'] = data['Close'].rolling(window=10).mean()
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['MA30'] = data['Close'].rolling(window=30).mean()
        data['MA60'] = data['Close'].rolling(window=60).mean()
        data['MA120'] = data['Close'].rolling(window=120).mean()
        data['MA250'] = data['Close'].rolling(window=250).mean()
        data['MA500'] = data['Close'].rolling(window=500).mean()
        data['MA1000'] = data['Close'].rolling(window=1000).mean()
        data['K'], data['D'], data['J'] = self.calculate_kdj(data)

        latest = data.iloc[-1]
        results = {
            'bullish': latest['Close'] > latest['MA10'] > latest['MA20'] > latest['MA60'],
            'bearish': latest['Close'] < latest['MA60'],
            'below_ma10': latest['Close'] < latest['MA10'],
            'below_ma20': latest['Close'] < latest['MA20'],
            'death_cross': latest['MA5'] < latest['MA10'] and data['MA5'].iloc[-2] > data['MA10'].iloc[-2],
            'short_bottom': latest['Close'] > latest['MA10'] and latest['MA5'] >= data['MA5'].iloc[-2] and latest['K'] >= 50 and data['K'].iloc[-2] < 50,
            'J1': latest['J'] <= 1 and latest['MA20'] >= latest['MA60'] and latest['MA20'] >= data['MA20'].iloc[-2] and latest['MA60'] >= data['MA60'].iloc[-2] and latest['MA120'] < data['MA120'].iloc[-2],
            'J2': latest['J'] <= 1 and latest['MA20'] >= latest['MA60'] and latest['MA20'] >= data['MA20'].iloc[-2] and latest['MA60'] >= data['MA60'].iloc[-2] and latest['MA120'] >= data['MA120'].iloc[-2]
        }
        return results

    def analyze(self):
        bullish_list = []
        bearish_list = []
        reduce_position_list = []
        clear_position_list = []
        short_bottom_list = []
        J1_list = []
        J2_list = []

        for ticker in self.tickers:
            result = self.analyze_ticker(ticker)
            if result['bullish']:
                bullish_list.append(ticker)
            if result['bearish']:
                bearish_list.append(ticker)
            if result['below_ma10'] and result['death_cross']:
                reduce_position_list.append(ticker)
            if result['below_ma20']:
                clear_position_list.append(ticker)
            if result['short_bottom']:
                short_bottom_list.append(ticker)
            if result['J1']:
                J1_list.append(ticker)
            if result['J2']:
                J2_list.append(ticker)

        return bullish_list, bearish_list, reduce_position_list, clear_position_list, short_bottom_list, J1_list, J2_list

from watchlist_parser import WatchlistParser

def main():
    # Initialize WatchlistParser with the path to the file
    watchlist_file = 'watchlist.txt'  # Replace with your actual file path
    parser = WatchlistParser(watchlist_file)
    
    # Read and extract tickers from the watchlist
    watchlist_text = parser.read_watchlist()
    tickers = parser.extract_tickers(watchlist_text)
    
    # Initialize the analyzer with the extracted tickers
    analyzer = StockAnalyzer(tickers)
    
    # Analyze the tickers
    bullish_list, bearish_list, reduce_position_list, clear_position_list, short_bottom_list, J1_list, J2_list = analyzer.analyze()
    
    # Print the results
    print("多头排列 (Bullish Alignment):", bullish_list)
    print("强烈空头趋势 (Strong Bearish Trend):", bearish_list)
    print("减仓(破ma10):", reduce_position_list)
    print("清仓(破ma20):", clear_position_list)
    print("短底成型 (Short Bottom Formation):", short_bottom_list)
    print("J1 List:", J1_list)
    print("J2 List:", J2_list)

if __name__ == "__main__":
    main()
