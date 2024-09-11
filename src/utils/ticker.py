class StockTicker:

    def __init__(self, df):
        self.df = df
        self.index = 0
        self.date = df.index[self.index]

    def next_day(self):
        self.index += 1
        self.date = self.df.index[self.index]

    def get_price(self):
        return self.df.loc[self.date].Close

    def get_date(self):
        return self.date

    def get_price_history(self, days):
        if days <= 0:
            raise ValueError("days must be greater than 0")
        days = min(days, self.index+1)
        return self.df.loc[self.df.index[self.index-days+1]: self.df.index[self.index]].Close

    def get_prev_price(self):
        return self.df.loc[self.index - 1].Close

    def get_next_price(self):
        return self.df.loc[self.index + 1].Close
