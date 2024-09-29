import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st

def generate_jumping_stock(n_days, event_day):
    noise_amp = 10
    days = np.arange(0, n_days)
    stock_price = noise_amp * np.random.normal(size=n_days)
    for i in range(n_days):
        if i < event_day:
            stock_price[i] = stock_price[i] + 200 + i * 2
        else:
            stock_price[i] = stock_price[i] + 400 + i * 2
    return days, stock_price


def generate_returns(time_series):
    return_series = []
    for i in range(len(time_series) - 1):
        return_series.append(1 - time_series[i] / time_series[i + 1])
    return_series.append(0)
    return np.array(return_series)


def CMR_model(returns):
    """
    Returns the mean and Variance of the returns
    """
    return np.average(returns), np.var(returns)

def plot_stock_price_and_returns(days, stock_price, returns):
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Stock Price", "Returns"))
    fig.add_trace(go.Scatter(x=days, y=stock_price, mode='lines', name='Stock Price'), row=1, col=1)
    fig.add_vrect(x0=EVENT_DAY - EVENT_WINDOW_PRE, x1=EVENT_DAY + EVENT_WINDOW_POST, fillcolor="LightSalmon", opacity=0.5, line_width=0, row=1, col=1)
    fig.update_xaxes(title_text="Days", row=1, col=1)
    fig.update_yaxes(title_text="Stock Price", row=1, col=1)

    fig.add_trace(go.Scatter(x=days, y=returns, mode='lines', name='Returns'), row=1, col=2)
    fig.add_vrect(x0=EVENT_DAY - EVENT_WINDOW_PRE, x1=EVENT_DAY + EVENT_WINDOW_POST, fillcolor="LightSalmon", opacity=0.5, line_width=0, row=1, col=2)
    fig.update_xaxes(title_text="Days", row=1, col=2)
    fig.update_yaxes(title_text="Returns", row=1, col=2)


    fig.update_layout(
        height=350,
        showlegend=False,
        title_text="Stock Price and Returns",
        xaxis1_fixedrange=True,
        yaxis1_fixedrange=True,
        xaxis2_fixedrange=True,
        yaxis2_fixedrange=True
        )

    st.plotly_chart(fig, use_container_width=True)


def plot_abnormal_returns(days, abnormal_returns):
    AR_avg, AR_std = np.average(abnormal_returns), np.std(abnormal_returns) / np.sqrt(EVENT_WINDOW_PRE + EVENT_WINDOW_POST)
    AR_mva = np.convolve(abnormal_returns, np.ones((EVENT_WINDOW_PRE + EVENT_WINDOW_POST,))/EVENT_WINDOW_PRE, mode='valid')

    fig = go.Figure()
    fig.add_hrect(y0=AR_avg - 2 * AR_std, y1=AR_avg + 2 * AR_std, fillcolor="LightSalmon", opacity=0.5, line_width=0)
    fig.add_trace(go.Scatter(x=days, y=abnormal_returns, mode='lines', name='AR'))
    fig.add_trace(go.Scatter(x=days[EVENT_WINDOW_PRE:-EVENT_WINDOW_POST], y=AR_mva, mode='lines', name='AR MVA'))

    fig.update_layout(
        title="Abnormal Returns",
        xaxis_title="Days",
        yaxis_title="Abnormal Returns",
        height=400,
        xaxis_fixedrange=True,
        yaxis_fixedrange=True
        )

    st.plotly_chart(fig, use_container_width=True)


def main():
    np.random.seed(0)
    global EVENT_DAY, EVENT_WINDOW_PRE, EVENT_WINDOW_POST
    NUMBER_OF_DAYS = st.slider("Number of days", 50, 80, 70, 10)
    EVENT_WINDOW_PRE = 2
    EVENT_WINDOW_POST = 3
    EVENT_DAY = st.slider("Event day", 10, NUMBER_OF_DAYS - 20 , 30, 1)

    days, stock_price = generate_jumping_stock(NUMBER_OF_DAYS, EVENT_DAY)
    returns = generate_returns(stock_price)
    mean, variance = CMR_model(returns)
    abnormal_returns = returns - mean

    plot_stock_price_and_returns(days, stock_price, returns)

    plot_abnormal_returns(days, abnormal_returns)


if __name__ == "__main__":
    main()
