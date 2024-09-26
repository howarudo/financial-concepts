from collections import defaultdict
import yfinance as yahooFinance
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import logging

from utils.ticker import StockTicker
from utils.trader import Trader
from utils.strategy.golden_death_cross import GoldenAndDeathCrossStrategy

# Setup logging
logging.basicConfig(level=logging.INFO)

# Configurable parameters
START_CASH = 10000
TRADING_DAYS = 2000
AMOUNT_BOUGHT_PER_DAY = START_CASH / TRADING_DAYS
TICKER_SYMBOL = "SPY"
START_DATE = "2005-01-01"
END_DATE = "2017-01-01"
SHORT_MVA = 30
LONG_MVA = 200
COMMISSION_RATE = 0.05

# Function to fetch ticker data
@st.cache_data
def fetch_ticker_data(ticker_symbol, start_date, end_date):
    try:
        df = yahooFinance.Ticker(ticker_symbol).history(start=start_date, end=end_date)
        return df
    except Exception as e:
        logging.error(f"Error fetching data for {ticker_symbol}: {e}")
        st.error("Failed to fetch stock data. Please try again later.")
        return None

# Function to run trading strategies
def run_trading_simulation(ticker_df):
    spy_ticker = StockTicker(ticker_df)
    golden_death_cross = GoldenAndDeathCrossStrategy(spy_ticker, SHORT_MVA, LONG_MVA, 0.01)

    # Traders setup
    trader_benchmark = Trader(START_CASH, spy_ticker, commission=0)
    trader_benchmark.buy(START_CASH)

    trader_commission = Trader(START_CASH, spy_ticker, commission=COMMISSION_RATE)
    trader_no_commission = Trader(START_CASH, spy_ticker, commission=0)
    trader_death_cross = Trader(START_CASH, spy_ticker, commission=COMMISSION_RATE)

    portfolio_values = defaultdict(list)

    for i in range(TRADING_DAYS):
        # Daily buy for commission and no-commission traders
        trader_commission.buy(AMOUNT_BOUGHT_PER_DAY)
        trader_no_commission.buy(AMOUNT_BOUGHT_PER_DAY)

        # Execute strategy based on signals
        signal = golden_death_cross.get_signal()
        if signal == "buy":
            trader_death_cross.buy(trader_death_cross.cash / 2)
        elif signal == "sell":
            trader_death_cross.sell(trader_death_cross.holdings / 2)

        # Store portfolio values
        portfolio_values['benchmark'].append(trader_benchmark.portfolio_value())
        portfolio_values['commission'].append(trader_commission.portfolio_value())
        portfolio_values['no_commission'].append(trader_no_commission.portfolio_value())
        portfolio_values['death_cross'].append(trader_death_cross.portfolio_value())

        spy_ticker.next_day()

    return portfolio_values, spy_ticker, golden_death_cross

