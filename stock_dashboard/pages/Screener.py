import streamlit as st
import pandas as pd
from core import (
    DEFAULT_WATCHLIST,
    get_live_price,
    get_history,
    calc_sma,
    calc_rsi,
    calc_macd,
)

st.title("📋 Simple Trend Screener + Swing Picks")

wl_raw = st.sidebar.text_area("Watchlist (comma separated)", DEFAULT_WATCHLIST)
wl = [s.strip().upper() for s in wl_raw.split(",") if s.strip()]

rows = []

for sym in wl:
    lp = get_live_price(sym)
    h = get_history(sym, "3mo", "1d")

    if lp is None or h is None:
        rows.append({"Symbol": sym, "Price": "--", "SMA5>SMA20": "--", "View": "Data Error"})
        continue

    close = h["Close"]
    s5 = calc_sma(close, 5)
    s20 = calc_sma(close, 20)

    if s5 is not None and s20 is not None:
        if s5 > s20:
            stat = "Yes"
            view = "Bullish"
        elif s5 < s20:
            stat = "No"
            view = "Bearish"
        else:
            stat = "Equal"
            view = "Sideways"
    else:
        stat = "--"
        view = "Weak / Insufficient"

    rows.append(
        {
            "Symbol": sym,
            "Price": round(lp, 2),
            "SMA5>SMA20": stat,
            "View": view,
        }
    )

st.subheader("Trend Screener")
st.dataframe(pd.DataFrame(rows), use_container_width=True)

# Swing picks
st.markdown("---")
st.subheader("🔥 Swing Buy Candidates (Indicators Based)")

picks = []

for sym in wl:
    lp = get_live_price(sym)
    h = get_history(sym, "6mo", "1d")
    if lp is None or h is None:
        continue

    close = h["Close"]

    s5 = calc_sma(close, 5)
    s20 = calc_sma(close, 20)
    r = calc_rsi(close, 14)
    m, sig = calc_macd(close)

    cond_sma = s5 is not None and s20 is not None and s5 > s20
    cond_rsi = r is not None and 45 <= r <= 60
    cond_macd = m is not None and sig is not None and m > sig

    if cond_sma and cond_rsi and cond_macd:
        picks.append(
            {
                "Symbol": sym,
                "Price": round(lp, 2),
                "RSI14": round(r, 2),
                "SMA5>SMA20": "Yes",
                "MACD>Signal": "Yes",
            }
        )

if picks:
    st.success("Potential Swing BUY candidates:")
    st.dataframe(pd.DataFrame(picks), use_container_width=True)
else:
    st.info("No ideal swing setups found right now.")
