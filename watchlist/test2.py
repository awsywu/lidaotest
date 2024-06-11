import yfinance as yf
import pandas as pd
import datetime

def calculate_kdj(data, n=9, k_period=3, d_period=3):
    low_min = data['Low'].rolling(window=n, min_periods=1).min()
    high_max = data['High'].rolling(window=n, min_periods=1).max()
    rsv = (data['Close'] - low_min) / (high_max - low_min) * 100

    k = rsv.ewm(com=(k_period - 1), min_periods=1).mean()
    d = k.ewm(com=(d_period - 1), min_periods=1).mean()
    j = 3 * k - 2 * d

    return k, d, j

def short_bottom_formation(data):
    data['MA10'] = data['Close'].rolling(window=10).mean()
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['K'], data['D'], data['J'] = calculate_kdj(data)

    condition = (
        (data['Close'] > data['MA10']) &
        (data['MA5'] >= data['MA5'].shift(1)) &
        (data['K'] >= 50) &
        (data['K'].shift(1) < 50)
    )
    return condition

def check_watchlist(watchlist, start_date, end_date):
    tickers_meeting_criteria = []

    for ticker in watchlist:
        data = yf.download(ticker, start=start_date, end=end_date)
        if not data.empty:
            data['Condition'] = short_bottom_formation(data)
            dates_meeting_criteria = data.index[data['Condition']].tolist()
            for date in dates_meeting_criteria:
                tickers_meeting_criteria.append({'Ticker': ticker, 'Date': date})

    return tickers_meeting_criteria

# Define your watchlist here
watchlist = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']  # Example watchlist

# Define the date range for the last 2 years
end_date = datetime.datetime.now().date()
start_date = end_date - datetime.timedelta(days=2*365)

# Find tickers meeting the "短底成型" criteria in the last 2 years
tickers_meeting_criteria = check_watchlist(watchlist, start_date, end_date)

# Print results
print("Tickers meeting '短底成型' criteria in the last 2 years:")
for record in tickers_meeting_criteria:
    print(f"Ticker: {record['Ticker']}, Date: {record['Date']}")

