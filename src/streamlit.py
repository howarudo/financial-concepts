import yfinance as yahooFinance
import numpy as np

spy_df = yahooFinance.Ticker("SPY").history(start="2005-01-01", end="2017-01-01")


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
        return self.df.loc[spy_df.index[self.index-days+1]: spy_df.index[self.index]].Close

    def get_prev_price(self):
        return self.df.loc[self.index - 1].Close

    def get_next_price(self):
        return self.df.loc[self.index + 1].Close

spy_ticker = StockTicker(spy_df)

# have a class to hold information about holding, cash, and portfolio value
class Trader:

    def __init__(self, cash, stock_ticker, commision=0):
        self.cash = cash
        self.holdings = 0 # number of shares of SPY
        self.stock_ticker = stock_ticker
        self.commision = commision

    def __str__(self):
        return f"Cash: {self.cash}, SPY Holding: {self.holdings}"

    def portfolio_value(self):
        return self.cash + self.stock_ticker.get_price() * self.holdings

    def buy(self, amount):
        # commision is a % of the amount
        if self.cash < amount * (1 + self.commision):
            amount = self.cash / (1 + self.commision)
        price = self.stock_ticker.get_price()
        self.holdings += amount / price
        self.cash -= amount * (1 + self.commision)

    def sell(self, amount):
        if self.holdings < amount:
            amount = self.holdings
        price = self.stock_ticker.get_price()
        self.holdings -= amount
        self.cash += amount * price * (1 - self.commision)

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

golden_death_cross = GoldenAndDeathCrossStrategy(spy_ticker, 30, 200, 0.01)

from collections import defaultdict

START_CASH = 10000
TRADING_DAYS = 2000
AMOUNT_BOUGHT_PER_DAY = START_CASH / TRADING_DAYS

trader_benchmark = Trader(START_CASH, spy_ticker, commision=0)
trader_benchmark.buy(trader_benchmark.cash)

trader_commision = Trader(START_CASH, spy_ticker, commision=0.05)
trader_no_commision = Trader(START_CASH, spy_ticker, commision=0)
trader_death_cross = Trader(START_CASH, spy_ticker, commision=0.05)

portfolio_values = defaultdict(list)

for i in range(TRADING_DAYS):
    trader_commision.buy(AMOUNT_BOUGHT_PER_DAY)
    trader_no_commision.buy(AMOUNT_BOUGHT_PER_DAY)

    signal = golden_death_cross.get_signal()
    if signal == "buy":
        trader_death_cross.buy(trader_death_cross.cash/2)
    elif signal == "sell":
        trader_death_cross.sell(trader_death_cross.holdings/2)

    portfolio_values[trader_benchmark].append(trader_benchmark.portfolio_value())
    portfolio_values[trader_commision].append(trader_commision.portfolio_value())
    portfolio_values[trader_no_commision].append(trader_no_commision.portfolio_value())
    portfolio_values[trader_death_cross].append(trader_death_cross.portfolio_value())

    spy_ticker.next_day()

import plotly.graph_objects as go

# Create a single figure
fig = go.Figure()

# Add the first trace for SPY Price
fig.add_trace(go.Scatter(x=spy_ticker.get_price_history(2000).index,
                         y=spy_ticker.get_price_history(2000).values,
                         mode='lines', name='SPY Price'))

# Add the second trace for 30 Day MVA
fig.add_trace(go.Scatter(x=spy_ticker.get_price_history(2000).index,
                         y=golden_death_cross.slow_avg,
                         mode='lines', name='30 Day MVA'))

# Add the third trace for 200 Day MVA
fig.add_trace(go.Scatter(x=spy_ticker.get_price_history(2000).index,
                         y=golden_death_cross.long_avg,
                         mode='lines', name='200 Day MVA'))

# add death and golden cross signals
buy_signal = []
sell_signal = []
for i in range(len(golden_death_cross.signal)):
    if golden_death_cross.signal[i] == "buy":
        buy_signal.append(spy_ticker.get_price_history(2000).index[i])
    if golden_death_cross.signal[i] == "sell":
        sell_signal.append(spy_ticker.get_price_history(2000).index[i])


# Add vertical lines for buy signals
for signal in buy_signal:
    fig.add_vline(x=signal, line=dict(color='green', width=2, dash='dash'))

# Add vertical lines for sell signals
for signal in sell_signal:
    fig.add_vline(x=signal, line=dict(color='red', width=2, dash='dash'))

fig.add_trace(go.Scatter(x=buy_signal, y=[spy_ticker.get_price_history(2000).max()]*len(buy_signal),\
                            mode='markers', name='Buy Signal', marker=dict(size=10, color='green', symbol='triangle-up')))
fig.add_trace(go.Scatter(x=sell_signal, y=[spy_ticker.get_price_history(2000).max()]*len(sell_signal),\
                            mode='markers', name='Sell Signal', marker=dict(size=10, color='red', symbol='triangle-down')))

# Update layout with a title and axis labels
fig.update_layout(title="SPY Price with 30 Day and 200 Day MVA",
                  xaxis_title="Date",
                  yaxis_title="Price",
                  legend_title="Legend",
                  width=1000,
                  height=600)


# Show the combined graph

import streamlit as st

event = st.plotly_chart(fig, use_container_width=True)
event.selection
