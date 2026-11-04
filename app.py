"""
AlphaQuant Intelligence Terminal | Minimalist Light-Mode Quantitative Dashboard
Configured for:
- India Equities (HDFCBANK, HCLTECH, TITAN) -> Displayed in Native INR (₹)
- Forex Exchange Pair (CAD to INR) -> Displayed in Native INR (₹ per 1 CAD)
- Canada Equities (Shopify) -> Displayed in Native CAD ($)
- US Equities (Berkshire Hathaway, AAPL, United Healthcare) -> Displayed in CAD Hedged ($)
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from quant_engine import (
    TRACKED_STOCKS,
    fetch_stock_data,
    get_all_overview_tiles,
    analyze_quant_signals,
    get_usdcad_fx_rate
)
from charts import create_financial_dashboard_figure
from agent_summary import render_vertex_agent_markdown


# =============================================================================
# STREAMLIT PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="AlphaQuant | Market Overview & Quantitative Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =============================================================================
# HIGH-END MINIMALIST LIGHT MODE CSS (WHITE BACKGROUND & THIN TYPOGRAPHY)
# =============================================================================
st.markdown("""
<style>
    /* Google Fonts: Inter with light weights (200, 300, 400, 500) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600&display=swap');

    /* Global Background and Typography */
    html, body, [class*="css"], .stApp {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1400px;
    }

    /* Thinner Headings */
    h1, h2, h3, h4 {
        font-family: 'Inter', -apple-system, sans-serif !important;
        font-weight: 300 !important;
        letter-spacing: -0.025em !important;
        color: #0F172A !important;
    }

    p, span, label {
        font-weight: 300 !important;
    }

    /* Sleek Light Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #FFFFFF;
    }
    ::-webkit-scrollbar-thumb {
        background: #E2E8F0;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #CBD5E1;
    }

    /* Header Bar */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 1.2rem;
        margin-bottom: 1.8rem;
    }

    .brand-title {
        font-size: 1.75rem;
        font-weight: 300;
        letter-spacing: -0.03em;
        color: #0F172A;
        line-height: 1.2;
    }

    .brand-title strong {
        font-weight: 500;
        color: #0F172A;
    }

    .brand-subtitle {
        font-size: 0.85rem;
        font-weight: 300;
        color: #64748B;
        margin-top: 0.25rem;
    }

    .header-badge {
        font-size: 0.72rem;
        font-weight: 400;
        padding: 4px 10px;
        border-radius: 20px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        color: #64748B;
        letter-spacing: 0.02em;
    }

    /* Overview Tiles Grid */
    .tiles-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px;
        margin-bottom: 2.5rem;
    }

    .stock-tile {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .stock-tile:hover {
        border-color: #CBD5E1;
        box-shadow: 0 6px 16px -2px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }

    .tile-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 10px;
    }

    .tile-ticker {
        font-size: 1.05rem;
        font-weight: 500;
        color: #0F172A;
        letter-spacing: -0.01em;
    }

    .tile-name {
        font-size: 0.78rem;
        font-weight: 300;
        color: #64748B;
        margin-top: 1px;
    }

    .currency-pill {
        font-size: 0.68rem;
        font-weight: 400;
        padding: 3px 8px;
        border-radius: 6px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        color: #475569;
        white-space: nowrap;
    }

    .tile-price {
        font-size: 1.85rem;
        font-weight: 300;
        letter-spacing: -0.025em;
        color: #0F172A;
        margin: 6px 0 10px 0;
        font-variant-numeric: tabular-nums;
    }

    .tile-price-currency {
        font-size: 0.85rem;
        font-weight: 300;
        color: #64748B;
        margin-left: 3px;
    }

    .change-badge-up {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.78rem;
        font-weight: 400;
        color: #059669;
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        padding: 3px 9px;
        border-radius: 6px;
    }

    .change-badge-down {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.78rem;
        font-weight: 400;
        color: #E11D48;
        background: #FFF1F2;
        border: 1px solid #FECDD3;
        padding: 3px 9px;
        border-radius: 6px;
    }

    .range-bar-container {
        margin-top: 14px;
        padding-top: 10px;
        border-top: 1px solid #F1F5F9;
    }

    .range-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.7rem;
        font-weight: 300;
        color: #94A3B8;
        margin-bottom: 4px;
    }

    .range-track {
        height: 3px;
        background: #F1F5F9;
        border-radius: 2px;
        position: relative;
        overflow: hidden;
    }

    .range-fill {
        height: 100%;
        background: #CBD5E1;
        border-radius: 2px;
    }

    /* Section Divider and Headers */
    .section-header {
        margin-top: 1.5rem;
        margin-bottom: 1.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid #F1F5F9;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 300;
        color: #0F172A;
        letter-spacing: -0.02em;
    }

    .section-subtitle {
        font-size: 0.82rem;
        font-weight: 300;
        color: #64748B;
        margin-top: 0.2rem;
    }

    /* Detail Stat Card */
    .stat-pill {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 16px;
        text-align: left;
    }

    .stat-pill-label {
        font-size: 0.7rem;
        font-weight: 400;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 3px;
    }

    .stat-pill-value {
        font-size: 1.15rem;
        font-weight: 400;
        color: #0F172A;
        letter-spacing: -0.01em;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0;
    }

    /* Buttons */
    .stButton button {
        background: #0F172A !important;
        color: #FFFFFF !important;
        border: 1px solid #0F172A !important;
        border-radius: 8px !important;
        font-weight: 400 !important;
        letter-spacing: 0.01em !important;
        transition: all 0.2s ease !important;
        padding: 0.5rem 1.2rem !important;
    }

    .stButton button:hover {
        background: #334155 !important;
        border-color: #334155 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08) !important;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# DATA FETCHING WITH CACHING (FAST LIGHTWEIGHT LOADING)
# =============================================================================
@st.cache_data(ttl=180, show_spinner=False)
def load_all_overview_tiles():
    """Fetches high-speed overview prices and daily changes for all 8 assets."""
    return get_all_overview_tiles(period="3mo")


@st.cache_data(ttl=180, show_spinner=False)
def load_single_asset_data(asset_key: str, period: str):
    """Fetches full historical bars and computes indicators for deep charting."""
    return fetch_stock_data(asset_key, period=period)


# =============================================================================
# TOP HEADER BAR
# =============================================================================
now_str = datetime.now().strftime("%B %d, %Y • %H:%M:%S")

st.markdown(f"""
<div class="header-container">
    <div>
        <div class="brand-title"><strong>AlphaQuant</strong> Intelligence</div>
        <div class="brand-subtitle">Live multi-currency monitoring across India, Canada, United States & Foreign Exchange</div>
    </div>
    <div>
        <span class="header-badge">● Live Synced • {now_str}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# 1. LANDING PAGE: ALL PRICES & CHANGES ARRANGED IN TILES ONLY
# (RSI and other indicators are strictly excluded here and pushed down below)
# =============================================================================
with st.spinner("Streaming live quotes..."):
    tiles = load_all_overview_tiles()

tiles_html = '<div class="tiles-grid">'

for tile in tiles:
    sym = tile["currency_symbol"]
    t_curr = tile["target_currency"]
    price_val = tile["curr_price"]
    chg_abs = tile["change_abs"]
    chg_pct = tile["change_pct"]
    p_hi = tile["period_high"]
    p_lo = tile["period_low"]

    # Price formatting
    if tile["is_forex"]:
        price_str = f"{sym}{price_val:.4f}"
        diff_str = f"{chg_abs:+.4f}"
    else:
        price_str = f"{sym}{price_val:,.2f}"
        diff_str = f"{chg_abs:+,.2f}"

    # Change badge styling
    if chg_abs >= 0:
        badge_html = f'<span class="change-badge-up">▲ {diff_str} (+{chg_pct:.2f}%)</span>'
    else:
        badge_html = f'<span class="change-badge-down">▼ {diff_str} ({chg_pct:.2f}%)</span>'

    # Range progress bar
    if p_hi > p_lo and p_lo > 0:
        pct_pos = max(0.0, min(100.0, ((price_val - p_lo) / (p_hi - p_lo)) * 100.0))
    else:
        pct_pos = 50.0

    tile_card = f"""
    <div class="stock-tile">
        <div>
            <div class="tile-top">
                <div>
                    <div class="tile-ticker">{tile['flag']} {tile['short_name']}</div>
                    <div class="tile-name">{tile['company']}</div>
                </div>
                <div class="currency-pill">{tile['hedged_label']}</div>
            </div>
            <div class="tile-price">
                {price_str}<span class="tile-price-currency">{t_curr}</span>
            </div>
            <div>
                {badge_html}
            </div>
        </div>
        <div class="range-bar-container">
            <div class="range-labels">
                <span>3M Low: {sym}{p_lo:,.2f}</span>
                <span>3M High: {sym}{p_hi:,.2f}</span>
            </div>
            <div class="range-track">
                <div class="range-fill" style="width: {pct_pos:.1f}%;"></div>
            </div>
        </div>
    </div>
    """
    tiles_html += tile_card

tiles_html += '</div>'
st.markdown(tiles_html, unsafe_allow_html=True)


# =============================================================================
# 2. PUSHED DOWN SECTION: DEEP TECHNICALS, RSI, MACD & AGENT DOSSIER
# =============================================================================
st.markdown("""
<div class="section-header">
    <div class="section-title">Deep Technical Analysis & Charts</div>
    <div class="section-subtitle">Select an asset below to reveal Candlesticks, 12/26 Exponential Moving Averages, RSI (14), MACD Momentum, and AI Agentic Synthesis.</div>
</div>
""", unsafe_allow_html=True)

# Asset and Timeframe Selectors
col_select, col_period, col_btn = st.columns([2.5, 1.2, 1.3])

with col_select:
    stock_options = list(TRACKED_STOCKS.keys())
    selected_asset = st.selectbox(
        "Select Asset for Deep Technical Inspection:",
        stock_options,
        index=0,
        format_func=lambda x: f"{TRACKED_STOCKS[x]['flag']} {TRACKED_STOCKS[x]['display_name']} [{TRACKED_STOCKS[x]['hedged_label']}]",
        label_visibility="collapsed"
    )

with col_period:
    selected_period = st.selectbox(
        "Lookback Period:",
        ["1mo", "3mo", "6mo", "1y"],
        index=1,
        label_visibility="collapsed"
    )

with col_btn:
    run_analysis = st.button("🚀 Run Agentic Analysis", use_container_width=True)

# Fetch detailed data for selected asset
try:
    df, meta = load_single_asset_data(selected_asset, period=selected_period)
    signals = analyze_quant_signals(df, selected_asset, meta)

    # Secondary Mini Telemetry Ribbon for the selected asset
    curr_sym = meta["currency_symbol"]
    target_curr = meta["target_currency"]
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    
    with m_col1:
        st.markdown(f"""
        <div class="stat-pill">
            <div class="stat-pill-label">Selected Price</div>
            <div class="stat-pill-value">{curr_sym}{signals['curr_price']:,.2f} <span style="font-size: 0.75rem; color: #64748B;">{target_curr}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col2:
        st.markdown(f"""
        <div class="stat-pill">
            <div class="stat-pill-label">Fast EMA (12)</div>
            <div class="stat-pill-value">{curr_sym}{signals['ema12']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col3:
        st.markdown(f"""
        <div class="stat-pill">
            <div class="stat-pill-label">Slow EMA (26)</div>
            <div class="stat-pill-value">{curr_sym}{signals['ema26']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col4:
        st.markdown(f"""
        <div class="stat-pill">
            <div class="stat-pill-label">RSI (14-Period)</div>
            <div class="stat-pill-value" style="color: {signals['rsi_badge_color']};">{signals['rsi']:.1f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col5:
        st.markdown(f"""
        <div class="stat-pill">
            <div class="stat-pill-label">MACD Momentum</div>
            <div class="stat-pill-value">{curr_sym}{signals['macd']:+.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Render Unified 3-Panel Vertical Plotly Chart (Light Mode)
    fig = create_financial_dashboard_figure(df, selected_asset, meta)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Render Vertex AI Agentic Analysis
    if run_analysis:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        with st.spinner("Synthesizing quantitative telemetry with Vertex AI Agent..."):
            dossier_markdown = render_vertex_agent_markdown(signals, meta)
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; margin-top: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                {dossier_markdown}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💡 Tap **'🚀 Run Agentic Analysis'** above to generate the full institutional research dossier and crossover telemetry for this asset.")

except Exception as e:
    st.error(f"Error analyzing {selected_asset}: {str(e)}")


# =============================================================================
# SIDEBAR (CLEAN, MINIMALIST INFO)
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 16px;">
        <div style="font-size: 1.15rem; font-weight: 500; color: #0F172A;">AlphaQuant</div>
        <div style="font-size: 0.75rem; font-weight: 300; color: #64748B;">Multi-Currency Portfolio Terminal</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Portfolio Currency Framework:**
    - 🇮🇳 **India (NSE)**: `HDFCBANK`, `HCLTECH`, `TITAN` in native **₹ INR**.
    - 💱 **Foreign Exchange**: `CAD to INR` (1 CAD in **₹ INR**).
    - 🇨🇦 **Canada (TSX)**: `Shopify` in native **$ CAD**.
    - 🇺🇸 **USA (NYSE/NASDAQ)**: `BRK-B`, `AAPL`, `UNH` in **$ CAD Hedged** via `USDCAD=X`.
    """)

    st.markdown("---")
    st.markdown("""
    **Quantitative Formulas Active:**
    - `EMA12` = 12-period Exponential MA
    - `EMA26` = 26-period Exponential MA
    - `MACD` = `EMA12` - `EMA26`
    - `Signal Line` = 9-period EMA of MACD
    - `Histogram` = `MACD` - `Signal Line`
    - `RSI` = 14-period Wilder Smoothed
    """)

    if st.button("🔄 Clear Cache & Refresh Data"):
        st.cache_data.clear()
        st.rerun()
