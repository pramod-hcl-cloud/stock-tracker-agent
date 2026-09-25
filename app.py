"""
AlphaQuant Intelligence Terminal | Sleek Dark-Mode Quantitative Dashboard
Multi-Currency Portfolio:
- India (NSE): HDFCBANK, HCLTECH in Native INR (₹)
- Canada (TSX): Shopify in Native CAD ($)
- USA (NYSE/NASDAQ): Berkshire Hathaway, AAPL, United Healthcare in CAD Hedged ($)
Powered by Streamlit, Plotly, and yfinance with Vertex AI Agentic Synthesis.
"""

import streamlit as st
import pandas as pd
from quant_engine import TRACKED_STOCKS, fetch_stock_data, analyze_quant_signals
from charts import create_financial_dashboard_figure
from agent_summary import render_vertex_agent_markdown


# Configure Streamlit Page
st.set_page_config(
    page_title="AlphaQuant | Multi-Currency Intelligence Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Quantitative Dark Mode CSS
st.markdown("""
<style>
    /* Global Background and Typography */
    .stApp {
        background-color: #0A0E17;
        color: #E2E8F0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sleek Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0A0E17;
    }
    ::-webkit-scrollbar-thumb {
        background: #1E293B;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0E131F !important;
        border-right: 1px solid #1E293B;
    }
    
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 0 16px 0;
        border-bottom: 1px solid #1E293B;
        margin-bottom: 20px;
    }
    
    .brand-title {
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #00F5A0 0%, #00D2FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .brand-tag {
        font-size: 0.65rem;
        background: rgba(0, 245, 160, 0.12);
        color: #00F5A0;
        padding: 2px 7px;
        border-radius: 4px;
        border: 1px solid rgba(0, 245, 160, 0.25);
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .currency-regime-card {
        background: #131A29;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 16px;
        font-size: 0.74rem;
        color: #94A3B8;
        line-height: 1.45;
    }

    /* Top KPI Cards */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 14px;
        margin-bottom: 18px;
    }

    .kpi-card {
        background: linear-gradient(145deg, #111726 0%, #0D121D 100%);
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 14px 18px;
        transition: transform 0.15s ease, border-color 0.15s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
    }
    
    .kpi-card:hover {
        border-color: #334155;
        transform: translateY(-1px);
    }

    .kpi-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        color: #94A3B8;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .currency-pill {
        background: rgba(0, 245, 160, 0.12);
        color: #00F5A0;
        border: 1px solid rgba(0, 245, 160, 0.25);
        font-size: 0.62rem;
        padding: 1px 6px;
        border-radius: 4px;
        font-weight: 700;
    }

    .currency-pill-inr {
        background: rgba(249, 115, 22, 0.12);
        color: #FB923C;
        border: 1px solid rgba(249, 115, 22, 0.25);
        font-size: 0.62rem;
        padding: 1px 6px;
        border-radius: 4px;
        font-weight: 700;
    }

    .kpi-value {
        font-size: 1.45rem;
        font-weight: 800;
        color: #F8FAFC;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.02em;
    }

    .kpi-sub {
        font-size: 0.78rem;
        font-weight: 600;
        margin-top: 4px;
    }

    .sub-green {
        color: #00F5A0;
    }
    
    .sub-red {
        color: #FF3B30;
    }

    .sub-neutral {
        color: #94A3B8;
    }

    /* Vertex AI Simulation Container */
    .vertex-container {
        background: linear-gradient(180deg, #101626 0%, #0B0F1A 100%);
        border: 1px solid #2B384E;
        border-radius: 12px;
        padding: 24px;
        margin-top: 24px;
        position: relative;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
        overflow: hidden;
    }

    .vertex-container::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00F5A0, #00D2FF, #A855F7, #00F5A0);
        background-size: 300% 100%;
        animation: borderGradient 6s linear infinite;
    }

    @keyframes borderGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .vertex-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #1E293B;
    }

    .vertex-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #F1F5F9;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .vertex-badge {
        font-size: 0.72rem;
        background: rgba(0, 210, 255, 0.12);
        color: #00D2FF;
        border: 1px solid rgba(0, 210, 255, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        letter-spacing: 0.04em;
    }

    /* Streamlit Button Override */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #00F5A0 0%, #00B894 100%);
        color: #041014;
        font-weight: 800;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        letter-spacing: 0.02em;
        transition: all 0.2s ease;
        box-shadow: 0 4px 14px rgba(0, 245, 160, 0.35);
        width: 100%;
    }

    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(0, 245, 160, 0.5);
        background: linear-gradient(135deg, #26F7AC 0%, #00C896 100%);
        color: #041014;
    }

    /* Plotly Chart Card Wrapper */
    .chart-wrapper {
        background: #0A0E17;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 10px 10px 0 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SIDEBAR CONTROLS
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div>
            <div class="brand-title">ALPHAQUANT</div>
            <div style="font-size: 0.75rem; color: #64748B;">QUANTITATIVE RESEARCH TERMINAL</div>
        </div>
        <div class="brand-tag">v2.5 PRO</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="currency-regime-card">
        <b>Active Currency Framework:</b><br>
        🇮🇳 <b>India (HDFC, HCLTech)</b>: Native <b>INR (₹)</b><br>
        🇨🇦 <b>Canada (Shopify)</b>: Native <b>CAD ($)</b><br>
        🇺🇸 <b>USA (BRK-B, AAPL, UNH)</b>: <b>CAD Hedged ($)</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 Asset Selection")
    
    stock_keys = list(TRACKED_STOCKS.keys())
    format_func = lambda k: f"{TRACKED_STOCKS[k]['display_name']} [{TRACKED_STOCKS[k]['hedged_label']}]"

    selected_key = st.selectbox(
        "Select Stock to Track",
        options=stock_keys,
        index=0,
        format_func=format_func,
        help="Select any asset: Indian stocks are quoted in INR (₹), Canadian/US stocks in CAD ($)."
    )

    # Optional custom ticker override
    enable_custom = st.checkbox("Custom Symbol Override", value=False)
    if enable_custom:
        custom_input = st.text_input("Enter Yahoo Finance Symbol (e.g. RELIANCE.NS, GOOGL)", value="").strip().upper()
        if custom_input:
            selected_key = custom_input

    st.markdown("---")
    st.markdown("### ⚙️ Timeframe & Parameters")
    
    period_options = {
        "3 Months (Default Spec)": "3mo",
        "1 Month": "1mo",
        "6 Months": "6mo",
        "1 Year": "1y"
    }
    selected_period_label = st.selectbox(
        "Historical Period",
        options=list(period_options.keys()),
        index=0,
        help="Default 3m period loads 3 months of daily trading bars."
    )
    selected_period = period_options[selected_period_label]

    st.caption("• Fast EMA: **12 periods**  \n• Slow EMA: **26 periods**  \n• MACD Signal: **9 periods**  \n• RSI: **14 periods (30/70)**")

    st.markdown("---")
    
    # Primary Agentic Trigger Button
    run_agent = st.button("🚀 Run Agentic Analysis", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.7rem; color: #475569; line-height: 1.4;">
        🟢 <b>Vertex AI Engine</b>: Active & Calibrated<br>
        📡 <b>Cross-Border Feeds</b>: NSE (India), TSX (Canada), NYSE/NASDAQ (USA)<br>
        💱 <b>FX Engine</b>: Live USD/CAD Hedging
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# DATA FETCHING & QUANTITATIVE PROCESSING
# =============================================================================
@st.cache_data(ttl=300, show_spinner=False)
def load_market_data(asset_key: str, period: str):
    return fetch_stock_data(asset_key, period=period)

with st.spinner(f"Ingesting market data for {selected_key}..."):
    try:
        df, meta = load_market_data(selected_key, selected_period)
        signals = analyze_quant_signals(df, selected_key, meta)
    except Exception as e:
        st.error(f"❌ Failed to fetch or process market data for {selected_key}: {str(e)}")
        st.stop()


# =============================================================================
# TOP KPI METRICS RIBBON
# =============================================================================
curr_sym = meta.get('currency_symbol', '$')
target_curr = meta.get('target_currency', 'CAD')
is_inr = target_curr == "INR"
pill_class = "currency-pill-inr" if is_inr else "currency-pill"

p_curr = signals['curr_price']
p_chg = signals['change_abs']
p_pct = signals['change_pct']
chg_sign = "+" if p_chg >= 0 else ""
chg_class = "sub-green" if p_chg >= 0 else "sub-red"

macd_badge = "BULLISH CROSS" if signals['macd_state'] == "BULLISH" else "BEARISH CROSS"
macd_class = "sub-green" if signals['macd_state'] == "BULLISH" else "sub-red"

rsi_val = signals['rsi']
rsi_class = "sub-green" if (45 <= rsi_val <= 68) else ("sub-red" if rsi_val > 70 else "sub-neutral")

if is_inr:
    sub_desc = f"National Stock Exchange of India (NSE)"
elif meta.get('is_cad_hedged', False):
    price_loc = signals.get('curr_price_local', p_curr)
    sub_desc = f"Local: ${price_loc:,.2f} USD (Hedged @ USDCAD {meta.get('fx_multiplier', 1.0):.4f})"
else:
    sub_desc = f"Toronto Stock Exchange (TSX) Native CAD"

st.markdown(f"""
<div class="metric-container">
    <div class="kpi-card">
        <div class="kpi-label">
            <span>{meta['display_name']}</span>
            <span class="{pill_class}">{meta['hedged_label'].upper()}</span>
        </div>
        <div class="kpi-value">{curr_sym}{p_curr:,.2f} <span style="font-size: 0.8rem; color: #94A3B8;">{target_curr}</span></div>
        <div class="kpi-sub {chg_class}">{chg_sign}{curr_sym}{p_chg:.2f} ({chg_sign}{p_pct:.2f}%) Today</div>
        <div style="font-size: 0.68rem; color: #64748B; margin-top: 2px;">{sub_desc}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">
            <span>MACD (12, 26, 9)</span>
            <span class="{pill_class}">{target_curr}</span>
        </div>
        <div class="kpi-value">{curr_sym}{signals['macd']:+.2f}</div>
        <div class="kpi-sub {macd_class}">Signal: {curr_sym}{signals['signal']:+.2f} • {macd_badge}</div>
        <div style="font-size: 0.68rem; color: #64748B; margin-top: 2px;">Hist: {curr_sym}{signals['histogram']:+.3f} {target_curr}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">
            <span>RSI (14-Period)</span>
            <span class="currency-pill">OSCILLATOR</span>
        </div>
        <div class="kpi-value">{rsi_val:.1f}</div>
        <div class="kpi-sub {rsi_class}">{signals['rsi_zone'].split('(')[0].strip()}</div>
        <div style="font-size: 0.68rem; color: #64748B; margin-top: 2px;">30 Oversold / 70 Overbought</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">
            <span>Quantitative Stance</span>
            <span class="currency-pill">AI VERDICT</span>
        </div>
        <div class="kpi-value" style="font-size: 1.15rem; color: {signals['action_color']};">{signals['verdict'].split('/')[0].strip()}</div>
        <div class="kpi-sub sub-neutral">Confidence: {signals['quant_score']}% Composite</div>
        <div style="font-size: 0.68rem; color: #64748B; margin-top: 2px;">{signals['trend_bias']} Regime</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">
            <span>Period Range</span>
            <span class="{pill_class}">{target_curr}</span>
        </div>
        <div class="kpi-value" style="font-size: 1.1rem; color: #CBD5E1;">{curr_sym}{signals['period_low']:,.2f} - {curr_sym}{signals['period_high']:,.2f}</div>
        <div class="kpi-sub sub-neutral">Volume Ratio: {signals['vol_ratio']:.2f}x 20D MA</div>
        <div style="font-size: 0.68rem; color: #64748B; margin-top: 2px;">Exchange: {meta['exchange']}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# THE LAYOUT PANEL: 3 LINKED PLOTLY SUBPLOTS
# =============================================================================
fig = create_financial_dashboard_figure(df, selected_key, meta)

st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": "hover", "scrollZoom": True})
st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# VERTEX AI AGENT RESEARCH SUMMARY BOX
# =============================================================================
markdown_dossier = render_vertex_agent_markdown(signals, meta)

# Render the distinct styled simulation box
st.markdown(f"""
<div class="vertex-container">
    <div class="vertex-header">
        <div class="vertex-title">
            <span>🤖 Vertex AI Agent Research Summary</span>
        </div>
        <div class="vertex-badge">
            {target_curr} QUANT SYNTHESIS ENGINE • ACTIVE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.container():
    # Print the markdown analysis detailing active crossovers and trend behaviors
    st.markdown(markdown_dossier, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 35px; margin-bottom: 20px; font-size: 0.75rem; color: #475569;">
    AlphaQuant Intelligence Dashboard • Multi-Currency Institutional Terminal • Quantitative Trading Division
</div>
""", unsafe_allow_html=True)
