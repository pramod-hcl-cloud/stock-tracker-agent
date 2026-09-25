"""
Vertex AI Quantitative Agent Research Summary Generator
Formulates structured markdown intelligence reports grounded in exact technical calculations
with asset-specific currency formatting (INR for India, CAD for Canada/US).
"""


def render_vertex_agent_markdown(signals: dict, meta: dict) -> str:
    """
    Produces an institutional-grade quantitative research memorandum
    detailing active crossovers, oscillator telemetry, and risk parameters in the asset's active currency.
    """
    asset_key = signals['asset_key']
    name = meta.get('name', asset_key)
    symbol = meta.get('symbol', asset_key)
    exchange = meta.get('exchange', 'Global')
    base_curr = meta.get('base_currency', 'USD')
    target_curr = meta.get('target_currency', 'CAD')
    curr_sym = meta.get('currency_symbol', '$')
    hedged_label = meta.get('hedged_label', '')
    is_cad_hedged = meta.get('is_cad_hedged', False)
    fx_multiplier = meta.get('fx_multiplier', 1.0)

    price = signals['curr_price']
    chg_abs = signals['change_abs']
    chg_pct = signals['change_pct']
    sign = "+" if chg_abs >= 0 else ""

    # Crossover description
    crossover = signals['crossover_event']
    bars_ago = signals['crossover_lookback_bars']
    if crossover == "BULLISH_CROSSOVER":
        if bars_ago == 0:
            crossover_desc = f"⚡ **FRESH BULLISH CROSSOVER TODAY**: MACD line crossed above Signal line during the current session in {target_curr} valuation."
        else:
            crossover_desc = f"📈 **ACTIVE BULLISH CROSSOVER**: MACD crossed above Signal line **{bars_ago} session(s) ago**, maintaining positive upward momentum trajectory."
    elif crossover == "BEARISH_CROSSOVER":
        if bars_ago == 0:
            crossover_desc = f"⚠️ **FRESH BEARISH CROSSOVER TODAY**: MACD line sliced below Signal line during the current session."
        else:
            crossover_desc = f"📉 **ACTIVE BEARISH CROSSOVER**: MACD crossed below Signal line **{bars_ago} session(s) ago**, asserting downside pressure."
    else:
        state = "Bullish" if signals['macd_state'] == "BULLISH" else "Bearish"
        crossover_desc = f"⚖️ **STEADY STATE ({state.upper()})**: No crossover triggered within the last 15 trading sessions; established momentum regime persists."

    # Histogram narrative
    hist_val = signals['histogram']
    hist_mom = signals['hist_momentum']
    if hist_mom == "EXPANDING_POSITIVE":
        hist_analysis = f"Positive histogram expanding at `{curr_sym}{hist_val:+.3f} {target_curr}`. Buyers exhibit accelerating momentum dominance."
    elif hist_mom == "CONTRACTING_POSITIVE":
        hist_analysis = f"Positive histogram contracting at `{curr_sym}{hist_val:+.3f} {target_curr}`. Upside momentum is decelerating; watch for potential exhaustion."
    elif hist_mom == "EXPANDING_NEGATIVE":
        hist_analysis = f"Negative histogram widening at `{curr_sym}{hist_val:+.3f} {target_curr}`. Selling pressure is intensifying toward lower technical support."
    else:
        hist_analysis = f"Negative histogram contracting at `{curr_sym}{hist_val:+.3f} {target_curr}`. Downside momentum is waning; early base formation indicated."

    # RSI narrative
    rsi = signals['rsi']
    if rsi >= 70:
        rsi_commentary = f"RSI sits at **{rsi:.1f}** in the **Overbought territory**. Statistically vulnerable to mean-reversion pullbacks before further extension."
    elif rsi <= 30:
        rsi_commentary = f"RSI registers at **{rsi:.1f}** in the **Oversold zone**. Capitulation signals present; potential risk-reward asymmetry favors value accumulation."
    elif rsi >= 50:
        rsi_commentary = f"RSI stands at **{rsi:.1f}** within the **Bullish Momentum Corridor (50–70)**. Constructive expansion with ample headroom before hitting overbought friction."
    else:
        rsi_commentary = f"RSI registers at **{rsi:.1f}** within the **Bearish Drift Corridor (30–50)**. Subdued relative demand, indicating consolidation or sluggish recovery."

    # Price vs EMA narrative
    ema12 = signals['ema12']
    ema26 = signals['ema26']
    if price > ema12 and ema12 > ema26:
        ma_analysis = f"**Bullish Stacking Structure**: Price ({curr_sym}{price:,.2f}) > 12-day EMA ({curr_sym}{ema12:,.2f}) > 26-day EMA ({curr_sym}{ema26:,.2f}). Both short-term and medium-term moving average slopes are upward-sloping."
    elif price < ema12 and ema12 < ema26:
        ma_analysis = f"**Bearish Stacking Structure**: Price ({curr_sym}{price:,.2f}) < 12-day EMA ({curr_sym}{ema12:,.2f}) < 26-day EMA ({curr_sym}{ema26:,.2f}). Negative trend alignment with moving averages acting as overhead dynamic resistance."
    elif price > ema26:
        ma_analysis = f"**Mixed / Bullish Bias**: Price is trading above the 26-day EMA ({curr_sym}{ema26:,.2f}), but testing the short-term 12-day EMA ({curr_sym}{ema12:,.2f})."
    else:
        ma_analysis = f"**Consolidation / Below Median**: Price ({curr_sym}{price:,.2f}) has slipped beneath the 26-day EMA ({curr_sym}{ema26:,.2f}). Caution warranted until reclaiming short-term moving average."

    # Volume profile narrative
    vol_ratio = signals['vol_ratio']
    vol_confirmation = signals['vol_confirmation']
    vol_commentary = f"Current trading volume is tracking at **{vol_ratio * 100:.1f}%** of the 20-day average volume ({vol_confirmation})."

    # Support / Resistance / Risk metrics
    sup = signals['recent_swing_low']
    res = signals['recent_swing_high']
    inval_stop = sup * 0.985 if signals['trend_bias'] in ["BULLISH", "LEAN_BULLISH"] else res * 1.015
    target_1 = res * 1.025 if signals['trend_bias'] in ["BULLISH", "LEAN_BULLISH"] else sup * 0.975

    # Currency architecture disclosure
    if target_curr == "INR":
        curr_section = f"🇮🇳 **Native Indian Rupee Listing**: Quoted and analyzed directly in native **Indian Rupees (`₹ INR`)** on the **National Stock Exchange of India (`NSE`)**."
    elif is_cad_hedged:
        price_local = signals.get('curr_price_local', price / fx_multiplier)
        curr_section = (
            f"🇨🇦 **USD to CAD Hedged Architecture**: Originally listed in **`USD`** on `{exchange}` (`${price_local:,.2f} USD`). "
            f"Scaled to **`CAD`** using the active USD/CAD rate (`1 USD = ${fx_multiplier:.4f} CAD`) to isolate equity alpha while neutralizing FX currency drag."
        )
    else:
        curr_section = f"🇨🇦 **Domestic Canadian Equity**: Quoted and analyzed directly in native **Canadian Dollars (`$ CAD`)** on the **Toronto Stock Exchange (`TSX`)**."

    markdown_report = f"""
### 📋 Quantitative Executive Dossier: {name} ({hedged_label})
**Exchange & Identifier**: `{symbol}` on `{exchange}` | **Reporting Currency**: `{curr_sym} {target_curr}`  
**Analysis Timestamp**: `{signals['last_bar_date']}` | **Model**: `Vertex AI Quant Agent (Gemini 1.5 Pro Architecture)`

---

#### 🌐 Market & Currency Framework
> {curr_section}

---

#### 🎯 Strategic Quant Verdict
> **Action Recommendation**: <span style="font-size: 1.15em; font-weight: 700; color: {signals['action_color']};">{signals['verdict']}</span>  
> **Confidence Rating**: `{signals['quant_score']}% Composite Model Probability`  
> **Tactical Guidance**: {signals['recommended_action']}

---

#### 📊 Multi-Indicator Crossover & Signal Telemetry

1. **MACD (12, 26, 9) Dynamics & Zero-Line Regime**:
   - {crossover_desc}
   - **MACD Value**: `{curr_sym}{signals['macd']:+.3f}` | **Signal Line**: `{curr_sym}{signals['signal']:+.3f}` | **Zero-Line Stance**: `{'Above Zero (Expansion)' if signals['zero_line_state'] == 'ABOVE_ZERO' else 'Below Zero (Contraction)'}`
   - **Histogram Momentum**: {hist_analysis}

2. **RSI (14-Period) Oscillator State**:
   - **Current Value**: `{rsi:.2f}` ({signals['rsi_zone']})
   - {rsi_commentary}

3. **Trend Structure & Moving Average Stack**:
   - {ma_analysis}
   - **Short-Term Trend Gauge**: `{signals['trend_bias']}`

4. **Institutional Volume Confirmation**:
   - {vol_commentary}

---

#### 🛡️ Quantitative Risk Boundaries & Key Price Levels ({curr_sym} {target_curr})

| Technical Boundary Marker | Price Level ({target_curr}) | Quantitative Rationale |
| :--- | :--- | :--- |
| **Current Market Price** | **{curr_sym}{price:,.2f} {target_curr}** | Change: `{sign}{curr_sym}{chg_abs:.2f} ({sign}{chg_pct:.2f}%)` |
| **Dynamic Support (EMA 12 / 26)** | **{curr_sym}{ema12:,.2f} / {curr_sym}{ema26:,.2f}** | Primary dynamic moving average support band |
| **Tactical Swing Support** | **{curr_sym}{sup:,.2f} {target_curr}** | 15-day local structural swing floor |
| **Overhead Swing Resistance** | **{curr_sym}{res:,.2f} {target_curr}** | 15-day local structural swing ceiling |
| **Model Invalidation Stop** | **{curr_sym}{inval_stop:,.2f} {target_curr}** | Invalidation threshold for current momentum thesis |
| **Tactical Extension Target** | **{curr_sym}{target_1:,.2f} {target_curr}** | Volatility/ATR expansion target |

---

*Notice: This agentic research briefing is generated algorithmically using mathematical EMA, MACD, and RSI formulations. Always corroborate algorithmic model output with individual risk tolerance and macroeconomic catalyst calendars.*
"""
    return markdown_report
