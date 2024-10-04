import pandas as pd
import numpy as np
import yfinance as yahooFinance
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import n_colors
from scipy import stats
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
    ff_coeff_df = pd.read_csv("data/F-F_Research_Data_Factors_daily.csv")
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
    """
    Displays the model comparison table from data/model_comparison.csv
    """
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
        height=570,
        margin=dict(b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_AR(ticker):
    """
    Returns the plot of the abnormal returns of the ticker, and the z-score and p-value of the earning date.
    """
    prices = get_ticker_df(ticker)
    returns = get_returns(prices["Close"].values)
    market_prices = get_ticker_df("^GSPC")
    market_returns = get_returns(market_prices["Close"].values)
    model_returns, ar_returns, ar_std, mva_ar_returns = get_AR_FF(returns, market_returns)
    earning_date = prices.index[prices.index.date == pd.to_datetime(TICKERS2CALLDATE[ticker]).date()][0]
    earning_index = prices.index.get_loc(earning_date)
    z_score = mva_ar_returns[earning_index] / ar_std / np.sqrt(EVENT_WINDOW[0] + EVENT_WINDOW[1])
    p_value = (1 - stats.norm.cdf(z_score)) / 2

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prices.index, y=ar_returns, name="AR"))
    fig.add_vline(x=earning_date, line_dash="dash", line_color="blue", line_width=2, name="Earning Call")
    fig.add_trace(go.Scatter(x=prices.index[EVENT_WINDOW[0]:-EVENT_WINDOW[1]], y=mva_ar_returns, name="MVA AR"))
    fig.add_hrect(y0=-ar_std, y1=ar_std, fillcolor="#F0E68C", opacity=0.2, layer="below", line_width=0)
    fig.update_layout(
        title=f"{ticker} Abnormal Returns",
        xaxis_title="Date",
        yaxis_title="Abnormal Returns",
        showlegend=True,
        colorway=["lightgrey", "red", "black"]
        )

    return fig, z_score, p_value

def get_all_AR():
    """
    Returns the plot data, z-scores, and p-values of all the tickers.
    """
    plot_data = {}
    z_scores = {}
    p_values = {}
    for ticker in TICKERS2CALLDATE.keys():
        plot_data[ticker], z_scores[ticker], p_values[ticker] = plot_AR(ticker)
    return plot_data, z_scores, p_values

