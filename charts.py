"""
Plotly Chart Builder for Multi-Currency Quantitative Terminal
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
    Constructs the unified 3-subplot Plotly figure with dark-mode styling,
    shared x-axes, synchronized crosshairs, and dynamic currency labeling (INR for India, CAD for Canada/US).
    """
    display_title = meta.get("display_name", asset_key)
    target_curr = meta.get("target_currency", "CAD")
    curr_sym = meta.get("currency_symbol", "$")
    hedged_label = meta.get("hedged_label", "")

    # 1. Initialize 3 linked subplots with secondary y-axis for Panel 1 (Volume)
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.55, 0.22, 0.23],
        specs=[
            [{"secondary_y": True}],
            [{"secondary_y": False}],
            [{"secondary_y": False}]
        ],
        subplot_titles=(
            f"<b>{display_title}</b> Price Action ({curr_sym} {target_curr}) & Volume Profile",
            "<b>RSI (14)</b> Relative Strength Index",
            f"<b>MACD (12, 26, 9)</b> Momentum & Signal Divergence ({curr_sym} {target_curr})"
        )
    )

    # -------------------------------------------------------------
    # PANEL 1: Candlestick, EMAs, and Secondary Y-Axis Volume
    # -------------------------------------------------------------
    vol_colors = [
        'rgba(0, 245, 160, 0.32)' if c >= o else 'rgba(255, 59, 48, 0.32)'
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
                line=dict(color='#00F5A0', width=1.2),
                fillcolor='#00F5A0'
            ),
            decreasing=dict(
                line=dict(color='#FF3B30', width=1.2),
                fillcolor='#FF3B30'
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
            line=dict(color='#00E5FF', width=1.8),
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
            line=dict(color='#FFB300', width=1.8),
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
            line=dict(color='#C084FC', width=2),
            hoverinfo="y+name"
        ),
        row=2, col=1
    )

    # RSI Overbought line (70)
    fig.add_hline(
        y=70,
        line_dash="dot",
        line_color="#FF453A",
        line_width=1.2,
        annotation_text="70 Overbought",
        annotation_position="top right",
        annotation_font=dict(color="#FF453A", size=10),
        row=2, col=1
    )

    # RSI Oversold line (30)
    fig.add_hline(
        y=30,
        line_dash="dot",
        line_color="#30D158",
        line_width=1.2,
        annotation_text="30 Oversold",
        annotation_position="bottom right",
        annotation_font=dict(color="#30D158", size=10),
        row=2, col=1
    )

    # RSI Midline (50)
    fig.add_hline(
        y=50,
        line_dash="dash",
        line_color="#4B5563",
        line_width=1.0,
        row=2, col=1
    )

    # Shaded neutral band
    fig.add_hrect(
        y0=30, y1=70,
        fillcolor="rgba(192, 132, 252, 0.05)",
        line_width=0,
        row=2, col=1
    )

    # -------------------------------------------------------------
    # PANEL 3: MACD Line, Signal Line, and Color-Coded Histogram
    # -------------------------------------------------------------
    hist_colors = [
        '#00F5A0' if val >= 0 else '#FF3B30'
        for val in df['Histogram']
    ]

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Histogram'],
            name=f"MACD Hist ({target_curr})",
            marker_color=hist_colors,
            opacity=0.85,
            hoverinfo="y+name"
        ),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MACD'],
            name=f"MACD ({target_curr})",
            line=dict(color='#00F5A0', width=1.9),
            hoverinfo="y+name"
        ),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Signal_Line'],
            name=f"Signal Line ({target_curr})",
            line=dict(color='#FB923C', width=1.7, dash='solid'),
            hoverinfo="y+name"
        ),
        row=3, col=1
    )

    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="#4B5563",
        line_width=1.0,
        row=3, col=1
    )

    # -------------------------------------------------------------
    # INSTITUTIONAL DARK-THEME STYLING & SYNCHRONIZATION
    # -------------------------------------------------------------
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        font=dict(family="Inter, -apple-system, sans-serif", color="#94A3B8", size=11),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=11,
            font_family="JetBrains Mono, monospace"
        ),
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(10, 14, 23, 0.7)",
            bordercolor="rgba(148, 163, 184, 0.15)",
            borderwidth=1,
            font=dict(size=11, color="#E2E8F0")
        ),
        margin=dict(l=65, r=45, t=55, b=30),
        height=860
    )

    # Style Panel 1 Y-Axes (Candlestick in target currency on left, Volume on right)
    fig.update_yaxes(
        title_text=f"Price ({curr_sym} {target_curr})",
        showgrid=True,
        gridcolor="#1E293B",
        zerolinecolor="#1E293B",
        tickfont=dict(color="#CBD5E1"),
        secondary_y=False,
        row=1, col=1
    )

    # Scale volume bars to occupy bottom ~25% of top panel
    max_vol = df['Volume'].max() if len(df['Volume']) > 0 else 1
    fig.update_yaxes(
        range=[0, max_vol * 4.2],
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
        gridcolor="#1E293B",
        zerolinecolor="#1E293B",
        tickfont=dict(color="#CBD5E1"),
        row=2, col=1
    )

    # Style Panel 3 Y-Axis (MACD in target currency)
    fig.update_yaxes(
        title_text=f"MACD ({curr_sym})",
        showgrid=True,
        gridcolor="#1E293B",
        zerolinecolor="#1E293B",
        tickfont=dict(color="#CBD5E1"),
        row=3, col=1
    )

    # Configure shared X-axes and clean date formatting
    for r in [1, 2, 3]:
        fig.update_xaxes(
            showgrid=True,
            gridcolor="#1E293B",
            zerolinecolor="#1E293B",
            showline=True,
            linecolor="#334155",
            tickfont=dict(color="#94A3B8"),
            row=r, col=1
        )

    # Subplot titles styling
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(size=12, color='#E2E8F0', family='Inter, sans-serif')
        annotation['xanchor'] = 'left'
        annotation['x'] = 0.01

    return fig
