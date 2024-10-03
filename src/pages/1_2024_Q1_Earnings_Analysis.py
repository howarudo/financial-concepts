import pandas as pd
import numpy as np
import yfinance as yahooFinance
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

START_DATE = '2023-08-01'
END_DATE = '2024-08-01'
TICKERS2CALLDATE = {
    "NVDA": "2024-05-22",
    "TSM": "2024-04-18",
    "AAPL": "2024-05-02",
    "TSLA": "2024-04-23",
    "MSFT": "2024-04-25",
    "JPM": "2024-04-12",
    "V": "2024-04-24"
}
EVENT_WINDOW = [2, 3]

def get_ticker_df(ticker):
    res_df = yahooFinance.Ticker(ticker).history(start=START_DATE, end=END_DATE)
    return res_df

def get_returns(prices):
    returns = []
    for i in range(1, len(prices)):
        returns.append(prices[i] / prices[i-1] - 1)
    returns.append(0)
    return np.array(returns)

def get_AR_CMR(returns):
    """
    returns
    model_returns: array of returns by the model
    ar_returns: array of abnormal returns
    ar_std: standard deviation of the abnormal returns
    mva_ar_returns: array of moving average of abnormal returns
    """
    model_returns = np.mean(returns) * np.ones(len(returns))
    ar_returns = returns - model_returns
    ar_std = np.std(ar_returns)
    mva_ar_returns = np.convolve(ar_returns, np.ones(EVENT_WINDOW[0] + EVENT_WINDOW[1]) / (EVENT_WINDOW[0] + EVENT_WINDOW[1]), mode='valid')
    return model_returns, ar_std, ar_returns, mva_ar_returns

def get_AR_CAPM(returns, market_returns):
    """
    returns
    model_returns: array of returns by the model
    ar_returns: array of abnormal returns
    mva_ar_returns: array of moving average of abnormal returns
    """
    beta = np.cov(returns, market_returns)[0][1] / np.var(market_returns)
    model_returns = beta * market_returns + np.mean(returns - beta * market_returns)
    ar_returns = returns - model_returns
    ar_std = np.std(ar_returns)
    mva_ar_returns = np.convolve(ar_returns, np.ones(EVENT_WINDOW[0] + EVENT_WINDOW[1]) / (EVENT_WINDOW[0] + EVENT_WINDOW[1]), mode='valid')
    return model_returns, ar_returns, ar_std, mva_ar_returns

def _get_FF_coeff_df():
    ff_coeff_df = pd.read_csv("../data/F-F_Research_Data_Factors_daily.csv")
    ff_coeff_df["date"] = pd.to_datetime(ff_coeff_df["date"], format='%Y%m%d')
    ff_coeff_df = ff_coeff_df[(ff_coeff_df["date"] >= START_DATE) & (ff_coeff_df["date"] <= END_DATE)]
    ff_coeff_df = ff_coeff_df.set_index("date")
    return ff_coeff_df

def get_AR_FF(returns, market_returns):
    """
    returns
    model_returns: array of returns by the model
    model_std: standard deviation of the model returns
    ar_returns: array of abnormal returns
    mva_ar_returns: array of moving average of abnormal returns
    """
    ff_coeff_df = _get_FF_coeff_df()
    b1 = np.cov(returns - ff_coeff_df["RF"], market_returns - ff_coeff_df["RF"])[0][1] / np.var(market_returns - ff_coeff_df["RF"])
    b2 = np.cov(returns, ff_coeff_df["SMB"])[0][1] / np.var(ff_coeff_df["SMB"])
    b3 = np.cov(returns, ff_coeff_df["HML"])[0][1] / np.var(ff_coeff_df["HML"])
    alpha = np.mean(returns - ff_coeff_df["RF"] - b1 * (market_returns - ff_coeff_df["RF"]) - b2 * ff_coeff_df["SMB"] - b3 * ff_coeff_df["HML"])
    model_returns = alpha + ff_coeff_df["RF"] + b1 * (market_returns - ff_coeff_df["RF"]) + b2 * ff_coeff_df["SMB"] + b3 * ff_coeff_df["HML"]
    ar_returns = returns - model_returns
    ar_std = np.std(ar_returns)
    mva_ar_returns = np.convolve(ar_returns, np.ones(EVENT_WINDOW[0] + EVENT_WINDOW[1]) / (EVENT_WINDOW[0] + EVENT_WINDOW[1]), mode='valid')
    return model_returns, ar_returns, ar_std, mva_ar_returns

