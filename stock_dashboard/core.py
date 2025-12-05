import requests
import numpy as np
import pandas as pd
import yfinance as yf

# ------------------ CONFIG ------------------

NSE_URL = "https://www.nseindia.com/api/quote-equity?symbol={symbol}"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

DEFAULT_SYMBOL = "RELIANCE"
DEFAULT_WATCHLIST = "RELIANCE, TCS, SBIN, INFY, HDFCBANK"

# ------------------ DATA FETCH ------------------


def get_live_price(symbol: str) -> float | None:
    try:
        r = requests.get(
            NSE_URL.format(symbol=symbol.upper()),
            headers=HEADERS,
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        return float(data["priceInfo"]["lastPrice"])
    except Exception:
        return None


def get_history(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame | None:
    try:
        df = yf.download(
            symbol.upper() + ".NS",
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False,
        )
        if df is None or df.empty:
            return None
        return df
    except Exception:
        return None


# ------------------ INDICATORS ------------------


def calc_sma(series: pd.Series, window: int) -> float | None:
    if series is None or len(series) < window:
        return None
    return float(series.tail(window).mean())


def calc_ema(series: pd.Series, window: int) -> float | None:
    if series is None or len(series) < window:
        return None
    ema = series.ewm(span=window, adjust=False).mean()
    return float(ema.iloc[-1])


def calc_rsi(series: pd.Series, period: int = 14) -> float | None:
    if series is None:
        return None
    values = np.asarray(series, dtype="float64")
    if values.size < period + 1:
        return None

    deltas = np.diff(values)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    avg_gain = gains[-period:].mean()
    avg_loss = losses[-period:].mean()
    if np.isnan(avg_gain) or np.isnan(avg_loss):
        return None
    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi_val = 100 - (100 / (1 + rs))
    return float(rsi_val)


def calc_macd(series: pd.Series) -> tuple[float | None, float | None]:
    if series is None or len(series) < 35:
        return None, None
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return float(macd_line.iloc[-1]), float(signal_line.iloc[-1])


def calc_sr(series: pd.Series, window: int = 30) -> tuple[float | None, float | None]:
    if series is None or len(series) < window:
        return None, None
    recent = series.tail(window)
    return float(recent.min()), float(recent.max())


def volume_check(series: pd.Series, window: int = 20) -> tuple[float | None, float | None, float | None]:
    if series is None or len(series) < window + 1:
        return None, None, None
    avg = float(series.tail(window).mean())
    last = float(series.iloc[-1])
    ratio = None if avg == 0 else last / avg
    return last, avg, ratio


# ------------------ BACKTEST (SMA CROSSOVER) ------------------


def sma_crossover_backtest(df: pd.DataFrame, fast: int = 20, slow: int = 50) -> dict | None:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return None
    if "Close" not in df.columns:
        return None

    close = df["Close"]
    min_req = max(fast, slow) + 10
    if len(close) < min_req:
        return None

    fast_sma = close.rolling(fast, min_periods=fast).mean()
    slow_sma = close.rolling(slow, min_periods=slow).mean()

    if not isinstance(fast_sma, pd.Series) or not isinstance(slow_sma, pd.Series):
        return None
    if fast_sma.dropna().shape[0] < 10 or slow_sma.dropna().shape[0] < 10:
        return None

    bt = pd.DataFrame(
        {
            "close": close,
            "fast": fast_sma,
            "slow": slow_sma,
        }
    ).dropna()

    if bt.empty or bt.shape[0] < 10:
        return None

    bt["signal"] = (bt["fast"] > bt["slow"]).astype(int)
    bt["position"] = bt["signal"].shift().fillna(0)

    bt["ret"] = bt["close"].pct_change()
    bt["strategy_ret"] = bt["ret"] * bt["position"]

    bt["bh_curve"] = (1 + bt["ret"]).cumprod()
    bt["strat_curve"] = (1 + bt["strategy_ret"]).cumprod()

    strat = float((bt["strat_curve"].iloc[-1] - 1) * 100)
    bh = float((bt["bh_curve"].iloc[-1] - 1) * 100)

    return {
        "data": bt,
        "strategy_return_pct": strat,
        "buy_hold_return_pct": bh,
    }


# ------------------ RANKING ENGINE SCORE ------------------


def rank_score(symbol: str, df: pd.DataFrame, live: float) -> dict:
    """Return dict with score + components for ranking engine."""
    close = df["Close"]
    vol = df["Volume"]

    sma5 = calc_sma(close, 5)
    sma20 = calc_sma(close, 20)
    ema12 = calc_ema(close, 12)
    ema26 = calc_ema(close, 26)
    rsi = calc_rsi(close, 14)
    mac, sig = calc_macd(close)
    sup, res = calc_sr(close, 30)
    lastv, avgv, relv = volume_check(vol, 20)

    score = 0

    # Trend
    if sma5 and sma20 and sma5 > sma20:
        score += 20
    if ema12 and ema26 and ema12 > ema26:
        score += 20

    # MACD
    if mac and sig and mac > sig:
        score += 15

    # RSI
    if rsi:
        if 45 <= rsi <= 60:
            score += 15
        if 60 < rsi <= 70:
            score += 10

    # Near support
    if sup and res and live:
        gap = res - sup
        if gap > 0:
            dist = live - sup
            if dist >= 0:
                pct = dist / gap * 100
                if pct <= 25:
                    score += 15

    # Volume
    if relv and relv >= 1.2:
        score += 15

    if score >= 75:
        grade = "🔥 STRONG BUY"
    elif score >= 60:
        grade = "BUY"
    elif score >= 40:
        grade = "HOLD"
    elif score >= 20:
        grade = "WEAK"
    else:
        grade = "BEARISH"

    return {
        "Symbol": symbol,
        "LTP": round(live, 2) if live else None,
        "Score": score,
        "Grade": grade,
        "RSI": round(rsi, 2) if rsi else None,
        "RelVol": round(relv, 2) if relv else None,
    }


# ------------------ SIMPLE BREAKOUT DETECTION ------------------


def detect_breakout(df: pd.DataFrame) -> str:
    """Very simple breakout/breakdown text label based on last close vs recent range."""
    if df is None or df.empty:
        return "No data"
    close = df["Close"]
    last = float(close.iloc[-1])
    recent = close.tail(30)
    hi = float(recent.max())
    lo = float(recent.min())

    # near breakout up
    if last >= hi * 0.995:
        return "Resistance Breakout 🔼"
    # near breakdown
    if last <= lo * 1.005:
        return "Support Breakdown 🔽"
    return "In Range"
