import streamlit as st
import pandas as pd
from core import DEFAULT_WATCHLIST, get_history

st.title("🏦 Institutional Flow Style View (Volume Based)")

wl_raw = st.sidebar.text_area("Watchlist", DEFAULT_WATCHLIST)
wl = [s.strip().upper() for s in wl_raw.split(",") if s.strip()]

rows = []

for sym in wl:
    h = get_history(sym, "3mo", "1d")
    if h is None:
        rows.append({"Symbol": sym, "Flow": "No data"})
        continue

    close = h["Close"]
    vol = h["Volume"]

    if len(close) < 10:
        rows.append({"Symbol": sym, "Flow": "Too few candles"})
        continue

    # simplest approach: last 10 candles up vs down volume
    df = pd.DataFrame({"close": close, "vol": vol}).dropna().tail(10)
    df["chg"] = df["close"].diff()
    df["up_vol"] = df.apply(lambda r: r["vol"] if r["chg"] > 0 else 0, axis=1)
    df["down_vol"] = df.apply(lambda r: r["vol"] if r["chg"] < 0 else 0, axis=1)

    up_sum = df["up_vol"].sum()
    down_sum = df["down_vol"].sum()

    if up_sum > down_sum * 1.3:
        flow = "Strong Accumulation 🟢"
    elif down_sum > up_sum * 1.3:
        flow = "Strong Distribution 🔴"
    else:
        flow = "Mixed / Neutral"

    rows.append({"Symbol": sym, "Flow": flow})

st.dataframe(pd.DataFrame(rows), use_container_width=True)
