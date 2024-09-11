class GoldenAndDeathCrossStrategy:

    def __init__(self, stock_ticker, short_window, long_window, threshold):
        self.stock_ticker = stock_ticker
        self.short_window = short_window
        self.long_window = long_window
        self.threshold = threshold
        self.signal = []

        self.slow_avg = []
        self.long_avg = []

    def get_signal(self):
        if self.stock_ticker.index < self.long_window - 1:
            self.signal.append("hold")
            self.slow_avg.append(None)
            self.long_avg.append(None)
            return None

        prev_short_avg = self.stock_ticker.get_price_history(self.short_window+1)[:self.short_window].mean()
        prev_long_avg = self.stock_ticker.get_price_history(self.long_window+1)[:self.long_window].mean()
        short_avg = self.stock_ticker.get_price_history(self.short_window).mean()
        long_avg = self.stock_ticker.get_price_history(self.long_window).mean()

        self.slow_avg.append(short_avg)
        self.long_avg.append(long_avg)

        if short_avg > long_avg * (1 + self.threshold) and prev_short_avg < prev_long_avg * (1 + self.threshold):
            self.signal.append("buy")
            return "buy"
        if short_avg < long_avg * (1 - self.threshold) and prev_short_avg > prev_long_avg * (1 - self.threshold):
            self.signal.append("sell")
            return "sell"
        self.signal.append("hold")
        return None
