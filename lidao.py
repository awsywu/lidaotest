import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# Set the style for a dark background
plt.style.use('dark_background')

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
ax1.set_xlabel('Date')
ax1.set_ylabel('QQQ Close', color='cyan')
ax1.plot(combined_data.index, combined_data['QQQ Close'], label='QQQ Close', color='cyan', marker='*', linestyle='-', markersize=8)
ax1.tick_params(axis='y', labelcolor='cyan')

# Second axis for lidao data
ax2 = ax1.twinx()
ax2.set_ylabel('Lidao Indices', color='magenta')
ax2.plot(combined_data.index, combined_data['lidao-1.0'], label='Lidao-1.0', color='magenta', marker='s', linestyle='-', markersize=6)
ax2.plot(combined_data.index, combined_data['lidao-SPX'], label='Lidao-SPX', color='lime', marker='^', linestyle='-', markersize=6)
ax2.plot(combined_data.index, combined_data['lidao-NASDAQ'], label='Lidao-NASDAQ', color='yellow', marker='D', linestyle='-', markersize=6)
ax2.tick_params(axis='y', labelcolor='magenta')

# Adjust layout to make space for title
fig.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust the rectangle in which the plot fits (left, bottom, right, top)
fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9))
plt.title('QQQ Close and Lidao Indices on Dark Background', fontsize=16, color='white')

# Save the plot to a file with the current date as the filename
filename = datetime.now().strftime('%Y-%m-%d') + '_QQQ_and_Lidao_Indices_Dark.png'
plt.savefig(filename)

# Display the plot
plt.show()

print(f"File saved as {filename}")
