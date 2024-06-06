import yfinance as yf
import pandas as pd

class TickerAnalyzer:
    def __init__(self, tickers):
        self.tickers = tickers

    def analyze_ticker(self, ticker):
        data = yf.download(ticker, period='6mo', interval='1d')
        data['EMA10'] = data['Close'].ewm(span=10, adjust=False).mean()
        data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
        data['EMA60'] = data['Close'].ewm(span=60, adjust=False).mean()
        
        latest = data.iloc[-1]
        if latest['Close'] > latest['EMA10'] > latest['EMA20'] > latest['EMA60']:
            return '多头排列'
        elif latest['Close'] < latest['EMA60']:
            return '强烈空头趋势'
        else:
            return None

    def analyze(self):
        bullish_list = []
        bearish_list = []
        for ticker in self.tickers:
            result = self.analyze_ticker(ticker)
            if result == '多头排列':
                bullish_list.append(ticker)
            elif result == '强烈空头趋势':
                bearish_list.append(ticker)
        return bullish_list, bearish_list
