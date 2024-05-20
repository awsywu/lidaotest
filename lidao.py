import yfinance as yf
import matplotlib.pyplot as plt

# Fetch the data
qqq = yf.Ticker("QQQ")
data = qqq.history(period="1mo")  # You can change the period as needed

# Plot the closing prices
plt.figure(figsize=(10, 5))
plt.plot(data.index, data['Close'], label='QQQ Closing Price')
plt.title('Daily Closing Prices of QQQ')
plt.xlabel('Date')
plt.ylabel('Closing Price (USD)')
plt.legend()
plt.grid(True)
plt.show()