class WatchlistParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_watchlist(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            watchlist_text = file.read()
        return watchlist_text

    def extract_tickers(self, watchlist_text):
        tokens = watchlist_text.split(',')
        tickers = [token for token in tokens if not token.strip().startswith('###')]
        tickers_cleaned = [ticker.split(':')[1].strip() if ':' in ticker else ticker.strip() for ticker in tickers]
        return tickers_cleaned
