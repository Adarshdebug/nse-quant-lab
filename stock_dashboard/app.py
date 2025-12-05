import streamlit as st
from core import DEFAULT_SYMBOL, DEFAULT_WATCHLIST

st.set_page_config(page_title="NSE Quant Suite", layout="wide")

st.title("📊 NSE Quant Suite – Multi-Page Dashboard")
st.markdown("""
Welcome!  
Ye project multi-page **Streamlit trading analytics suite** hai:

**Pages:**
1. Overview – Live price + indicators  
2. Backtest – SMA crossover strategy  
3. Screener – Basic trend screener + swing picks  
4. Ranking Engine – Smart algo rank (Score /100)  
5. Breakout Scanner – Support/Resistance breakout check  
6. Alerts Panel – Live conditions based alerts  
7. Pattern AI – Simple pattern style checks  
8. Institutional Flow – Volume-based accumulation/distribution view  
9. Tomorrow Picks – Best candidates for next session

Left sidebar se **symbol & watchlist** change kar sakte ho.
""")

st.markdown(f"**Default symbol:** `{DEFAULT_SYMBOL}`")
st.markdown(f"**Default watchlist:** `{DEFAULT_WATCHLIST}`")
st.info("Use the pages in left sidebar (or top navigation) to explore each module.")
