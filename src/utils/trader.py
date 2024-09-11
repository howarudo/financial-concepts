class Trader:
    # have a class to hold information about holding, cash, and portfolio value
    def __init__(self, cash, stock_ticker, commission=0):
        self.cash = cash
        self.holdings = 0 # number of shares of SPY
        self.stock_ticker = stock_ticker
        self.commission = commission

    def __str__(self):
        return f"Cash: {self.cash}, SPY Holding: {self.holdings}"

    def portfolio_value(self):
        return self.cash + self.stock_ticker.get_price() * self.holdings

    def buy(self, amount):
        # commission is a % of the amount
        if self.cash < amount * (1 + self.commission):
            amount = self.cash / (1 + self.commission)
        price = self.stock_ticker.get_price()
        self.holdings += amount / price
        self.cash -= amount * (1 + self.commission)

    def sell(self, amount):
        if self.holdings < amount:
            amount = self.holdings
        price = self.stock_ticker.get_price()
        self.holdings -= amount
        self.cash += amount * price * (1 - self.commission)
