import streamlit as st
import pandas as pd
from core import DEFAULT_WATCHLIST, get_history

st.title("🧠 Pattern Style Hints (Very Simple)")

st.caption("Simple heuristic checks (NOT real pattern AI, but good for project demo).")

wl_raw = st.sidebar.text_area("Watchlist", DEFAULT_WATCHLIST)
wl = [s.strip().upper() for s in wl_raw.split(",") if s.strip()]

rows = []

for sym in wl:
    h = get_history(sym, "6mo", "1d")
    if h is None:
        rows.append({"Symbol": sym, "Pattern Hint": "No data"})
        continue

    close = h["Close"]
    if len(close) < 40:
        rows.append({"Symbol": sym, "Pattern Hint": "Too few candles"})
        continue

    recent = close.tail(40).reset_index(drop=True)

    # crude W-pattern check: 2 lows separated by higher middle
    low1 = recent[:15].min()
    low2 = recent[20:35].min()
    mid = recent[15:25].max()
    last = recent.iloc[-1]

    hint = "No clear pattern"

    if low1 and low2 and mid:
        if abs(low1 - low2) / low1 < 0.05 and mid > low1 * 1.05 and last > mid * 0.98:
            hint = "Possible W / Double Bottom pattern 🟢"

    # crude double top
    high1 = recent[:15].max()
    high2 = recent[20:35].max()
    mid2 = recent[15:25].min()
    if high1 and high2 and mid2:
        if abs(high1 - high2) / high1 < 0.05 and mid2 < high1 * 0.97 and last < mid2 * 1.02:
            hint = "Possible Double Top pattern 🔴"

    rows.append({"Symbol": sym, "Pattern Hint": hint})

st.dataframe(pd.DataFrame(rows), use_container_width=True)
