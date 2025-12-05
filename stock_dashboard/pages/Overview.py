import time
import streamlit as st
import pandas as pd
from core import (
    get_live_price,
    get_history,
    calc_sma,
    calc_ema,
    calc_rsi,
    calc_macd,
    calc_sr,
    volume_check,
    DEFAULT_SYMBOL,
)

st.title("📈 Overview – Live Price & Indicators")

sym = st.sidebar.text_input("NSE Symbol", DEFAULT_SYMBOL).upper() or DEFAULT_SYMBOL
auto = st.sidebar.checkbox("Auto refresh", True)
sec = st.sidebar.slider("Refresh seconds", 5, 60, 10)

st.sidebar.markdown("---")
smaF = st.sidebar.slider("SMA Fast", 3, 30, 5)
smaS = st.sidebar.slider("SMA Slow", 10, 120, 20)
emaF = st.sidebar.slider("EMA Fast", 5, 30, 12)
emaS = st.sidebar.slider("EMA Slow", 10, 60, 26)
rsiP = st.sidebar.slider("RSI period", 7, 30, 14)

if auto:
    time.sleep(sec)

col1, col2 = st.columns(2)

# --- live price history state ---
if "ph" not in st.session_state:
    st.session_state["ph"] = {}
if sym not in st.session_state["ph"]:
    st.session_state["ph"][sym] = []

with col1:
    st.subheader(f"Live Price: {sym}")
    lp = get_live_price(sym)
    if lp is not None:
        st.metric("LTP (₹)", f"{lp:,.2f}")
        st.session_state["ph"][sym].append(lp)
    else:
        st.error("Could not fetch live price.")

    ph = st.session_state["ph"][sym]
    if len(ph) > 1:
        st.line_chart(ph, height=260, use_container_width=True)
    else:
        st.info("Waiting for a few ticks...")

with col2:
    st.subheader("Daily Technicals (6 Months)")

    h = get_history(sym, "6mo", "1d")
    if h is None:
        st.error("No history available.")
    else:
        close = h["Close"]
        vol = h["Volume"]

        sF = calc_sma(close, smaF)
        sS = calc_sma(close, smaS)
        eF = calc_ema(close, emaF)
        eS = calc_ema(close, emaS)
        rsi = calc_rsi(close, rsiP)
        mac, sig = calc_macd(close)
        sp, rs = calc_sr(close)
        lv, av, rv = volume_check(vol)

        def f(x):
            return f"{x:.2f}" if x is not None else "--"

        st.write(f"SMA({smaF}): {f(sF)}")
        st.write(f"SMA({smaS}): {f(sS)}")
        st.write(f"EMA({emaF}): {f(eF)}")
        st.write(f"EMA({emaS}): {f(eS)}")
        st.write(f"RSI({rsiP}): {f(rsi)}")
        st.write(f"MACD / Signal: {f(mac)} / {f(sig)}")
        st.write(f"Support / Resistance: {f(sp)} / {f(rs)}")

        st.markdown("---")
        st.write("Volume (Last vs 20D Avg)")
        if lv is not None:
            st.write(f"Last Volume: {int(lv):,}")
            st.write(f"20D Avg: {int(av):,}")
            st.write(f"Relative Volume: {rv:.2f}x")
        else:
            st.write("Not enough volume data.")

        st.markdown("---")
        st.subheader("Final Signal")

        signal = "Not Enough Data"
        col = "gray"
        if all(v is not None for v in [sF, sS, eF, eS, rsi, mac, sig]):
            if sF > sS and eF > eS and mac > sig and rsi > 50:
                signal = "BUY"
                col = "green"
            elif sF < sS and eF < eS and mac < sig and rsi < 50:
                signal = "SELL"
                col = "red"
            else:
                signal = "HOLD"
                col = "orange"

        st.markdown(
            f"<h2 style='text-align:center;color:{col}'>{signal}</h2>",
            unsafe_allow_html=True,
        )
