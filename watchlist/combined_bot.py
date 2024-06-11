import discord
from discord.ext import commands
import schedule
import asyncio
import re
from datetime import datetime
from watchlist_parser import WatchlistParser
from analyzer import StockAnalyzer
import yfinance as yf
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN', None)

CHART_CHANNEL_ID = 1249429941200879741
CHAT_OUTPUT_CHANNEL_ID = 1249872056925945907
WATCHLIST_CHANNEL_ID = 1249430358198321253

CSV_FILE = '2024-Lidao.csv'
WATCHLIST_FILE = 'watchlist.txt'  # Replace with your actual file path

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

def generate_lists():
    parser = WatchlistParser(WATCHLIST_FILE)
    watchlist_text = parser.read_watchlist()
    tickers = parser.extract_tickers(watchlist_text)

    analyzer = StockAnalyzer(tickers)
    bullish_list, bearish_list, reduce_position_list, clear_position_list, short_bottom_list, J1_list, J2_list = analyzer.analyze()

    return bullish_list, bearish_list, reduce_position_list, clear_position_list, short_bottom_list, J1_list, J2_list

async def send_lists_to_channel():
    channel = bot.get_channel(WATCHLIST_CHANNEL_ID)
    bullish_list, bearish_list, reduce_position_list, clear_position_list, short_bottom_list, J1_list, J2_list = generate_lists()

    bullish_msg = "多头排列 (Bullish Alignment): " + ', '.join(bullish_list)
    bearish_msg = "强烈空头趋势 (Strong Bearish Trend): " + ', '.join(bearish_list)
    reduce_position_msg = "减仓 (破 ma10): " + ', '.join(reduce_position_list)
    clear_position_msg = "清仓 (破 ma20): " + ', '.join(clear_position_list)
    short_bottom_msg = "短底成型 (Short Bottom Formation): " + ', '.join(short_bottom_list)
    j1_msg = "J1: " + ', '.join(J1_list)
    j2_msg = "J2: " + ', '.join(J2_list)

    await channel.send(bullish_msg)
    await channel.send(bearish_msg)
    await channel.send(reduce_position_msg)
    await channel.send(clear_position_msg)
    await channel.send(short_bottom_msg)
    await channel.send(j1_msg)
    await channel.send(j2_msg)

def schedule_job():
    schedule.every().monday.at("16:30").do(lambda: asyncio.run_coroutine_threadsafe(send_lists_to_channel(), bot.loop))
    schedule.every().tuesday.at("16:30").do(lambda: asyncio.run_coroutine_threadsafe(send_lists_to_channel(), bot.loop))
    schedule.every().wednesday.at("16:30").do(lambda: asyncio.run_coroutine_threadsafe(send_lists_to_channel(), bot.loop))
    schedule.every().thursday.at("16:30").do(lambda: asyncio.run_coroutine_threadsafe(send_lists_to_channel(), bot.loop))
    schedule.every().friday.at("16:30").do(lambda: asyncio.run_coroutine_threadsafe(send_lists_to_channel(), bot.loop))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    schedule_job()
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

@bot.command()
async def getdata(ctx):
    await send_lists_to_channel()

