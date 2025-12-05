import streamlit as st
import pandas as pd
from core import (
    DEFAULT_WATCHLIST,
    get_live_price,
    get_history,
    rank_score,
)

st.title("🏆 Smart Stock Ranking Engine")

wl_raw = st.sidebar.text_area("Watchlist (comma separated)", DEFAULT_WATCHLIST)
wl = [s.strip().upper() for s in wl_raw.split(",") if s.strip()]

rankings = []

for sym in wl:
    live = get_live_price(sym)
    h = get_history(sym, "6mo", "1d")

    if live is None or h is None:
        rankings.append(
            {
                "Symbol": sym,
                "LTP": None,
                "Score": 0,
                "Grade": "Data Error",
                "RSI": None,
                "RelVol": None,
            }
        )
        continue

    info = rank_score(sym, h, live)
    rankings.append(info)

df = pd.DataFrame(rankings)
df = df.sort_values(by="Score", ascending=False)

st.subheader("Full Ranking Table")
st.dataframe(df, use_container_width=True)

st.markdown("---")
best = df[df["Score"] >= 70]
if not best.empty:
    st.success("📌 Top Ranked Stocks (Score ≥ 70):")
    st.table(best[["Symbol", "Score", "Grade"]])
else:
    st.info("No strong bullish stocks at the moment based on current ranking model.")