def display_z_score_p_value(z_scores, p_values):
    df = pd.DataFrame({"Ticker": list(z_scores.keys()), "Z-Score": list(z_scores.values()), "P-Value": list(p_values.values())})
    red_colors = n_colors("rgb(50, 20, 20)", "rgb(200, 50, 50)", 100, colortype="rgb")
    green_colors = n_colors("rgb(1, 50, 32)", "rgb(20, 200, 50)", 100, colortype="rgb")[::-1]
    colorway = []
    for z_score in df["Z-Score"]:
        z_score = int(z_score*100)
        if z_score < 0:
            colorway.append(red_colors[z_score])
        else:
            colorway.append(green_colors[z_score])
    df["P-Value"] = df["P-Value"].apply(lambda x: f"{x:.4f}")
    df["Z-Score"] = df["Z-Score"].apply(lambda x: f"{x:.2f}")
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df.columns),
            align=['left', 'center', 'center'],
            font=dict(size=14, color='white'),
            height=40,
        ),
        cells=dict(
            values=[df.Ticker, df["Z-Score"], df["P-Value"]],
            align='left',
            fill_color=[colorway, colorway, colorway],
            font=dict(size=12, color='white'),
            height=20,
        )
    )])
    fig.update_layout(
        title="Z-Score and P-Value",
        height=290,
        margin=dict(b=0),
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
    ### Models
    #### Constant Mean Return (CMR)
    The CMR model assumes that the stock prices have a constant mean return.
    $$
    R_{t} = \mu + \epsilon_{t} \\newline
    E[\epsilon_{t}] = 0, Var[\epsilon_{t}] = \sigma^{2}
    $$
    $R_{t}$: Return at time t, $\mu$: Mean return, $\epsilon_{t}$: Error term, $\sigma^{2}$: Variance of the error term \n
    This model assumes that the stock price does not fundamentally change over time, instead, the changes are due to random fluctuations. And it follows a normal distribution.
    """)

    st.markdown("""
    #### Capital Asset Pricing Model (CAPM)
    The CAPM model assumes that the returns are affected by the **market premium**, and the **risk-free rate**.
    $$
    R_{t} - R_{f} = \\beta(R_{m} - R_{f}) + \\epsilon_{t} \\newline
    E[\epsilon_{t}] = 0, Var[\epsilon_{t}] = \\sigma^{2}
    $$
    $R_{t}$: Return at time t, $R_{f}$: Risk-free rate, $R_{m}$: Market return, $\\beta$: Beta, the sensitivity of stock to the market.
    In this implementation we assume that $R_{f} = 0$ for simplicity.
    """)

    st.markdown("""
    #### Fama-French Three-Factor Model (FF)
    The FF model extends the CAPM model by adding two more factors: **SMB (Small Minus Big)** and **HML (High Minus Low)**.
    - **SMB**: Small Minus Big, the return difference between small-cap and large-cap stocks.
    - **HML**: High Minus Low, the return difference between value stocks (high BM ratio) and growth stocks (low BM ratio).
    The rationale behind this is that in the long term, small-cap tend to see higher returns tahn large-cap stocks. And value stocks tend to see higher returns than growth stocks.
    $$
    R_{t} - R_{f} = \\beta_{1}(R_{m} - R_{f}) + \\beta_{2}SMB + \\beta_{3}HML + \\epsilon_{t} \\newline
    $$
    $R_{t}$: Return at time t, $R_{f}$: Risk-free rate, $R_{m}$: Market return, $\\beta_{1}$: Market beta, $\\beta_{2}$: SMB beta, $\\beta_{3}$: HML beta.
    """)

    st.markdown("""
    ### Model Comparison
    We will compare the R-squared values of the three models to see which model fits the data the best.
    """)
    display_model_comparison()
    st.markdown("""
    After comparing the model performance from 2023-08-01 to 2024-08-01, we find that the FF model has the highest R-squared values for all the companies.
    Slightly beating the CAPM model, and significantly beating the CMR model.
    """)

    st.markdown("""
    ### Event Study Analysis
    The event study analysis is a statistical method used to measure the impact of a specific event on the value of a company. In this implementation, we will measure the impact of an earning call to the 5-day moving average of the abnormal returns - 2 days before and 3 days after the earning call.
    I wrote an introduction to the event study analysis in my previous post, you can read it [here](Event_Study_Analysis).
    Abnormal returns are calculated as follows:
    $$
    AR_{t} = R_{t} - R_{model} \\newline
    AR_{\\text{mva, t}} = \\frac{1}{n} \sum_{i=t-2}^{t+2} AR_{i}
    $$
    """)

    st.markdown("""
    ## Abnormal Returns Analysis
    We will analyze the abnormal returns during the earning calls of the following companies:
    - NVIDIA (NVDA), 2024-05-22
    - TSMC (TSM), 2024-04-18
    - Apple (AAPL), 2024-05-02
    - Tesla (TSLA), 2024-04-23
    - Microsoft (MSFT), 2024-04-25
    - JPMorgan Chase (JPM), 2024-04-12
    - Visa (V), 2024-04-24

    For each company, we will calculate the abnormal returns using the FF model, get the 5 day moving average of the abnormal returns, and calculate the z-score and p-value of the earning date.
    $$
    Z = \\frac{AR_{\\text{mva, t}}}{\\sigma_{AR} \\sqrt{n}}
    $$
    """)
    plot_data, z_scores, p_values = get_all_AR()
    display_z_score_p_value(z_scores, p_values)
    st.markdown("""
    From the z-score and p-value, we can see that NVIDIA and Tesla had the most impact on their stock prices during their earning calls.
    Trying the plot the abnormal returns of NVIDIA and Tesla, we can see that the abnormal returns are significantly higher than the normal fluctuations.
    """)

    st.plotly_chart(plot_data["NVDA"], use_container_width=True)
    st.plotly_chart(plot_data["TSLA"], use_container_width=True)

    st.markdown("""
    On the other hand, Apple, Microsoft, and Visa had a relatively small impact on their stock prices during their earning calls.
    """)
    st.plotly_chart(plot_data["AAPL"], use_container_width=True)

    st.markdown("""
    ## Discussion
    NVIDIA reported spectacular Q1 earnings, beating the market expectations and had promising guidance for the future. This lead to a surge in their stock prices.
    On the other hand, although Tesla reported a decrease in earnings from last year's Q1, Elon Musk promised to deliver a more affordable design, something that the market has been waiting for.
    This also lead to a surge in their stock prices.
    """)

    st.markdown("""
    ## Conclusion
    In this analysis, we compared the impact of the earning calls of multiple companies, and how the market reacted to the news.
    It is understandable that the market reacted positively to NVIDIA's, but I found it interesting that Tesla's stock prices surged even after reporting a decrease in earnings.
    This just shows how unpredictable and complex the stock market can be.
    """)
if __name__ == "__main__":
    main()
