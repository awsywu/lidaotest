import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

# Fetching the QQQ data starting from a specific date
start_date = '2024-05-01'
qqq_data = yf.download('QQQ', start=start_date)

# Filtering the 'Close' prices
closing_prices = qqq_data['Close']

# Setting up the plot
plt.figure(figsize=(10, 5))
plt.plot(closing_prices.index, closing_prices, linestyle='-', marker='o', color='b', markersize=5)
plt.title('Daily Closing Prices of QQQ from ' + start_date)
plt.xlabel('Date')
plt.ylabel('Closing Price ($)')

# Save the plot to a file with the current date as the filename
filename = datetime.now().strftime('%Y-%m-%d') + '_QQQ_Closing_Prices.png'
plt.savefig(filename)

# Display the plot (optional, you can comment this out if you don't want it to pop up)
plt.show()

print(f"File saved as {filename}")