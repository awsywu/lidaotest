import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# Load the lidao data from the CSV file
lidao_data = pd.read_csv('2024-Lidao.csv', parse_dates=['date'], index_col='date')

# Fetching the QQQ data starting from the earliest date in lidao data
start_date = lidao_data.index.min()
qqq_data = yf.download('QQQ', start=start_date.strftime('%Y-%m-%d'))

# Check if all data are aligned by date
combined_data = pd.DataFrame(index=qqq_data.index)
combined_data['QQQ Close'] = qqq_data['Close']
combined_data = combined_data.join(lidao_data, how='inner')  # Inner join to ensure all data are aligned

# Setting up the plot with secondary y-axis
fig, ax1 = plt.subplots(figsize=(10, 6))

# First axis for QQQ
color = 'tab:blue'
ax1.set_xlabel('Date')
ax1.set_ylabel('QQQ Close', color=color)
ax1.plot(combined_data.index, combined_data['QQQ Close'], label='QQQ Close', color=color, marker='o', linestyle='-')
ax1.tick_params(axis='y', labelcolor=color)

# Second axis for lidao data
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Lidao Indices', color=color)
ax2.plot(combined_data.index, combined_data['lidao-1.0'], label='Lidao-1.0', color='red', marker='o', linestyle='-')
ax2.plot(combined_data.index, combined_data['lidao-SPX'], label='Lidao-SPX', color='green', marker='o', linestyle='-')
ax2.plot(combined_data.index, combined_data['lidao-NASDAQ'], label='Lidao-NASDAQ', color='yellow', marker='o', linestyle='-')
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
plt.title('QQQ Close and Lidao Indices')
fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9))

# Save the plot to a file with the current date as the filename
filename = datetime.now().strftime('%Y-%m-%d') + '_QQQ_and_Lidao_Indices.png'
plt.savefig(filename)

# Display the plot
plt.show()

print(f"File saved as {filename}")
