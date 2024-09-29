import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st

def generate_jumping_stock(n_days, event_day):
    """
    Returns a time series of stock prices with a jump in price on the event day
    """
    noise_amp = 13
    days = np.arange(0, n_days)
    stock_price = noise_amp * np.random.normal(size=n_days)
    for i in range(n_days):
        if i < event_day:
            stock_price[i] = stock_price[i] + 200 + i * 2
        else:
            stock_price[i] = stock_price[i] + 300 + i * 2
    return days, stock_price


def generate_returns(time_series):
    """
    Returns the returns of a time series
    """
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
    fig.add_vrect(x0=DEMO_EVENT_DAY - DEMO_EVENT_WINDOW_PRE, x1=DEMO_EVENT_DAY + DEMO_EVENT_WINDOW_POST, fillcolor="LightSalmon", opacity=0.5, line_width=0, row=1, col=1)
    fig.update_xaxes(title_text="Days", row=1, col=1)
    fig.update_yaxes(title_text="Stock Price", row=1, col=1)

    fig.add_trace(go.Scatter(x=days, y=returns, mode='lines', name='Returns'), row=1, col=2)
    fig.add_vrect(x0=DEMO_EVENT_DAY - DEMO_EVENT_WINDOW_PRE, x1=DEMO_EVENT_DAY + DEMO_EVENT_WINDOW_POST, fillcolor="LightSalmon", opacity=0.5, line_width=0, row=1, col=2)
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
    AR_avg, AR_std = np.average(abnormal_returns), np.std(abnormal_returns) / np.sqrt(DEMO_EVENT_WINDOW_PRE + DEMO_EVENT_WINDOW_POST)
    AR_mva = np.convolve(abnormal_returns, np.ones((DEMO_EVENT_WINDOW_PRE + DEMO_EVENT_WINDOW_POST,))/DEMO_EVENT_WINDOW_PRE, mode='valid')

    fig = go.Figure()
    fig.add_hrect(y0=AR_avg - 3 * AR_std, y1=AR_avg + 3 * AR_std, fillcolor="#F0E68C", opacity=0.5, line_width=0)
    fig.add_trace(go.Scatter(x=days, y=abnormal_returns, mode='lines', name='AR'))
    fig.add_trace(go.Scatter(x=days[DEMO_EVENT_WINDOW_PRE:-DEMO_EVENT_WINDOW_POST], y=AR_mva, mode='lines', name='AR MVA'))

    fig.update_layout(
        title="Abnormal Returns",
        xaxis_title="Days",
        yaxis_title="Abnormal Returns",
        height=400,
        xaxis_fixedrange=True,
        yaxis_fixedrange=True,
        colorway=["#E2DED0", "#FF2511"]
        )

    st.plotly_chart(fig, use_container_width=True)

    z_score = (AR_mva[DEMO_EVENT_DAY-DEMO_EVENT_WINDOW_PRE] - AR_avg) / AR_std
    p_value = 1 - stats.norm.cdf(z_score)
    st.markdown("""
    $$
    \\text{Z-score = } %.2f, \\text{ p-value = } %.4f
    $$
    """ % (z_score, p_value))

    return



def main():
    st.set_page_config(
        page_title="Event Study Analysis",
        page_icon="📈",
    )
    np.random.seed(0)

    st.title("Event Study Analysis: An Introduction")

    st.markdown("*5 min read*")

    overview = open("src/pages/texts/event_study_analysis/overview.md", "r").read()
    st.markdown(overview)

    demo = open("src/pages/texts/event_study_analysis/demo.md", "r").read()
    st.markdown(demo)

    global DEMO_EVENT_DAY, DEMO_EVENT_WINDOW_PRE, DEMO_EVENT_WINDOW_POST
    DEMO_NUMBER_OF_DAYS = st.slider("Number of days", 50, 80, 70, 10)
    DEMO_EVENT_WINDOW_PRE = 2
    DEMO_EVENT_WINDOW_POST = 3
    DEMO_EVENT_DAY = st.slider("Event day", 10, DEMO_NUMBER_OF_DAYS - 20 , 30, 1)

    days, stock_price = generate_jumping_stock(DEMO_NUMBER_OF_DAYS, DEMO_EVENT_DAY)
    returns = generate_returns(stock_price)
    mean, variance = CMR_model(returns)
    abnormal_returns = returns - mean

    plot_stock_price_and_returns(days, stock_price, returns)

    demo_results = open("src/pages/texts/event_study_analysis/demo_results.md", "r").read()
    st.markdown(demo_results)

    statistical_anaylsis = open("src/pages/texts/event_study_analysis/statistical_analysis.md", "r").read()
    st.markdown(statistical_anaylsis)

    plot_abnormal_returns(days, abnormal_returns)

    statistical_results = open("src/pages/texts/event_study_analysis/statistical_results.md", "r").read()
    st.markdown(statistical_results)

    return
if __name__ == "__main__":
    main()
