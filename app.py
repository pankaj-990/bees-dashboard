import datetime as dt
from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

DEFAULT_TICKERS: Dict[str, str] = {
    "Nifty BeES": "NIFTYBEES.NS",
    "Bank BeES": "BANKBEES.NS",
    "Gold BeES": "GOLDBEES.NS",
    "Silver BeES": "SILVERBEES.NS",
    "Hang Seng BeES": "HNGSNGBEES.NS",
    "MON 100": "MON100.NS",
}


@st.cache_data(ttl=60 * 60)
def download_weekly_data(tickers: List[str], years: int = 7) -> pd.DataFrame:
    end = dt.date.today()
    start = end - dt.timedelta(days=365 * years)
    data = yf.download(
        tickers,
        start=start,
        end=end,
        interval="1wk",
        auto_adjust=True,
        group_by="ticker",
        progress=False,
    )
    if isinstance(data.columns, pd.MultiIndex):
        return data
    # Single ticker: normalize to MultiIndex-like structure
    data.columns = pd.MultiIndex.from_product([[tickers[0]], data.columns])
    return data


def build_chart(df: pd.DataFrame, label: str, ticker: str) -> go.Figure:
    if ticker not in df.columns.get_level_values(0):
        raise ValueError(f"No data returned for {ticker}")

    close = df[ticker]["Close"].dropna()
    sma_30 = close.rolling(window=30, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=close.index,
            y=close.values,
            name=f"{label} Close",
            line=dict(width=2.5, color="#1F77B4"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sma_30.index,
            y=sma_30.values,
            name="30W SMA",
            line=dict(width=2.5, color="#FF7F0E"),
        )
    )

    fig.update_layout(
        title=f"{label} ({ticker}) - Weekly Close & 30W SMA",
        xaxis_title="Week",
        yaxis_title="Price",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=70, b=40),
        template="plotly_white",
        paper_bgcolor="#FAFAFA",
        plot_bgcolor="#FFFFFF",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E6E6E6", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E6E6E6", zeroline=False)
    fig.update_traces(hovertemplate="%{x|%Y-%m-%d}<br>%{y:.2f}<extra></extra>")
    return fig


st.set_page_config(page_title="BeES Weekly Dashboard", layout="wide")

st.title("BeES Weekly Dashboard")
st.caption("Weekly data from Yahoo Finance with 30-week simple moving average.")

custom = DEFAULT_TICKERS
years = int(st.session_state.get("years", 7))

selected = [t for t in custom.values() if t.strip()]

with st.spinner("Downloading weekly data..."):
    data = download_weekly_data(selected, years=years)

st.subheader("Charts")
cols = st.columns(2)
for idx, (label, ticker) in enumerate(custom.items()):
    if not ticker.strip():
        continue
    try:
        fig = build_chart(data, label, ticker)
    except Exception as exc:
        st.warning(f"{label} ({ticker}) - {exc}")
        continue
    with cols[idx % 2]:
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Raw Weekly Data")
st.dataframe(data.tail(20), use_container_width=True)

st.subheader("Controls")
st.slider(
    "History (years)",
    min_value=2,
    max_value=15,
    value=years,
    step=1,
    key="years",
)
if st.button("Refresh data"):
    download_weekly_data.clear()
    st.rerun()