def plot_model_returns(ticker, prices, returns, model_returns):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)
    fig.add_trace(go.Scatter(x=prices.index, y=prices["Close"], name="Close Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=returns, name="Returns"), row=2, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=model_returns, name="Model Returns"), row=2, col=1)
    fig.update_layout(title=f"{ticker} Model Returns", xaxis_title="Date", yaxis_title="Price", showlegend=True)
    fig.show()

def plot_MR_CMR(ticker):
    prices = get_ticker_df(ticker)
    returns = get_returns(prices["Close"].values)
    model_returns, ar_std, ar_returns, mva_ar_returns = get_AR_CMR(returns)
    plot_model_returns(ticker, prices, returns, model_returns)

def plot_MR_CAPM(ticker):
    prices = get_ticker_df(ticker)
    returns = get_returns(prices["Close"].values)
    market_prices = get_ticker_df("^GSPC")
    market_returns = get_returns(market_prices["Close"].values)
    model_returns, ar_returns, ar_std, mva_ar_returns = get_AR_CAPM(returns, market_returns)
    plot_model_returns(ticker, prices, returns, model_returns)

def plot_MR_FF(ticker):
    prices = get_ticker_df(ticker)
    returns = get_returns(prices["Close"].values)
    market_prices = get_ticker_df("^GSPC")
    market_returns = get_returns(market_prices["Close"].values)
    model_returns, ar_returns, ar_std, mva_ar_returns = get_AR_FF(returns, market_returns)
    plot_model_returns(ticker, prices, returns, model_returns)

def display_model_comparison():
    results_df = pd.read_csv("data/model_comparison.csv")
    results_df = results_df.rename(columns={"Unnamed: 0": "Ticker", "Unnamed: 1": "Model"})
    results_df = results_df[["Ticker", "Model", "R2"]]
    results_df["R2"] = results_df["R2"].apply(lambda x: f"{x:.2f}")
    tickers = results_df["Ticker"].unique()
    colorway = {
        "NVDA": ["#053221", "#053926", "#06402B"],
        "TSM": ["#740505", "#840505", "#950606"],
        "AAPL": ["#101010", "#191919", "#212121"],
        "TSLA": ["#9F1613", "#B61915", "#CD1C18"],
        "MSFT": ["#1D43B5", "#214DCF", "#305CDE"],
        "JPM": ["#9B5600", "#B16200", "#C76E00"],
        "V": ["#0000AA", "#0000C6", "#0000E3"],
    }
    group_tickers = []
    for ticker in tickers:
        group_tickers += [ticker, "", ""]

    fill_colors = []
    ticker_colors = []
    for ticker in tickers:
        fill_colors += colorway[ticker]
        ticker_colors += [colorway[ticker][0]]*3

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(results_df.columns),
            align=['left', 'center', 'center'],
            font=dict(size=14, color='white'),
            height=40,
        ),
        cells=dict(
            values=[group_tickers, results_df.Model, results_df.R2],
            align='left',
            fill_color=[ticker_colors, fill_colors, fill_colors],
            font=dict(size=12, color='white'),
            height=20,
        )
    )])

    fig.update_layout(
        title="Model Comparison",
        height=800,
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(
        page_title="2024 Q1 Earnings Analysis",
        page_icon="📈",
    )
    st.title("2024 Q1 Earnings Event Study Analysis")
    st.markdown("### NVIDIA Shock & Tesla's Promises")
    st.markdown("*20 min read*")

    st.markdown("""
    ## Introduction
    NVIDIA's stock prices surged when they announced their spectacular Q1 earnings, beating the market expectations. This surge even lead to a stock-split.
    Marking a new era in the semiconductor industry, and fueled the market's expectations for other technological companies working in the AI, software, and hardware sectors.
    """)
    st.image("src/pages/texts/2024_q1_earnings/news_headlines.png", use_column_width=True)
    st.markdown("""
    In this analysis, we will compare the abnormal returns of NVIDIA with other companies such as TSMC, Apple, Visa and more, to answer the question
    """)
    st.markdown("<h4 style='text-align: center; color: white;'>Which company's earning calls had the most impact to their stock prices?</h4>", unsafe_allow_html=True)


    st.markdown("""
    ## Methods
    We will measure an impact of an earning call using the **Event Study Analysis**. This analysis is a statistical method used to measure the impact of a specific event on the value of a company.
    To measure the impact, we need to calculate the **abnormal returns** of the company's stock prices.
    For this analysis, we investigate three models to calculate the abnormal returns:
    - **Constant Mean Return (CMR)**
    - **Capital Asset Pricing Model (CAPM)**
    - **Fama-French Three-Factor Model (FF)**
    """)

    st.markdown("""
    ### Constant Mean Return (CMR)

    """)
    display_model_comparison()

if __name__ == "__main__":
    main()
