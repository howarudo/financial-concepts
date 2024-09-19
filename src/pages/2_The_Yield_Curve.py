import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import plotly.graph_objects as go
import yfinance as yahooFinance
import streamlit as st
from plotly.subplots import make_subplots

DATA_PATH = 'data/'
TREASURY_YIELD_CURVE = 'treasury_yield_curve.csv'
MATURITY_TO_DT = {
    "3 Mo": pd.DateOffset(months=3),
    "6 Mo": pd.DateOffset(months=6),
    "1 Yr": pd.DateOffset(years=1),
    "2 Yr": pd.DateOffset(years=2),
    "3 Yr": pd.DateOffset(years=3),
    "5 Yr": pd.DateOffset(years=5),
    "7 Yr": pd.DateOffset(years=7),
    "10 Yr": pd.DateOffset(years=10),
    "20 Yr": pd.DateOffset(years=20),
    "30 Yr": pd.DateOffset(years=30)
}
NORMAL_YIELD_DATE = "2022-03-02"
INVERTED_YIELD_DATE = "2007-03-15"

SHORT_TERM_MATURITY = "3 Mo"
LONG_TERM_MATURITY = "10 Yr"

def plot_3d_yield_curve(df):
    # fill as 3d array
    current_dates = []
    yields = []
    maturity_dates = []

    for date in df.index:
        for key, value in MATURITY_TO_DT.items():
            current_dates.append(date)
            yields.append(df[key][date])
            maturity_dates.append(date + value)

    # interpolate
    current_dates_num = pd.to_datetime(current_dates).map(pd.Timestamp.toordinal)
    maturity_dates_num = pd.to_datetime(maturity_dates).map(pd.Timestamp.toordinal)

    grid_x, grid_y = np.mgrid[
        current_dates_num.min():current_dates_num.max():100j,
        maturity_dates_num.min():maturity_dates_num.max():100j
        ]

    grid_z = griddata(
        (current_dates_num, maturity_dates_num),
        yields,
        (grid_x, grid_y),
        method='linear'
        )

    # Create the surface plot
    fig = go.Figure(data=[go.Surface(x=grid_x, y=grid_y, z=grid_z)])

    # Define tick positions and labels
    tickvals_x = np.linspace(current_dates_num.min(), current_dates_num.max(), 10)
    tickvals_y = np.linspace(maturity_dates_num.min(), maturity_dates_num.max(), 10)
    ticktext_x = [pd.Timestamp.fromordinal(int(val)).strftime('%Y-%m') for val in tickvals_x]
    ticktext_y = [pd.Timestamp.fromordinal(int(val)).strftime('%Y-%m') for val in tickvals_y]

    # Update layout
    fig.update_layout(
        title='Yield Curve Surface Plot',
        scene=dict(
            xaxis=dict(
                title='Current Date',
                tickmode='array',
                tickvals=tickvals_x,
                ticktext=ticktext_x
            ),
            yaxis=dict(
                title='Maturity Date',
                tickmode='array',
                tickvals=tickvals_y,
                ticktext=ticktext_y
            ),
            zaxis_title='Yield'
        ),
        width=800,
        height=800
    )

    # fix the x-axis range and y-axis range
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    st.plotly_chart(fig, use_container_width=True)

    return

def plot_normal_yield_curve(df):
    fig = go.Figure()
    normal_yields = df.loc[NORMAL_YIELD_DATE]
    fig.add_trace(go.Scatter(x=normal_yields.index, y=normal_yields, name='Yield Curve'))
    fig.add_trace(go.Scatter(x=normal_yields.index, y=normal_yields, mode='lines', name='Yield Curve'))
    fig.update_layout(
        title=f'Normal Yield Curve on {NORMAL_YIELD_DATE}',
        xaxis_title='Maturity',
        yaxis_title='Yield',
        width=600, height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    return

def plot_inverted_yield_curve(df):
    fig = go.Figure()
    inverted_yields = df.loc[INVERTED_YIELD_DATE]
    fig.add_trace(go.Scatter(x=inverted_yields.index, y=inverted_yields, name='Yield Curve'))
    fig.add_trace(go.Scatter(x=inverted_yields.index, y=inverted_yields, mode='lines', name='Yield Curve'))
    fig.update_layout(
        title=f'Inverted Yield Curve on {INVERTED_YIELD_DATE}',
        xaxis_title='Maturity',
        yaxis_title='Yield',
        width=600, height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    return

def plot_yield_curve_by_maturity(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['3 Mo'], mode='lines', name='3 Mo'))
    fig.add_trace(go.Scatter(x=df.index, y=df['1 Yr'], mode='lines', name='1 Yr'))
    fig.add_trace(go.Scatter(x=df.index, y=df['5 Yr'], mode='lines', name='5 Yr'))
    fig.add_trace(go.Scatter(x=df.index, y=df['10 Yr'], mode='lines', name='10 Yr'))

    fig.update_layout(
        title='Yield Curve',
        xaxis_title='Date',
        yaxis_title='Yield',
        width=800, height=600,
        legend_title='Maturity',
        colorway=["#FFFFED", "#FFD000", "#FFA500", "#FF2600"]
        )

    st.plotly_chart(fig, use_container_width=True)

    return

def plot_yield_and_spy(df):
    spy = yahooFinance.Ticker('SPY').history(start=df.index.min(), end=df.index.max())[::5]["Close"]
    interest_rate = (spy / spy.shift(1) - 1)
    moving_avg = interest_rate.rolling(window=30).mean()

    spread = df[LONG_TERM_MATURITY] - df[SHORT_TERM_MATURITY]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df.index, y=spread, mode='lines', name='Spread'), secondary_y=False)
    fig.add_trace(go.Scatter(x=interest_rate.index, y=moving_avg, mode='lines', name='SPY 30 day MVA'), secondary_y=True)
    fig.update_layout(
        title='Yield Spread and SPY 30-Day MVA',
        xaxis_title='Date',
        yaxis_title='Yield Spread',
        width=800, height=600,
        colorway=["#FF2511", "#E2DED0"]
    )

    st.plotly_chart(fig, use_container_width=True)

    return

def read_df():
    df = pd.read_csv(DATA_PATH + TREASURY_YIELD_CURVE)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')

    return df

def main():
    st.set_page_config(
        page_title="The Yield Curve",
        page_icon="📈",
    )

    df = read_df()

    st.title("The Yield Curve")
    plot_normal_yield_curve(df)
    plot_inverted_yield_curve(df)
    plot_yield_curve_by_maturity(df)
    plot_yield_and_spy(df)
    plot_3d_yield_curve(df)

    return

if __name__ == "__main__":
    main()
