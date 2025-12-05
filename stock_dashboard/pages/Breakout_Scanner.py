import streamlit as st
import pandas as pd
from core import (
    DEFAULT_WATCHLIST,
    get_live_price,
    get_history,
    detect_breakout,
)

st.title("📌 Breakout / Breakdown Scanner")

wl_raw = st.sidebar.text_area("Watchlist", DEFAULT_WATCHLIST)
wl = [s.strip().upper() for s in wl_raw.split(",") if s.strip()]

rows = []

for sym in wl:
    live = get_live_price(sym)
    h = get_history(sym, "6mo", "1d")

    if live is None or h is None:
        rows.append({"Symbol": sym, "Price": "--", "Breakout Status": "Data Error"})
        continue

    status = detect_breakout(h)
    rows.append({"Symbol": sym, "Price": round(live, 2), "Breakout Status": status})

st.dataframe(pd.DataFrame(rows), use_container_width=True)
