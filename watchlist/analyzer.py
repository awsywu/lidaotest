import yfinance as yf
import pandas as pd
from datetime import datetime

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

    def calculate_macd(self, data, short_window=12, long_window=26, signal_window=9):
        data['EMA12'] = data['Close'].ewm(span=short_window, adjust=False).mean()
        data['EMA26'] = data['Close'].ewm(span=long_window, adjust=False).mean()
        data['MACD'] = data['EMA12'] - data['EMA26']
        data['Signal_Line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()
        return data

    def cross(self, series1, series2):
        return series1.iloc[-1] > series2.iloc[-1] and series1.iloc[-2] <= series2.iloc[-2]

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
        data = self.calculate_macd(data)

        latest = data.iloc[-1]
        results = {
            'bullish': latest['Close'] > latest['MA10'] > latest['MA20'] > latest['MA60'],
            'bearish': latest['Close'] < latest['MA60'],
            'below_ma10': latest['Close'] < latest['MA10'],
            'below_ma20': latest['Close'] < latest['MA20'],
            'death_cross': latest['MA5'] < latest['MA10'] and data['MA5'].iloc[-2] > data['MA10'].iloc[-2],
            'short_bottom': latest['Close'] > latest['MA10'] and latest['MA5'] >= data['MA5'].iloc[-2] and latest['K'] >= 50 and data['K'].iloc[-2] < 50,
            'J1': latest['J'] <= 1 and latest['MA20'] >= latest['MA60'] and latest['MA20'] >= data['MA20'].iloc[-2] and latest['MA60'] >= data['MA60'].iloc[-2] and latest['MA120'] < data['MA120'].iloc[-2],
            'J2': latest['J'] <= 1 and latest['MA20'] >= latest['MA60'] and latest['MA20'] >= data['MA20'].iloc[-2] and latest['MA60'] >= data['MA60'].iloc[-2] and latest['MA120'] >= data['MA120'].iloc[-2],
            'turning_point': latest['MA5'] < data['MA5'].iloc[-2] and latest['Close'] > data['Close'].iloc[-5] and data['Close'].iloc[-5] > data['Close'].iloc[-4] and data['Close'].iloc[-4] > data['Close'].iloc[-3],
            'break_zero': latest['J'] < 0 and latest['D'] > 50 and latest['DIF'] > latest['DEA'],
            'one_cross_three': self.cross(data['Close'], data['MA5']) and self.cross(data['Close'], data['MA10']) and self.cross(data['Close'], data['MA20']),
            'kdj_buy': latest['D'] > 50 and self.cross(data['MACD'], data['Signal_Line']) and data['J'].iloc[-2] <= 0 and data['J'].iloc[-1] > 0,
            'kdj_sell': latest['K'] < 10 and latest['D'] < 10
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
        turning_point_list = []
        break_zero_list = []
        one_cross_three_list = []
        kdj_buy_list = []
        kdj_sell_list = []

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
            if result['turning_point']:
                turning_point_list.append(ticker)
            if result['break_zero']:
                break_zero_list.append(ticker)
            if result['one_cross_three']:
                one_cross_three_list.append(ticker)
            if result['kdj_buy']:
                kdj_buy_list.append(ticker)
            if result['kdj_sell']:
                kdj_sell_list.append(ticker)

        return (bullish_list, bearish_list, reduce_position_list, clear_position_list, 
                short_bottom_list, J1_list, J2_list, turning_point_list, 
                break_zero_list, one_cross_three_list, kdj_buy_list, kdj_sell_list)

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
    results = analyzer.analyze()
    
    # Unpack the results
    (bullish_list, bearish_list, reduce_position_list, clear_position_list, 
     short_bottom_list, J1_list, J2_list, turning_point_list, 
     break_zero_list, one_cross_three_list, kdj_buy_list, kdj_sell_list) = results
    
    # Print the results
    print("多头排列 (Bullish Alignment):", bullish_list)
    print("强烈空头趋势 (Strong Bearish Trend):", bearish_list)
    print("减仓(破ma10):", reduce_position_list)
    print("清仓(破ma20):", clear_position_list)
    print("短底成型 (Short Bottom Formation):", short_bottom_list)
    print("J1 List:", J1_list)
    print("J2 List:", J2_list)
    print("拐点 (Turning Point):", turning_point_list)
    print("破零 (Break Zero):", break_zero_list)
    print("一穿三 (One Cross Three):", one_cross_three_list)
    print("KDJ 买点 (KDJ Buy Point):", kdj_buy_list)
    print("KDJ 超跌 (KDJ Sell Point):", kdj_sell_list)

if __name__ == "__main__":
    main()
