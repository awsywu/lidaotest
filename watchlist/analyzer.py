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
        data['DIF'] = data['EMA12'] - data['EMA26']
        data['DEA'] = data['DIF'].ewm(span=signal_window, adjust=False).mean()
        data['MACD'] = 2 * (data['DIF'] - data['DEA'])
        return data

    def calculate_rsi(self, data, period=14):
        delta = data['Close'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def cross(self, series1, series2):
        return series1.iloc[-1] > series2.iloc[-1] and series1.iloc[-2] <= series2.iloc[-2]

    def cross_down(self, series1, series2):
        return series1.iloc[-1] < series2.iloc[-1] and series1.iloc[-2] >= series2.iloc[-2]

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
        data['EMA4'] = data['Close'].ewm(span=4, adjust=False).mean()
        data['EMA8'] = data['Close'].ewm(span=8, adjust=False).mean()
        data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
        data['EMA21'] = data['Close'].ewm(span=21, adjust=False).mean()
        data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
        data['K'], data['D'], data['J'] = self.calculate_kdj(data)
        data = self.calculate_macd(data)
        data['RSI'] = self.calculate_rsi(data)

        latest = data.iloc[-1]
        results = {
            'bullish': latest['Close'] > latest['MA10'] > latest['MA20'] > latest['MA60'],
            'bearish': latest['Close'] < latest['MA60'],
            'below_ma10': latest['Close'] < latest['MA10'] and data['Close'].iloc[-2] > data['MA10'].iloc[-2],
            'below_ma20': latest['Close'] < latest['MA20'] and data['Close'].iloc[-2] > data['MA20'].iloc[-2],
            'death_cross': latest['MA5'] < latest['MA10'] and data['MA5'].iloc[-2] > data['MA10'].iloc[-2],
            'short_bottom': latest['Close'] > latest['MA10'] and latest['MA5'] >= data['MA5'].iloc[-2] and latest['K'] >= 50 and data['K'].iloc[-2] < 50,
            'J1': latest['J'] <= 1 and latest['MA20'] >= latest['MA60'] and latest['MA20'] >= data['MA20'].iloc[-2] and latest['MA60'] >= data['MA60'].iloc[-2] and latest['MA120'] < data['MA120'].iloc[-2],
            'J2': latest['J'] <= 1 and latest['MA20'] >= latest['MA60'] and latest['MA20'] >= data['MA20'].iloc[-2] and latest['MA60'] >= data['MA60'].iloc[-2] and latest['MA120'] >= data['MA120'].iloc[-2],
            'turning_point': latest['MA5'] < data['MA5'].iloc[-2] and latest['Close'] > data['Close'].iloc[-5] and data['Close'].iloc[-5] > data['Close'].iloc[-4] and data['Close'].iloc[-4] > data['Close'].iloc[-3],
            'break_zero': latest['J'] < 0 and latest['D'] > 50 and latest['DIF'] > latest['DEA'],
            'one_cross_three': self.cross(data['Close'], data['MA5']) and self.cross(data['Close'], data['MA10']) and self.cross(data['Close'], data['MA20']),
            'kdj_buy': latest['D'] > 50 and self.cross(data['DIF'], data['DEA']) and data['J'].iloc[-2] <= 0 and data['J'].iloc[-1] > 0,
            'kdj_sell': latest['K'] < 10 and latest['D'] < 10,
            'e4e12_death_cross': self.cross_down(data['EMA4'], data['EMA12']),
            'e4e50_death_cross': self.cross_down(data['EMA4'], data['EMA50']),
            'e8e21_death_cross': self.cross_down(data['EMA8'], data['EMA21']),
            'rsi80_overbought': latest['RSI'] >= 80 and data['RSI'].iloc[-2] < 80,
            'macd_death_cross': self.cross_down(data['DIF'], data['DEA']) and data['DIF'].iloc[-2] > data['DEA'].iloc[-2],
            'e4e12_golden_cross': self.cross(data['EMA4'], data['EMA12']),
            'e4e50_golden_cross': self.cross(data['EMA4'], data['EMA50']),
            'e8e21_golden_cross': self.cross(data['EMA8'], data['EMA21']),
            'rsi20_oversold': latest['RSI'] <= 20 and data['RSI'].iloc[-2] > 20,
            'macd_golden_cross': self.cross(data['DIF'], data['DEA']) and data['DIF'].iloc[-2] < data['DEA'].iloc[-2],
            'above_ma10': latest['Close'] > latest['MA10'] and data['Close'].iloc[-2] <= data['MA10'].iloc[-2],
            'below_ma10_first': latest['Close'] < latest['MA10'] and data['Close'].iloc[-2] >= data['MA10'].iloc[-2]
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
        e4e12_death_cross_list = []
        e4e50_death_cross_list = []
        e8e21_death_cross_list = []
        rsi80_overbought_list = []
        macd_death_cross_list = []
        e4e12_golden_cross_list = []
        e4e50_golden_cross_list = []
        e8e21_golden_cross_list = []
        rsi20_oversold_list = []
        macd_golden_cross_list = []
        above_ma10_list = []
        below_ma10_list = []

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
            if result['e4e12_death_cross']:
                e4e12_death_cross_list.append(ticker)
            if result['e4e50_death_cross']:
                e4e50_death_cross_list.append(ticker)
            if result['e8e21_death_cross']:
                e8e21_death_cross_list.append(ticker)
            if result['rsi80_overbought']:
                rsi80_overbought_list.append(ticker)
            if result['macd_death_cross']:
                macd_death_cross_list.append(ticker)
            if result['e4e12_golden_cross']:
                e4e12_golden_cross_list.append(ticker)
            if result['e4e50_golden_cross']:
                e4e50_golden_cross_list.append(ticker)
            if result['e8e21_golden_cross']:
                e8e21_golden_cross_list.append(ticker)
            if result['rsi20_oversold']:
                rsi20_oversold_list.append(ticker)
            if result['macd_golden_cross']:
                macd_golden_cross_list.append(ticker)
            if result['above_ma10']:
                above_ma10_list.append(ticker)
            if result['below_ma10_first']:
                below_ma10_list.append(ticker)

        return (bullish_list, bearish_list, reduce_position_list, clear_position_list,
                short_bottom_list, J1_list, J2_list, turning_point_list,
                break_zero_list, one_cross_three_list, kdj_buy_list, kdj_sell_list,
                e4e12_death_cross_list, e4e50_death_cross_list, e8e21_death_cross_list,
                rsi80_overbought_list, macd_death_cross_list,
                e4e12_golden_cross_list, e4e50_golden_cross_list, e8e21_golden_cross_list,
                rsi20_oversold_list, macd_golden_cross_list, above_ma10_list, below_ma10_list)

from watchlist_parser import WatchlistParser

def main():
    watchlist_file_1 = 'M_每日关注_36804.txt'
    watchlist_file_2 = 'M—观察筛选_18984.txt'
    
    parser = WatchlistParser(watchlist_file_1)
    watchlist_text = parser.read_watchlist()
    tickers = parser.extract_tickers(watchlist_text)
    analyzer = StockAnalyzer(tickers)
    results_1 = analyzer.analyze()

    parser = WatchlistParser(watchlist_file_2)
    watchlist_text = parser.read_watchlist()
    tickers = parser.extract_tickers(watchlist_text)
    analyzer = StockAnalyzer(tickers)
    results_2 = analyzer.analyze()

    print("Results for watchlist 1:")
    unpack_results(results_1)

    print("\nResults for watchlist 2:")
    unpack_results(results_2)

def unpack_results(results):
    (bullish_list, bearish_list, reduce_position_list, clear_position_list, 
     short_bottom_list, J1_list, J2_list, turning_point_list, 
     break_zero_list, one_cross_three_list, kdj_buy_list, kdj_sell_list,
     e4e12_death_cross_list, e4e50_death_cross_list, e8e21_death_cross_list,
     rsi80_overbought_list, macd_death_cross_list,
     e4e12_golden_cross_list, e4e50_golden_cross_list, e8e21_golden_cross_list,
     rsi20_oversold_list, macd_golden_cross_list, above_ma10_list, below_ma10_list) = results

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
    print("e4e12减四成 (EMA4 and EMA12 Death Cross):", e4e12_death_cross_list)
    print("e4e50清仓 (EMA4 and EMA50 Death Cross):", e4e50_death_cross_list)
    print("e8e21死叉 (EMA8 and EMA21 Death Cross):", e8e21_death_cross_list)
    print("RSI80超买 (RSI >= 80):", rsi80_overbought_list)
    print("macd死叉 (MACD Death Cross):", macd_death_cross_list)
    print("e4e12加四成 (EMA4 and EMA12 Golden Cross):", e4e12_golden_cross_list)
    print("e4e50满仓 (EMA4 and EMA50 Golden Cross):", e4e50_golden_cross_list)
    print("e8e21金叉 (EMA8 and EMA21 Golden Cross):", e8e21_golden_cross_list)
    print("RSI20超卖 (RSI <= 20):", rsi20_oversold_list)
    print("macd金叉 (MACD Golden Cross):", macd_golden_cross_list)
    print("ma10之上 (Close Above MA10):", above_ma10_list)
    print("ma10之下 (Close Below MA10):", below_ma10_list)

if __name__ == "__main__":
    main()
