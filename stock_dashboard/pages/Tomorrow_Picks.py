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

st.title("🌟 Top Picks for Tomorrow (Daily + Intraday View)")

wl_raw = st.sidebar.text_area("Watchlist", DEFAULT_WATCHLIST)
wl = [s.strip().upper() for s in wl_raw.split(",") if s.strip()]

picks = []

for sname in wl:
    live = get_live_price(sname)
    hist = get_history(sname, "6mo", "1d")

    if live is None or hist is None:
        continue

    close = hist["Close"]
    rsi   = calc_rsi(close, 14)
    s5    = calc_sma(close, 5)
    s20   = calc_sma(close, 20)
    mac, sig = calc_macd(close)

    if any(v is None for v in [rsi, s5, s20, mac, sig]):
        continue

    # Conditions
    cond_trend = s5 > s20           # uptrend
    cond_rsi_good = 45 <= rsi <= 65 # thoda wide range
    cond_macd = mac > sig           # momentum

    # Score system instead of strict AND
    score = 0
    if cond_trend:
        score += 40
    if cond_rsi_good:
        score += 30
    if cond_macd:
        score += 30

    # 50+ ko hi pick karo (you can adjust)
    if score >= 50:
        picks.append({
            "Symbol": sname,
            "LTP": round(live, 2),
            "RSI(14)": round(rsi, 2),
            "SMA5>SMA20": "Yes" if cond_trend else "No",
            "MACD>Signal": "Yes" if cond_macd else "No",
            "Score": score,
        })

# Show sorted by score
if picks:
    import pandas as pd
    df = pd.DataFrame(picks).sort_values("Score", ascending=False)
    st.success("Shortlisted candidates for next sessions (score based):")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Even after relaxed scoring, no suitable tomorrow-picks found.")
