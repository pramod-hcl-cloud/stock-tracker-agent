"""
Automated Verification Suite for Multi-Currency Portfolio
Tests:
1. HDFCBANK (India - NSE) -> Native INR (₹)
2. HCLTECH (India - NSE) -> Native INR (₹)
3. Shopify (Canada - TSX) -> Native CAD ($)
4. Berkshire Hathaway (USA - NYSE) -> CAD Hedged ($)
5. AAPL (USA - NASDAQ) -> CAD Hedged ($)
6. United Healthcare (USA - NYSE) -> CAD Hedged ($)
"""

import sys
from quant_engine import TRACKED_STOCKS, fetch_stock_data, analyze_quant_signals
from charts import create_financial_dashboard_figure
from agent_summary import render_vertex_agent_markdown


def run_tests():
    print("=" * 65)
    print("STARTING MULTI-CURRENCY PORTFOLIO TEST SUITE")
    print("=" * 65)

    for asset_key, cfg in TRACKED_STOCKS.items():
        print(f"\n[Testing Asset: {asset_key} ({cfg['symbol']}) - Currency: {cfg['currency_symbol']} {cfg['target_currency']}]")
        
        # 1. Test data fetch & currency regime
        df, meta = fetch_stock_data(asset_key, period="3m")
        assert not df.empty, f"DataFrame for {asset_key} is empty!"
        assert meta["target_currency"] == cfg["target_currency"], f"Expected {cfg['target_currency']}, got {meta['target_currency']}"
        assert meta["currency_symbol"] == cfg["currency_symbol"], f"Expected {cfg['currency_symbol']}, got {meta['currency_symbol']}"
        
        # Specific currency checks:
        if asset_key in ["HDFCBANK", "HCLTECH"]:
            assert meta["target_currency"] == "INR"
            assert meta["currency_symbol"] == "₹"
            assert df['Close'].iloc[-1] > 300, f"Expected INR price > 300, got {df['Close'].iloc[-1]}"
        elif asset_key == "Shopify":
            assert meta["target_currency"] == "CAD"
            assert meta["currency_symbol"] == "$"
        else:
            assert meta["target_currency"] == "CAD"
            assert meta["is_cad_hedged"] is True
            assert meta["currency_symbol"] == "$"

        # Check required columns from spec
        required_cols = ['Close', 'EMA12', 'EMA26', 'MACD', 'Signal_Line', 'Histogram', 'RSI']
        for col in required_cols:
            assert col in df.columns, f"Missing required column: {col}"
            assert not df[col].isna().all(), f"Column {col} has all NaN values!"
        
        curr_sym = meta["currency_symbol"]
        curr_code = meta["target_currency"]
        print(f"  ✓ Data fetched: {len(df)} bars. Regime: {meta['hedged_label']}")
        print(f"  ✓ Latest Close: {curr_sym}{df['Close'].iloc[-1]:,.2f} {curr_code}")
        print(f"  ✓ Latest EMA12: {curr_sym}{df['EMA12'].iloc[-1]:,.2f} {curr_code}")
        print(f"  ✓ Latest EMA26: {curr_sym}{df['EMA26'].iloc[-1]:,.2f} {curr_code}")
        print(f"  ✓ Latest MACD: {curr_sym}{df['MACD'].iloc[-1]:+.4f} {curr_code}")
        print(f"  ✓ Latest Signal: {curr_sym}{df['Signal_Line'].iloc[-1]:+.4f} {curr_code}")
        print(f"  ✓ Latest Histogram: {curr_sym}{df['Histogram'].iloc[-1]:+.4f} {curr_code}")
        print(f"  ✓ Latest RSI (14): {df['RSI'].iloc[-1]:.2f}")

        # 2. Test quantitative signals & crossover extraction
        signals = analyze_quant_signals(df, asset_key, meta)
        assert "verdict" in signals, "Signals missing verdict!"
        assert "macd_state" in signals, "Signals missing macd_state!"
        print(f"  ✓ Quant Signal: Stance={signals['verdict']}, Score={signals['quant_score']}%, Crossover={signals['crossover_event']}")

        # 3. Test unified Plotly figure generation
        fig = create_financial_dashboard_figure(df, asset_key, meta)
        assert fig is not None, "Figure creation failed!"
        assert len(fig.data) >= 6, f"Expected at least 6 traces in 3 subplots, got {len(fig.data)}"
        print(f"  ✓ Plotly Figure generated successfully with {len(fig.data)} traces across 3 linked subplots.")

        # 4. Test Vertex AI Agent markdown synthesis
        report = render_vertex_agent_markdown(signals, meta)
        assert "Vertex AI" in report, "Report missing Vertex AI header!"
        assert curr_code in report, f"Report missing {curr_code} currency reference!"
        assert len(report) > 300, "Report is suspiciously short!"
        print(f"  ✓ Vertex AI Agent markdown summary generated ({len(report)} characters).")

    print("\n" + "=" * 65)
    print("ALL 6 ASSETS VERIFIED WITH ZERO ERRORS IN THEIR DESIGNATED CURRENCIES!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