# Plotting function
def plot_mva_results(spy_ticker, golden_death_cross, portfolio_values):
    fig = go.Figure()

    # Add SPY price trace
    fig.add_trace(go.Scatter(x=spy_ticker.get_price_history(TRADING_DAYS).index,
                             y=spy_ticker.get_price_history(TRADING_DAYS).values,
                             mode='lines', name='SPY'))

    # Add MVA traces
    fig.add_trace(go.Scatter(x=spy_ticker.get_price_history(TRADING_DAYS).index,
                             y=golden_death_cross.slow_avg,
                             mode='lines', name=f'{SHORT_MVA}d'))

    fig.add_trace(go.Scatter(x=spy_ticker.get_price_history(TRADING_DAYS).index,
                             y=golden_death_cross.long_avg,
                             mode='lines', name=f'{LONG_MVA}d'))

    # Add Buy/Sell signal markers
    buy_signals, sell_signals = [], []
    for i, signal in enumerate(golden_death_cross.signal):
        if signal == "buy":
            buy_signals.append(spy_ticker.get_price_history(TRADING_DAYS).index[i])
        elif signal == "sell":
            sell_signals.append(spy_ticker.get_price_history(TRADING_DAYS).index[i])

    # Add vertical lines for buy/sell signals
    for signal in buy_signals:
        fig.add_vline(x=signal, line=dict(color='green', width=2, dash='dash'))
    for signal in sell_signals:
        fig.add_vline(x=signal, line=dict(color='red', width=2, dash='dash'))

    # Add buy/sell markers
    fig.add_trace(go.Scatter(x=buy_signals, y=[spy_ticker.get_price_history(TRADING_DAYS).max()]*len(buy_signals),
                             mode='markers', name='Buy', marker=dict(size=10, color='green', symbol='triangle-up')))
    fig.add_trace(go.Scatter(x=sell_signals, y=[spy_ticker.get_price_history(TRADING_DAYS).max()]*len(sell_signals),
                             mode='markers', name='Sell', marker=dict(size=10, color='red', symbol='triangle-down')))

    # Update layout
    fig.update_layout(
        title="SPY Price with 30-Day and 200-Day MVA",
        xaxis_title="Date", yaxis_title="Price",
        legend_title="Legend",
        height=400
        )

    # fix the x-axis range and y-axis range
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    st.plotly_chart(fig, use_container_width=True)

def plot_trading_simulation_results(spy_ticker, golden_death_cross, portfolio_values):
    benchmark_values = np.array(portfolio_values['benchmark'])
    commision_values = np.array(portfolio_values['commission'])
    # no_commision_values = np.array(portfolio_values['no_commission'])
    death_cross_values = np.array(portfolio_values['death_cross'])
    dates = spy_ticker.get_price_history(TRADING_DAYS).index
    fig = go.Figure()
    # Add SPY price trace
    fig.add_trace(go.Scatter(x=dates, y=benchmark_values, mode='lines', name="BMark"))
    fig.add_trace(go.Scatter(x=dates, y=commision_values, mode='lines', name="T. Com."))
    fig.add_trace(go.Scatter(x=dates, y=death_cross_values, mode='lines', name="T. G&D"))
    for i, signal in enumerate(golden_death_cross.signal):
        if signal == "sell":
            fig.add_vline(x=dates[i], line=dict(color='red', width=2, dash='dash'))
        elif signal == "buy":
            fig.add_vline(x=dates[i], line=dict(color='green', width=2, dash='dash'))

    # Update layout with date-based x-axis
    fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        legend_title="Portfolio",
        height=400,
        xaxis=dict(type='date')  # Ensure x-axis is treated as dates
    )

    # fix the x-axis range and y-axis range
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    st.plotly_chart(fig, use_container_width=True)



# Main Streamlit application
def main():

    st.set_page_config(
    page_title="Golden Cross & Death Cross",
    page_icon="📈",
    )

    st.title("Golden Cross & Death Cross")

    # Fetch data
    ticker_df = fetch_ticker_data(TICKER_SYMBOL, START_DATE, END_DATE)

    if ticker_df is not None:
        # Run simulation
        portfolio_values, spy_ticker, golden_death_cross = run_trading_simulation(ticker_df)

        # Read overview from texts/golden_cross_death_cross/overview.md
        overview = open("src/pages/texts/golden_cross_death_cross/overview.md", "r").read()
        st.markdown(overview)

        mva = open("src/pages/texts/golden_cross_death_cross/mva.md", "r").read()
        st.markdown(mva)
        # Plot results
        plot_mva_results(spy_ticker, golden_death_cross, portfolio_values)

        backtest_conditions = open("src/pages/texts/golden_cross_death_cross/backtest_conditions.md", "r").read()
        st.markdown(backtest_conditions)
        # Plot trading simulation results
        plot_trading_simulation_results(spy_ticker, golden_death_cross, portfolio_values)

        analysis = open("src/pages/texts/golden_cross_death_cross/analysis.md", "r").read()
        st.markdown(analysis)

if __name__ == "__main__":
    main()
