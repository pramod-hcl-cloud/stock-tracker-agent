"""
Quantitative Engine for Technical Analysis, Multi-Currency FX Hedging, and Signal Generation.
Configured for:
- India Equities (HDFCBANK, HCLTECH) -> Displayed in Native INR (₹)
- Canada Equities (Shopify) -> Displayed in Native CAD ($)
- US Equities (Berkshire Hathaway, AAPL, United Healthcare) -> Displayed in CAD Hedged ($)
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

# =============================================================================
# ASSET SPECIFICATIONS & CURRENCY REGIMES
# =============================================================================
TRACKED_STOCKS = {
    "HDFCBANK": {
        "symbol": "HDFCBANK.NS",
        "display_name": "HDFCBANK (HDFC Bank - India)",
        "company": "HDFC Bank Ltd.",
        "base_currency": "INR",
        "target_currency": "INR",
        "currency_symbol": "₹",
        "exchange": "NSE (India)",
        "hedged_label": "Native INR",
        "is_cad_hedged": False
    },
    "HCLTECH": {
        "symbol": "HCLTECH.NS",
        "display_name": "HCLTECH (HCL Technologies - India)",
        "company": "HCL Technologies Ltd.",
        "base_currency": "INR",
        "target_currency": "INR",
        "currency_symbol": "₹",
        "exchange": "NSE (India)",
        "hedged_label": "Native INR",
        "is_cad_hedged": False
    },
    "Shopify": {
        "symbol": "SHOP.TO",
        "display_name": "Shopify (SHOP - TSX)",
        "company": "Shopify Inc.",
        "base_currency": "CAD",
        "target_currency": "CAD",
        "currency_symbol": "$",
        "exchange": "TSX (Canada)",
        "hedged_label": "Native CAD",
        "is_cad_hedged": False
    },
    "Berkshire Hathaway": {
        "symbol": "BRK-B",
        "display_name": "Berkshire Hathaway (BRK-B)",
        "company": "Berkshire Hathaway Inc. (Class B)",
        "base_currency": "USD",
        "target_currency": "CAD",
        "currency_symbol": "$",
        "exchange": "NYSE (USA)",
        "hedged_label": "CAD Hedged",
        "is_cad_hedged": True
    },
    "AAPL": {
        "symbol": "AAPL",
        "display_name": "AAPL (Apple Inc.)",
        "company": "Apple Inc.",
        "base_currency": "USD",
        "target_currency": "CAD",
        "currency_symbol": "$",
        "exchange": "NASDAQ (USA)",
        "hedged_label": "CAD Hedged",
        "is_cad_hedged": True
    },
    "United Healthcare": {
        "symbol": "UNH",
        "display_name": "United Healthcare (UNH)",
        "company": "UnitedHealth Group Inc.",
        "base_currency": "USD",
        "target_currency": "CAD",
        "currency_symbol": "$",
        "exchange": "NYSE (USA)",
        "hedged_label": "CAD Hedged",
        "is_cad_hedged": True
    }
}


def get_usdcad_fx_rate() -> float:
    """
    Retrieves the latest USD to CAD exchange rate (USDCAD=X) for CAD hedging US equities.
    """
    try:
        hist = yf.Ticker("USDCAD=X").history(period="5d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except Exception:
        pass
    return 1.4150  # Sturdy institutional fallback


def fetch_stock_data(asset_key: str, period: str = "3m") -> tuple[pd.DataFrame, dict]:
    """
    Fetches market data from yfinance, applies currency conversion / hedging
    according to asset specification (HDFC & HCLTech in INR, Shopify in CAD, US in CAD Hedged),
    and computes the quantitative technical indicators:
    - EMA12 = Close.ewm(span=12, adjust=False).mean()
    - EMA26 = Close.ewm(span=26, adjust=False).mean()
    - MACD = EMA12 - EMA26
    - Signal_Line = MACD.ewm(span=9, adjust=False).mean()
    - Histogram = MACD - Signal_Line
    - RSI (14-period)
    """
    if asset_key in TRACKED_STOCKS:
        cfg = TRACKED_STOCKS[asset_key]
        symbol = cfg["symbol"]
        base_curr = cfg["base_currency"]
        target_curr = cfg["target_currency"]
        curr_sym = cfg["currency_symbol"]
        display_name = cfg["display_name"]
        company = cfg["company"]
        exchange = cfg["exchange"]
        hedged_label = cfg["hedged_label"]
        is_cad_hedged = cfg["is_cad_hedged"]
    else:
        # Fallback for custom ticker entry
        symbol = asset_key.strip().upper()
        base_curr = "USD"
        target_curr = "USD"
        curr_sym = "$"
        display_name = symbol
        company = symbol
        exchange = "Global Equity"
        hedged_label = "Native USD"
        is_cad_hedged = False

    fetch_period = "3mo" if period in ["3m", "3mo"] else period

    ticker_obj = yf.Ticker(symbol)
    try:
        df = ticker_obj.history(period=fetch_period)
        if df is None or df.empty:
            df = ticker_obj.history(period="3mo")
    except Exception:
        df = ticker_obj.history(period="3mo")

    if df is None or df.empty:
        raise ValueError(f"No historical price data returned for symbol '{symbol}'.")

    # Clean index timezone
    df.index = pd.to_datetime(df.index)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    # Preserve raw local prices
    df['Close_Local'] = df['Close']
    df['Open_Local'] = df['Open']
    df['High_Local'] = df['High']
    df['Low_Local'] = df['Low']

    # -------------------------------------------------------------
    # CURRENCY CONVERSION / HEDGING ENGINE
    # -------------------------------------------------------------
    # For HDFCBANK & HCLTECH: target is INR -> multiplier = 1.0 (Stay in pure INR)
    # For Shopify: target is CAD -> multiplier = 1.0 (Native CAD)
    # For Berkshire Hathaway, AAPL, United Healthcare: USD -> CAD Hedged via USDCAD=X
    if is_cad_hedged and base_curr == "USD" and target_curr == "CAD":
        fx_multiplier = get_usdcad_fx_rate()
    else:
        fx_multiplier = 1.0

    price_cols = ['Open', 'High', 'Low', 'Close']
    for col in price_cols:
        df[col] = df[f'{col}_Local'] * fx_multiplier

    # -------------------------------------------------------------
    # BASE QUANTITATIVE DATA LOGIC (Strictly conforming to user spec)
    # Calculated on the display Close series (in INR for Indian stocks, CAD for Canadian/US stocks)
    # -------------------------------------------------------------
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal_Line']

    # -------------------------------------------------------------
    # RSI (14-Period) Indicator (Wilder's Standard Smoothing)
    # -------------------------------------------------------------
    delta = df['Close'].diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)

    avg_gain = gain.ewm(com=13, adjust=False).mean()
    avg_loss = loss.ewm(com=13, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df['RSI'] = 100.0 - (100.0 / (1.0 + rs))
    df['RSI'] = df['RSI'].fillna(50.0)

    # Institutional moving averages
    df['SMA50'] = df['Close'].rolling(window=min(50, len(df)), min_periods=1).mean()
    df['Vol_MA20'] = df['Volume'].rolling(window=min(20, len(df)), min_periods=1).mean()

    meta = {
        "asset_key": asset_key,
        "symbol": symbol,
        "name": company,
        "display_name": display_name,
        "base_currency": base_curr,
        "target_currency": target_curr,
        "currency_symbol": curr_sym,
        "fx_multiplier": fx_multiplier,
        "is_cad_hedged": is_cad_hedged,
        "exchange": exchange,
        "hedged_label": hedged_label,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return df, meta


def analyze_quant_signals(df: pd.DataFrame, asset_key: str, meta: dict = None) -> dict:
    """
    Performs comprehensive quantitative signal extraction, crossover detection,
    and momentum evaluation in the asset's active reporting currency.
    """
    if len(df) < 5:
        return {"status": "INSUFFICIENT_DATA"}

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    curr_price = float(latest['Close'])
    prev_price = float(prev['Close'])
    change_abs = curr_price - prev_price
    change_pct = (change_abs / prev_price) * 100.0

    curr_price_local = float(latest['Close_Local'])
    prev_price_local = float(prev['Close_Local'])
    change_abs_local = curr_price_local - prev_price_local

    # 1. MACD Crossover Detection
    macd_curr = float(latest['MACD'])
    signal_curr = float(latest['Signal_Line'])
    hist_curr = float(latest['Histogram'])
    hist_prev = float(prev['Histogram'])

    crossover_event = "NO_RECENT_CROSSOVER"
    crossover_lookback_bars = None

    for i in range(1, min(15, len(df))):
        idx_now = -i
        idx_before = -(i + 1)
        m_now = df['MACD'].iloc[idx_now]
        s_now = df['Signal_Line'].iloc[idx_now]
        m_prev = df['MACD'].iloc[idx_before]
        s_prev = df['Signal_Line'].iloc[idx_before]

        if m_prev <= s_prev and m_now > s_now:
            crossover_event = "BULLISH_CROSSOVER"
            crossover_lookback_bars = i - 1
            break
        elif m_prev >= s_prev and m_now < s_now:
            crossover_event = "BEARISH_CROSSOVER"
            crossover_lookback_bars = i - 1
            break

    macd_state = "BULLISH" if macd_curr >= signal_curr else "BEARISH"
    zero_line_state = "ABOVE_ZERO" if macd_curr >= 0 else "BELOW_ZERO"
    hist_momentum = "EXPANDING_POSITIVE" if hist_curr > 0 and hist_curr >= hist_prev else (
        "CONTRACTING_POSITIVE" if hist_curr > 0 and hist_curr < hist_prev else (
            "EXPANDING_NEGATIVE" if hist_curr < 0 and hist_curr <= hist_prev else "CONTRACTING_NEGATIVE"
        )
    )

    # 2. RSI Evaluation
    rsi_curr = float(latest['RSI'])
    if rsi_curr >= 70:
        rsi_zone = "OVERBOUGHT (Exhaustion Warning)"
        rsi_badge_color = "#FF453A"
    elif rsi_curr <= 30:
        rsi_zone = "OVERSOLD (Rebound Opportunity)"
        rsi_badge_color = "#30D158"
    elif rsi_curr >= 50:
        rsi_zone = "BULLISH EXPANSION CORRIDOR (50-70)"
        rsi_badge_color = "#00F5A0"
    else:
        rsi_zone = "BEARISH DRIFT CORRIDOR (30-50)"
        rsi_badge_color = "#FF9F0A"

    # 3. Moving Average Alignment
    ema12_curr = float(latest['EMA12'])
    ema26_curr = float(latest['EMA26'])
    if curr_price > ema12_curr and ema12_curr > ema26_curr:
        trend_regime = "STRONG BULLISH ALIGNMENT (Price > EMA12 > EMA26)"
        trend_bias = "BULLISH"
    elif curr_price < ema12_curr and ema12_curr < ema26_curr:
        trend_regime = "STRONG BEARISH ALIGNMENT (Price < EMA12 < EMA26)"
        trend_bias = "BEARISH"
    elif curr_price > ema26_curr:
        trend_regime = "MODERATE BULLISH RECOVERY (Above 26-EMA)"
        trend_bias = "LEAN_BULLISH"
    else:
        trend_regime = "CHOPPY / CONSOLIDATION PHASE"
        trend_bias = "NEUTRAL"

    # 4. Volume Confirmation
    vol_curr = float(latest['Volume'])
    vol_ma = float(latest['Vol_MA20'])
    vol_ratio = (vol_curr / vol_ma) if vol_ma > 0 else 1.0
    vol_confirmation = "HIGH VOLUME SURGE" if vol_ratio >= 1.25 else (
        "BELOW AVERAGE VOLUME" if vol_ratio <= 0.75 else "NORMAL INSTITUTIONAL VOLUME"
    )

    # 5. Key Price Levels
    period_high = float(df['High'].max())
    period_low = float(df['Low'].min())
    recent_swing_high = float(df['High'].tail(15).max())
    recent_swing_low = float(df['Low'].tail(15).min())

    # Composite Quant Scoring (0 - 100)
    score = 50
    if macd_state == "BULLISH": score += 15
    if zero_line_state == "ABOVE_ZERO": score += 10
    if "POSITIVE" in hist_momentum: score += 10
    if curr_price > ema12_curr: score += 10
    if curr_price > ema26_curr: score += 10
    if 45 <= rsi_curr <= 65: score += 10
    elif rsi_curr > 75: score -= 15
    elif rsi_curr < 30: score += 5
    if vol_ratio >= 1.2: score += (5 if trend_bias in ["BULLISH", "LEAN_BULLISH"] else -5)

    score = max(5, min(95, score))

    curr_sym = meta.get("currency_symbol", "$") if meta else "$"
    target_curr = meta.get("target_currency", "USD") if meta else "USD"

    if score >= 75:
        verdict = "STRONG BUY / AGGRESSIVE ACCUMULATION"
        action_color = "#00F5A0"
        recommended_action = f"Maintain long positioning in {target_curr} with trailing stop below EMA26."
    elif score >= 60:
        verdict = "MODERATE BUY / ACCUMULATE ON PULLBACKS"
        action_color = "#22C55E"
        recommended_action = f"Scale into position near EMA12 dynamic support ({curr_sym}{ema12_curr:,.2f})."
    elif score >= 45:
        verdict = "NEUTRAL / HOLD & CONSOLIDATE"
        action_color = "#EAB308"
        recommended_action = "Maintain position; observe support consolidation before adding capital."
    elif score >= 30:
        verdict = "MODERATE SELL / DEFENSIVE DE-RISK"
        action_color = "#F97316"
        recommended_action = "Tighten stop-loss boundaries; de-risk exposure on counter-trend rallies."
    else:
        verdict = "STRONG SELL / CAPITAL PRESERVATION"
        action_color = "#EF4444"
        recommended_action = "Protect capital; downside trend structure intact across key moving averages."

    return {
        "asset_key": asset_key,
        "curr_price": curr_price,
        "prev_price": prev_price,
        "change_abs": change_abs,
        "change_pct": change_pct,
        "curr_price_local": curr_price_local,
        "change_abs_local": change_abs_local,
        "target_currency": target_curr,
        "currency_symbol": curr_sym,
        "ema12": ema12_curr,
        "ema26": ema26_curr,
        "macd": macd_curr,
        "signal": signal_curr,
        "histogram": hist_curr,
        "hist_momentum": hist_momentum,
        "macd_state": macd_state,
        "zero_line_state": zero_line_state,
        "crossover_event": crossover_event,
        "crossover_lookback_bars": crossover_lookback_bars,
        "rsi": rsi_curr,
        "rsi_zone": rsi_zone,
        "rsi_badge_color": rsi_badge_color,
        "trend_regime": trend_regime,
        "trend_bias": trend_bias,
        "vol_ratio": vol_ratio,
        "vol_confirmation": vol_confirmation,
        "period_high": period_high,
        "period_low": period_low,
        "recent_swing_high": recent_swing_high,
        "recent_swing_low": recent_swing_low,
        "quant_score": score,
        "verdict": verdict,
        "action_color": action_color,
        "recommended_action": recommended_action,
        "last_bar_date": df.index[-1].strftime("%Y-%m-%d"),
    }
