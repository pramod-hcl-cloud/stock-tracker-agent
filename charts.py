"""
Plotly Chart Builder for Multi-Currency Quantitative Terminal
Minimalist, high-contrast light mode financial charts (white background).
Builds a unified 3-panel vertical subplot system sharing the X-axis:
- Panel 1: Candlesticks (Currency-Specific) + EMA12 + EMA26 + Volume on secondary Y-axis
- Panel 2: RSI 14-period with 30/70 boundary levels
- Panel 3: MACD, Signal line, and color-coded Histogram
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def create_financial_dashboard_figure(df: pd.DataFrame, asset_key: str, meta: dict) -> go.Figure:
    """
    Constructs the unified 3-subplot Plotly figure with sleek, modern light-mode styling (white background),
    shared x-axes, synchronized crosshairs, and dynamic currency labeling.
    """
    display_title = meta.get("display_name", asset_key)
    target_curr = meta.get("target_currency", "CAD")
    curr_sym = meta.get("currency_symbol", "$")
    is_forex = meta.get("is_forex", False)

    # 1. Initialize 3 linked subplots with secondary y-axis for Panel 1 (Volume)
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.035,
        row_heights=[0.55, 0.22, 0.23],
        specs=[
            [{"secondary_y": True}],
            [{"secondary_y": False}],
            [{"secondary_y": False}]
        ],
        subplot_titles=(
            f"<b>{display_title}</b> Price Action ({curr_sym} {target_curr}) & Volume",
            "<b>RSI (14)</b> Relative Strength Index",
            f"<b>MACD (12, 26, 9)</b> Momentum & Signal Divergence ({curr_sym} {target_curr})"
        )
    )

    # -------------------------------------------------------------
    # PANEL 1: Candlestick, EMAs, and Secondary Y-Axis Volume
    # -------------------------------------------------------------
    has_volume = not is_forex and len(df['Volume']) > 0 and df['Volume'].max() > 0

    if has_volume:
        vol_colors = [
            'rgba(5, 150, 105, 0.25)' if c >= o else 'rgba(225, 29, 72, 0.25)'
            for c, o in zip(df['Close'], df['Open'])
        ]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                marker_color=vol_colors,
                name="Volume",
                hoverinfo="x+y",
                showlegend=True
            ),
            row=1, col=1,
            secondary_y=True
        )

    # Candlestick chart in asset target currency (INR or CAD)
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=f"Price ({target_curr})",
            increasing=dict(
                line=dict(color='#059669', width=1.3),
                fillcolor='#059669'
            ),
            decreasing=dict(
                line=dict(color='#E11D48', width=1.3),
                fillcolor='#E11D48'
            )
        ),
        row=1, col=1,
        secondary_y=False
    )

    # EMA 12
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['EMA12'],
            name=f"EMA 12 ({target_curr})",
            line=dict(color='#0284C7', width=1.8),
            hoverinfo="y+name"
        ),
        row=1, col=1,
        secondary_y=False
    )

    # EMA 26
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['EMA26'],
            name=f"EMA 26 ({target_curr})",
            line=dict(color='#D97706', width=1.8),
            hoverinfo="y+name"
        ),
        row=1, col=1,
        secondary_y=False
    )

    # -------------------------------------------------------------
    # PANEL 2: RSI (14) with 70 / 30 Boundaries and Shaded Zone
    # -------------------------------------------------------------
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['RSI'],
            name="RSI (14)",
            line=dict(color='#7C3AED', width=2),
            hoverinfo="y+name"
        ),
        row=2, col=1
    )

    # RSI Overbought line (70)
    fig.add_hline(
        y=70,
        line_dash="dot",
        line_color="#DC2626",
        line_width=1.2,
        annotation_text="70 Overbought",
        annotation_position="top right",
        annotation_font=dict(color="#DC2626", size=10),
        row=2, col=1
    )

    # RSI Oversold line (30)
    fig.add_hline(
        y=30,
        line_dash="dot",
        line_color="#16A34A",
        line_width=1.2,
        annotation_text="30 Oversold",
        annotation_position="bottom right",
        annotation_font=dict(color="#16A34A", size=10),
        row=2, col=1
    )

    # RSI Midline (50)
    fig.add_hline(
        y=50,
        line_dash="dash",
        line_color="#CBD5E1",
        line_width=1.0,
        row=2, col=1
    )

    # Shaded neutral band
    fig.add_hrect(
        y0=30, y1=70,
        fillcolor="rgba(124, 58, 237, 0.04)",
        line_width=0,
        row=2, col=1
    )

    # -------------------------------------------------------------
    # PANEL 3: MACD Line, Signal Line, and Color-Coded Histogram
    # -------------------------------------------------------------
    hist_colors = [
        '#059669' if val >= 0 else '#E11D48'
        for val in df['Histogram']
    ]

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Histogram'],
            name=f"MACD Hist ({target_curr})",
            marker_color=hist_colors,
            opacity=0.8,
            hoverinfo="y+name"
        ),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MACD'],
            name=f"MACD ({target_curr})",
            line=dict(color='#059669', width=1.9),
            hoverinfo="y+name"
        ),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Signal_Line'],
            name=f"Signal Line ({target_curr})",
            line=dict(color='#EA580C', width=1.7, dash='solid'),
            hoverinfo="y+name"
        ),
        row=3, col=1
    )

    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="#CBD5E1",
        line_width=1.0,
        row=3, col=1
    )

    # -------------------------------------------------------------
    # LIGHT-MODE MINIMALIST STYLING (WHITE BACKGROUND)
    # -------------------------------------------------------------
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif", color="#475569", size=11),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=11,
            font_family="-apple-system, BlinkMacSystemFont, 'Inter', monospace",
            bordercolor="#E2E8F0"
        ),
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#E2E8F0",
            borderwidth=1,
            font=dict(size=11, color="#334155")
        ),
        margin=dict(l=65, r=45, t=55, b=30),
        height=820
    )

    # Style Panel 1 Y-Axes (Price on left, Volume on right)
    fig.update_yaxes(
        title_text=f"Price ({curr_sym} {target_curr})",
        showgrid=True,
        gridcolor="#F1F5F9",
        zerolinecolor="#E2E8F0",
        tickfont=dict(color="#475569"),
        secondary_y=False,
        row=1, col=1
    )

    # Scale volume bars if available
    if has_volume:
        max_vol = df['Volume'].max()
        fig.update_yaxes(
            range=[0, max_vol * 4.2 if max_vol > 0 else 1],
            showgrid=False,
            showticklabels=False,
            secondary_y=True,
            row=1, col=1
        )
    else:
        fig.update_yaxes(
            showgrid=False,
            showticklabels=False,
            secondary_y=True,
            row=1, col=1
        )

    # Style Panel 2 Y-Axis (RSI)
    fig.update_yaxes(
        title_text="RSI",
        range=[0, 100],
        tickvals=[20, 30, 50, 70, 80],
        showgrid=True,
        gridcolor="#F1F5F9",
        zerolinecolor="#E2E8F0",
        tickfont=dict(color="#475569"),
        row=2, col=1
    )

    # Style Panel 3 Y-Axis (MACD)
    fig.update_yaxes(
        title_text=f"MACD ({curr_sym})",
        showgrid=True,
        gridcolor="#F1F5F9",
        zerolinecolor="#E2E8F0",
        tickfont=dict(color="#475569"),
        row=3, col=1
    )

    # Configure shared X-axes and clean date formatting
    for r in [1, 2, 3]:
        fig.update_xaxes(
            showgrid=True,
            gridcolor="#F1F5F9",
            zerolinecolor="#E2E8F0",
            showline=True,
            linecolor="#E2E8F0",
            tickfont=dict(color="#64748B"),
            row=r, col=1
        )

    # Subplot titles styling
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(size=12, color='#1E293B', family='-apple-system, BlinkMacSystemFont, "Inter", sans-serif', weight=500)
        annotation['xanchor'] = 'left'
        annotation['x'] = 0.01

    return fig
