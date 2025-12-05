import streamlit as st
from core import get_history, sma_crossover_backtest, DEFAULT_SYMBOL

st.title("📉 SMA Crossover Backtest")

sym = st.sidebar.text_input("Backtest Symbol", DEFAULT_SYMBOL).upper() or DEFAULT_SYMBOL
fast = st.sidebar.slider("Fast SMA", 5, 50, 20)
slow = st.sidebar.slider("Slow SMA", 20, 200, 50)

st.write(f"Backtesting **{sym}** for last 1 year with SMA {fast} / {slow}")

h = get_history(sym, "1y", "1d")
if h is None:
    st.error("No history data for backtest.")
else:
    res = sma_crossover_backtest(h, fast, slow)
    if res is None:
        st.warning("Not enough valid data / candles for this parameter combination.")
    else:
        st.write(f"Strategy Return: **{res['strategy_return_pct']:.2f}%**")
        st.write(f"Buy & Hold Return: **{res['buy_hold_return_pct']:.2f}%**")

        curves = res["data"][["bh_curve", "strat_curve"]]
        curves.columns = ["Buy & Hold", "Strategy"]
        st.line_chart(curves, height=300, use_container_width=True)

        csv = res["data"].to_csv(index=False)
        st.download_button(
            "Download Backtest CSV",
            csv,
            file_name=f"{sym}_backtest.csv",
            mime="text/csv",
        )
