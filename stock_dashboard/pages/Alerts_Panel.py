import streamlit as st
import pandas as pd
from core import (
    DEFAULT_WATCHLIST,
    get_live_price,
    get_history,
    calc_rsi,
    calc_macd,
    calc_sma,
)

st.title("🚨 Live Alerts Panel")

wl_raw = st.sidebar.text_area("Watchlist", DEFAULT_WATCHLIST)
wl = [s.strip().upper() for s in wl_raw.split(",") if s.strip()]

alerts = []

for sym in wl:
    live = get_live_price(sym)
    h = get_history(sym, "3mo", "1d")

    if live is None or h is None:
        continue

    close = h["Close"]

    r = calc_rsi(close, 14)
    m, sig = calc_macd(close)
    s5 = calc_sma(close, 5)
    s20 = calc_sma(close, 20)

    note_list = []

    if r is not None:
        if r < 30:
            note_list.append("RSI Oversold (<30)")
        elif r > 70:
            note_list.append("RSI Overbought (>70)")

    if m is not None and sig is not None:
        if m > sig:
            note_list.append("MACD Bullish Cross")
        elif m < sig:
            note_list.append("MACD Bearish Cross")

    if s5 is not None and s20 is not None:
        if s5 > s20:
            note_list.append("Short-term Uptrend (SMA5>SMA20)")
        elif s5 < s20:
            note_list.append("Short-term Downtrend (SMA5<SMA20)")

    if note_list:
        alerts.append(
            {
                "Symbol": sym,
                "Price": round(live, 2),
                "Alerts": " | ".join(note_list),
            }
        )

if alerts:
    st.subheader("Active Alerts")
    st.dataframe(pd.DataFrame(alerts), use_container_width=True)
else:
    st.info("No special alert conditions triggered right now.")