@bot.command()
async def cat(ctx, *, message: str):
    print(f'{message}')
    if ctx.channel.id == CHART_CHANNEL_ID:
        pattern = r'(\d+月\d+日).*(猫姐买卖力道1\.0数值)(-?\d+\.\d+).*(买卖力道2\.0标普数值)(-?\d+\.\d+).*(纳指数值)(-?\d+\.\d+)'
        match = re.search(pattern, message)
        if match:
            date_str = match.group(1)
            date = datetime.strptime(date_str, '%m月%d日').replace(year=datetime.now().year)
            formatted_date = date.strftime('%Y-%m-%d')
            lidao_1 = float(match.group(3))
            lidao_spx = float(match.group(5))
            lidao_nasdaq = float(match.group(7))

            # Load existing data
            if os.path.exists(CSV_FILE):
                existing_data = pd.read_csv(CSV_FILE, parse_dates=['Date'])
                existing_data['Date'] = pd.to_datetime(existing_data['Date'])
            else:
                existing_data = pd.DataFrame(columns=['Date', 'Lidao-1.0', 'Lidao-SPX', 'Lidao-NASDAQ'])

            # Check if the date already exists in the CSV
            date_exists = existing_data['Date'] == date
            if date_exists.any():
                # Update existing entry
                existing_data.loc[date_exists, ['Lidao-1.0', 'Lidao-SPX', 'Lidao-NASDAQ']] = [lidao_1, lidao_spx, lidao_nasdaq]
            else:
                # Append new entry
                new_entry = pd.DataFrame([[date, lidao_1, lidao_spx, lidao_nasdaq]], columns=['Date', 'Lidao-1.0', 'Lidao-SPX', 'Lidao-NASDAQ'])
                existing_data = pd.concat([existing_data, new_entry], ignore_index=True)

            # Save data back to CSV
            existing_data.to_csv(CSV_FILE, index=False)

            await ctx.send('Data has been added to CSV. Generating plot...')
            await generate_and_send_plot(ctx)
        else:
            await ctx.send('Message format is incorrect.')

async def generate_and_send_plot(ctx):
    try:
        # Load the lidao data from the CSV file
        lidao_data = pd.read_csv(CSV_FILE, parse_dates=['Date'], index_col='Date')

        # Ensure that all dates are parsed correctly
        lidao_data.index = pd.to_datetime(lidao_data.index)

        # Fetching the QQQ data starting from the earliest date in lidao data
        start_date = lidao_data.index.min()
        qqq_data = yf.download('QQQ', start=start_date.strftime('%Y-%m-%d'))

        # Check if all data are aligned by date
        combined_data = pd.DataFrame(index=qqq_data.index)
        combined_data['QQQ Close'] = qqq_data['Close']
        combined_data = combined_data.join(lidao_data, how='inner')  # Inner join to ensure all data are aligned

        # Setting up the plot with secondary y-axis
        plt.style.use('dark_background')
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # First axis for QQQ
        ax1.set_xlabel('Date')
        ax1.set_ylabel('QQQ Close', color='cyan')
        ax1.plot(combined_data.index, combined_data['QQQ Close'], label='QQQ Close', color='cyan', marker='*', linestyle='-', markersize=8)
        ax1.tick_params(axis='y', labelcolor='cyan')

        # Second axis for lidao data
        ax2 = ax1.twinx()
        ax2.set_ylabel('Lidao Indices', color='magenta')
        ax2.plot(combined_data.index, combined_data['Lidao-1.0'], label='Lidao-1.0', color='magenta', marker='s', linestyle='-', markersize=6)
        ax2.plot(combined_data.index, combined_data['Lidao-SPX'], label='Lidao-SPX', color='lime', marker='^', linestyle='-', markersize=6)
        ax2.plot(combined_data.index, combined_data['Lidao-NASDAQ'], label='Lidao-NASDAQ', color='yellow', marker='D', linestyle='-', markersize=6)
        ax2.tick_params(axis='y', labelcolor='magenta')

        # Adjust layout to make space for title
        fig.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust the rectangle in which the plot fits (left, bottom, right, top)
        fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9))
        plt.title('QQQ Close and Lidao Indices on Dark Background', fontsize=16, color='white')

        # Save the plot to a file with the current date as the filename
        filename = datetime.now().strftime('%Y-%m-%d') + '_QQQ_and_Lidao_Indices_Dark.png'
        plt.savefig(filename)

        # Send the plot to the Discord channel
        #await ctx.send(file=discord.File(filename))
        channel = bot.get_channel(CHAT_OUTPUT_CHANNEL_ID)

        await channel.send(file=discord.File(filename))
        await ctx.send('Plot Generation Done.')


        # Do not show the plot
        # plt.show()

        print(f"File saved as {filename}")
    except Exception as e:
        await ctx.send(f'Error generating plot: {e}')
        print(f'Error generating plot: {e}')

if __name__ == "__main__":
    bot.run(TOKEN)