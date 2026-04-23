import base64
import os
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, callback_context, dcc, html


BASE_DIR = Path(__file__).parent
BG = "#f8f8f6"
CARD = "#ffffff"
PRIMARY = "#356887"
LIGHT = "#c6d5dd"
TEXT = "#263238"
MUTED = "#666666"
GREEN = "#68a66c"
ORANGE = "#d6895c"
SIDEBAR = "#356886"


def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(BASE_DIR / name)


weekly_metrics = load_csv("weekly_metrics.csv")
audience = load_csv("audience.csv")
activity_type = load_csv("activity_type.csv")
visibility = load_csv("visibility.csv")
channel_ranking = load_csv("channel_ranking.csv")
channel_totals = load_csv("channel_totals.csv")
traffic_source = load_csv("traffic_source.csv")
weekday_heatmap = load_csv("weekday_heatmap.csv")
campaign_details = load_csv("campaign_details.csv")


def card_style():
    return {
        "backgroundColor": CARD,
        "borderRadius": "24px",
        "boxShadow": "0 8px 18px rgba(20, 41, 61, 0.05)",
    }


def svg_data_uri(svg: str) -> str:
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def icon_badge(direction: str):
    bg = GREEN if direction == "up" else ORANGE
    arrow = "UP" if direction == "up" else "DN"
    return html.Span(
        arrow,
        style={
            "display": "inline-flex",
            "alignItems": "center",
            "justifyContent": "center",
            "width": "18px",
            "height": "18px",
            "borderRadius": "50%",
            "backgroundColor": bg,
            "color": "#ffffff",
            "fontSize": "9px",
            "fontWeight": "700",
            "marginRight": "8px",
        },
    )


def nav_icon(kind: str):
    svgs = {
        "home": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M4 11.5 12 5l8 6.5' fill='none' stroke='white' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/><path d='M6.5 10.5V19h11v-8.5' fill='none' stroke='white' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/></svg>",
        "grid": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><rect x='4' y='4' width='16' height='16' rx='1.5' fill='none' stroke='white' stroke-width='1.6'/><path d='M4 10h16M10 4v16M16 4v16' fill='none' stroke='white' stroke-width='1.6'/></svg>",
        "info": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><circle cx='12' cy='12' r='9' fill='none' stroke='white' stroke-width='1.8'/><circle cx='12' cy='8' r='1' fill='white'/><path d='M12 11v5' fill='none' stroke='white' stroke-width='1.8' stroke-linecap='round'/></svg>",
        "bulb": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M9 18h6M10 21h4M8.6 14.5c-1.3-1-2.1-2.6-2.1-4.4a5.5 5.5 0 1 1 11 0c0 1.8-.8 3.4-2.1 4.4-.8.6-1.4 1.5-1.6 2.5h-3.6c-.2-1-.8-1.9-1.6-2.5Z' fill='none' stroke='white' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/><path d='M12 2.5v1.6M4.8 5.5l1.1 1.1M19.2 5.5l-1.1 1.1' fill='none' stroke='white' stroke-width='1.6' stroke-linecap='round'/></svg>",
        "export": "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M14 4h6v6M20 4l-9 9' fill='none' stroke='white' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/><path d='M14 10v8H4V8h8' fill='none' stroke='white' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/></svg>",
    }
    return html.Img(
        src=svg_data_uri(svgs[kind]),
        style={
            "width": "34px",
            "height": "34px",
            "display": "block",
        },
    )


def sidebar_section(title: str, icon_component):
    return html.Div(
        [
            html.Div(title, style={"fontSize": "18px", "letterSpacing": "0.04em"}),
            html.Div(style={"width": "58px", "height": "1px", "backgroundColor": "rgba(255,255,255,0.9)", "margin": "10px auto 18px"}),
            html.Div(icon_component, style={"display": "flex", "justifyContent": "center"}),
        ],
        style={"marginTop": "54px", "textAlign": "center"},
    )


def info_modal():
    item_icon_style = {
        "width": "38px",
        "fontSize": "28px",
        "fontWeight": "700",
        "color": "#1f2d3a",
        "textAlign": "center",
        "flexShrink": "0",
    }
    item_text_style = {
        "fontSize": "15px",
        "lineHeight": "1.5",
        "color": "#334e68",
    }
    return html.Div(
        id="info-modal",
        style={"display": "none"},
        children=[
            html.Div(
                style={
                    "position": "fixed",
                    "inset": "0",
                    "backgroundColor": "rgba(20, 41, 61, 0.18)",
                    "zIndex": "999",
                }
            ),
            html.Div(
                [
                    html.Button(
                        "×",
                        id="info-close",
                        n_clicks=0,
                        style={
                            "position": "absolute",
                            "right": "26px",
                            "top": "18px",
                            "border": "none",
                            "background": "transparent",
                            "fontSize": "34px",
                            "cursor": "pointer",
                            "color": "#111111",
                        },
                    ),
                    html.H2("Information", style={"fontSize": "24px", "color": "#1f2d3a", "marginTop": "0", "marginBottom": "28px"}),
                    html.Div(
                        [
                            html.Div("▦", style=item_icon_style),
                            html.Div(
                                [
                                    html.Div("Current Week (CW): Most recently completed week of data."),
                                    html.Div("Last 10 Weeks (L10W): Rolling window of the 10 most recently completed weeks."),
                                ],
                                style=item_text_style,
                            ),
                        ],
                        style={"display": "flex", "gap": "18px", "marginBottom": "28px"},
                    ),
                    html.Div(
                        [
                            html.Div("%", style=item_icon_style),
                            html.Div(
                                [
                                    html.Div("Conversion Rate: Conversions ÷ Clicks"),
                                    html.Div("Return on Investment (ROI): Profit ÷ Cost"),
                                    html.Div("Cost per Click (CPC): Cost ÷ Clicks"),
                                ],
                                style=item_text_style,
                            ),
                        ],
                        style={"display": "flex", "gap": "18px", "marginBottom": "28px"},
                    ),
                    html.Div(
                        [
                            html.Div("▽", style=item_icon_style),
                            html.Div(
                                [
                                    html.Div("Performance dashboard focuses on CW data, with trended visuals displaying data from L10W."),
                                    html.Div("Details dashboard can be filtered to display data by CW data or L10W."),
                                ],
                                style=item_text_style,
                            ),
                        ],
                        style={"display": "flex", "gap": "18px", "marginBottom": "28px"},
                    ),
                    html.Div(
                        [
                            html.Div("⧉", style=item_icon_style),
                            html.Div("Dataset from ChatGPT-generated mock campaign marketing data.", style=item_text_style),
                        ],
                        style={"display": "flex", "gap": "18px"},
                    ),
                ],
                style={
                    "position": "fixed",
                    "top": "54px",
                    "left": "190px",
                    "right": "160px",
                    "backgroundColor": "#ffffff",
                    "border": "3px solid #e0e5e9",
                    "padding": "34px 24px 28px 24px",
                    "zIndex": "1000",
                    "minHeight": "420px",
                    "boxShadow": "0 12px 28px rgba(20, 41, 61, 0.12)",
                },
            ),
        ],
    )


def sparkline_figure(values):
    y_max = max(values)
    weeks = list(range(7, 17))
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=weeks,
            y=values,
            mode="lines+markers",
            line={"color": PRIMARY, "width": 3},
            marker={"size": 6, "color": PRIMARY},
            fill="tozeroy",
            fillcolor="rgba(53, 104, 135, 0.14)",
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        template="plotly_white",
        margin={"l": 0, "r": 0, "t": 0, "b": 22},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis={
            "tickmode": "array",
            "tickvals": weeks,
            "ticktext": [str(w) for w in weeks],
            "tickfont": {"size": 11, "color": "#666666"},
            "showgrid": False,
            "zeroline": False,
            "showline": True,
            "linecolor": "#dce4e8",
            "linewidth": 1,
            "ticks": "",
        },
        yaxis={"visible": False, "range": [0, y_max * 1.15]},
        height=130,
    )
    return fig


def horizontal_bar_figure(df: pd.DataFrame, label_col: str = "category", height: int = 190):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["value"],
            y=df[label_col],
            orientation="h",
            marker={"color": [PRIMARY] + [LIGHT] * (len(df) - 1)},
            text=[f"{v/1000:.1f}K" if v >= 1000 else f"{v}" for v in df["value"]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x}<extra></extra>",
        )
    )
    fig.update_layout(
        template="plotly_white",
        margin={"l": 118, "r": 78, "t": 8, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        height=height,
        shapes=[
            {
                "type": "line",
                "xref": "x",
                "yref": "paper",
                "x0": 0,
                "x1": 0,
                "y0": 0,
                "y1": 1,
                "line": {"color": "#d9e2e7", "width": 1.2},
            }
        ],
    )
    fig.update_xaxes(visible=False, range=[0, df["value"].max() * 1.24])
    fig.update_yaxes(autorange="reversed", tickfont={"size": 15, "color": "#444"}, showgrid=False, zeroline=False)
    return fig


def weekday_heatmap_figure(df: pd.DataFrame):
    pivot = df.pivot(index="day", columns="week", values="value").loc[["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]]
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=[str(col) for col in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[[0.0, "#f2f2f2"], [0.25, "#d8e2e8"], [0.5, "#a9c0cf"], [0.75, "#6c97af"], [1.0, PRIMARY]],
            showscale=False,
            xgap=2,
            ygap=2,
            hovertemplate="Week %{x}<br>%{y}<br>Value %{z}<extra></extra>",
        )
    )
    fig.update_layout(template="plotly_white", margin={"l": 40, "r": 20, "t": 18, "b": 20}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=208)
    fig.update_xaxes(side="top", tickfont={"size": 13, "color": "#555"}, showgrid=False)
    fig.update_yaxes(autorange="reversed", tickfont={"size": 13, "color": "#555"}, showgrid=False, zeroline=False)
    return fig


def channel_rank_figure(df: pd.DataFrame):
    weeks = df["week"].tolist()
    fig = go.Figure()
    for line in [[1, 3, 2, 4, 1, 4, 2, 5, 2, 4], [3, 2, 4, 1, 3, 1, 4, 3, 5, 2], [5, 1, 5, 2, 4, 3, 1, 4, 3, 1], [2, 4, 1, 5, 3, 5, 2, 1, 4, 3]]:
        fig.add_trace(go.Scatter(x=weeks, y=line, mode="lines", line={"color": "#dfe7ec", "width": 2}, hoverinfo="skip", showlegend=False))
    fig.add_trace(
        go.Scatter(
            x=weeks,
            y=df["rank"],
            mode="lines+markers+text",
            line={"color": PRIMARY, "width": 3},
            marker={"size": 8, "color": PRIMARY},
            text=[f"#{r}" for r in df["rank"]],
            textposition="top center",
            textfont={"size": 13, "color": TEXT},
            cliponaxis=False,
            hovertemplate="Week %{x}<br>Rank %{y}<extra></extra>",
            showlegend=False,
        )
    )
    fig.update_layout(
        template="plotly_white",
        margin={"l": 55, "r": 45, "t": 46, "b": 40},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=250,
        annotations=[{"text": "Click icons to change channel", "xref": "paper", "yref": "paper", "x": 0.82, "y": 1.03, "showarrow": False, "font": {"size": 12, "color": "#7b7b7b", "style": "italic"}}],
    )
    fig.update_xaxes(tickmode="array", tickvals=weeks, range=[6.5, 16.5], tickfont={"size": 13, "color": "#555"}, showgrid=False, zeroline=False)
    fig.update_yaxes(tickmode="array", tickvals=[1, 2, 3, 4, 5], ticktext=["#1", "#2", "#3", "#4", "#5"], autorange="reversed", range=[5.3, 0.7], tickfont={"size": 13, "color": "#555"}, gridcolor="#e5ecef", zeroline=False)
    return fig


def duration_histogram(df: pd.DataFrame):
    avg = df["duration_days"].mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["duration_days"], y=[1] * len(df), marker={"color": ["#dfe7ec"] * len(df)}, hovertemplate="%{x} days<extra></extra>", showlegend=False))
    fig.add_vline(x=avg, line_width=3, line_color=PRIMARY)
    fig.add_annotation(x=avg, y=1.12, xref="x", yref="paper", text=f"Average: {avg:.0f} days", showarrow=False, font={"size": 12, "color": TEXT}, bgcolor="rgba(255,255,255,0.9)")
    fig.update_layout(template="plotly_white", margin={"l": 0, "r": 0, "t": 18, "b": 18}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=120)
    fig.update_xaxes(range=[10, 90], dtick=10, tickfont={"size": 11}, showgrid=False)
    fig.update_yaxes(visible=False)
    return fig


def detail_kpi_card(title: str, value: str, subtitle: str, figure=None):
    parts = [html.Div(title, style={"fontSize": "16px", "color": MUTED}), html.Div(value, style={"fontSize": "28px", "fontWeight": "700", "color": "#333", "marginTop": "24px"}), html.Div(subtitle, style={"fontSize": "16px", "color": GREEN, "marginTop": "12px"})]
    if figure is not None:
        parts.append(dcc.Graph(figure=figure, config={"displayModeBar": False}, style={"height": "140px", "marginTop": "6px"}))
    return html.Div(parts, style={**card_style(), "padding": "20px 20px 14px"})


def kpi_card(metric_row: pd.Series):
    value = metric_row["value"]
    if metric_row["metric"] in {"Impressions", "Clicks"}:
        display_value = f"{value/1000:.1f}K" if value >= 1000 else f"{value}"
    elif metric_row["metric"] in {"Conversion Rate", "ROI"}:
        display_value = f"{int(value)}%"
    elif metric_row["metric"] == "Profit":
        display_value = f"${value/1000:.1f}K"
    elif metric_row["metric"] == "CPC":
        display_value = f"${int(value)}"
    else:
        display_value = str(value)
    trend_values = [metric_row[f"trend_{week}"] for week in range(7, 17)]
    change_icon = "up" if metric_row["change_pct"] > 0 else "down"
    change_color = GREEN if metric_row["change_pct"] > 0 else ORANGE
    return html.Div(
        [
            html.Div(metric_row["metric"], style={"fontSize": "18px", "color": "#202020", "marginTop": "-8px"}),
            html.Div(display_value, style={"fontSize": "28px", "fontWeight": "700", "color": "#333333", "marginTop": "28px"}),
            html.Div([icon_badge(change_icon), html.Span(metric_row["change_label"])], style={"fontSize": "16px", "color": change_color, "marginTop": "10px", "display": "flex", "alignItems": "center"}),
            dcc.Graph(figure=sparkline_figure(trend_values), config={"displayModeBar": False}, style={"height": "142px", "marginTop": "6px"}),
        ],
        style={**card_style(), "padding": "18px 18px 10px", "border": "1px solid rgba(53, 104, 135, 0.08)"},
    )


def small_bar_card(df: pd.DataFrame, small_title: str, big_title: str):
    return html.Div([html.Div([html.Div(small_title, style={"fontSize": "16px", "color": MUTED}), html.Div(big_title, style={"fontSize": "18px", "fontWeight": "700", "color": TEXT, "marginTop": "2px"})], style={"padding": "20px 22px 0"}), dcc.Graph(figure=horizontal_bar_figure(df), config={"displayModeBar": False}, style={"height": "205px"})], style={**card_style(), "paddingBottom": "8px"})


def heatmap_card(df: pd.DataFrame):
    return html.Div([html.Div([html.Div("Impressions by", style={"fontSize": "16px", "color": MUTED}), html.Div("Weekday & Week No", style={"fontSize": "18px", "fontWeight": "700", "color": TEXT, "marginTop": "2px"})], style={"padding": "18px 22px 0"}), dcc.Graph(figure=weekday_heatmap_figure(df), config={"displayModeBar": False}, style={"height": "225px"})], style={**card_style(), "paddingBottom": "8px"})


def ranking_card(figure, small_title: str, big_title: str, height: str = "285px"):
    return html.Div([html.Div([html.Div(small_title, style={"fontSize": "16px", "color": MUTED}), html.Div(big_title, style={"fontSize": "18px", "fontWeight": "700", "color": TEXT, "marginTop": "2px"})], style={"padding": "20px 22px 0"}), dcc.Graph(figure=figure, config={"displayModeBar": False}, style={"height": height})], style={**card_style(), "paddingBottom": "8px"})


def objective_summary(df: pd.DataFrame, column: str, label: str):
    summary = df.groupby(column).size().reset_index(name="value").sort_values("value", ascending=False).rename(columns={column: "category"})
    return html.Div([html.Div("# of Campaigns by", style={"fontSize": "16px", "color": MUTED}), html.Div(label, style={"fontSize": "18px", "fontWeight": "700", "color": TEXT, "marginTop": "2px"}), dcc.Graph(figure=horizontal_bar_figure(summary, height=150), config={"displayModeBar": False}, style={"height": "160px", "marginTop": "10px"})], style={**card_style(), "padding": "20px 20px 8px"})


def details_table(df: pd.DataFrame):
    header_style = {"backgroundColor": "#dfe7ec", "padding": "14px 12px", "fontWeight": "700", "fontSize": "14px", "color": "#333", "textAlign": "left", "borderBottom": "1px solid #d7dfe3"}
    cell_style = {"padding": "14px 12px", "fontSize": "14px", "color": "#333", "borderBottom": "1px solid #e6ecef", "verticalAlign": "top"}
    rows = []
    for _, row in df.iterrows():
        rows.append(html.Tr([html.Td([html.Div(row["campaign_name"], style={"fontWeight": "600"}), html.Div(row["campaign_id"], style={"color": "#888", "marginTop": "4px"})], style=cell_style), html.Td([html.Div(f"{row['duration_days']} days", style={"fontWeight": "600"}), html.Div(row["end_date"], style={"color": "#888", "marginTop": "4px"})], style=cell_style), html.Td(row["objective"], style=cell_style), html.Td(row["target_audience"], style=cell_style), html.Td(row["source"], style=cell_style), html.Td(row["impressions"], style=cell_style), html.Td(row["clicks"], style=cell_style), html.Td(row["conversions"], style=cell_style)]))
    return html.Div(html.Table([html.Thead(html.Tr([html.Th("Campaign Name", style=header_style), html.Th("Duration", style=header_style), html.Th("Objective", style=header_style), html.Th("Target Audience", style=header_style), html.Th("Source", style=header_style), html.Th("Impressions", style=header_style), html.Th("Clicks", style=header_style), html.Th("Conversions", style=header_style)])), html.Tbody(rows)], style={"width": "100%", "borderCollapse": "collapse"}), style={"maxHeight": "720px", "overflowY": "auto"})


def sidebar(pathname: str):
    info_icon = nav_icon("info")
    bulb_icon = nav_icon("bulb")
    export_icon = nav_icon("export")
    dots_icon = html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(3, 6px)", "gap": "5px", "justifyContent": "center"}, children=[html.Span(style={"width": "6px", "height": "6px", "borderRadius": "50%", "backgroundColor": "#ffffff"}) for _ in range(9)])
    return html.Div(
        [
            html.Div("k", style={"fontSize": "76px", "fontWeight": "700", "lineHeight": "1", "color": "#ffffff"}),
            html.Div(
                [
                    html.Div("NAVIGATE", style={"fontSize": "18px", "letterSpacing": "0.04em", "marginBottom": "18px"}),
                    dcc.Link(nav_icon("home"), href="/", style={"display": "flex", "justifyContent": "center", "alignItems": "center", "padding": "14px 10px", "marginTop": "18px", "borderRadius": "10px", "backgroundColor": "rgba(255,255,255,0.18)" if pathname == "/" else "transparent"}),
                    dcc.Link(nav_icon("grid"), href="/details", style={"display": "flex", "justifyContent": "center", "alignItems": "center", "padding": "14px 10px", "marginTop": "18px", "borderRadius": "10px", "backgroundColor": "rgba(255,255,255,0.18)" if pathname == "/details" else "transparent"}),
                    html.Div(
                        [
                            html.Div("INFO", style={"fontSize": "18px", "letterSpacing": "0.04em"}),
                            html.Div(style={"width": "58px", "height": "1px", "backgroundColor": "rgba(255,255,255,0.9)", "margin": "10px auto 18px"}),
                            html.Button(
                                info_icon,
                                id="info-open",
                                n_clicks=0,
                                style={
                                    "background": "transparent",
                                    "border": "none",
                                    "padding": "0",
                                    "cursor": "pointer",
                                    "display": "flex",
                                    "justifyContent": "center",
                                    "width": "100%",
                                },
                            ),
                        ],
                        style={"marginTop": "54px", "textAlign": "center"},
                    ),
                    html.Div(style={"marginTop": "24px", "display": "flex", "justifyContent": "center"}, children=[bulb_icon]),
                    sidebar_section("EXPORT", export_icon),
                    html.Div("CONNECT", style={"fontSize": "18px", "marginTop": "18px", "letterSpacing": "0.04em"}),
                    html.Div(style={"width": "58px", "height": "1px", "backgroundColor": "rgba(255,255,255,0.9)", "margin": "10px auto 18px"}),
                    html.Div("in", style={"fontSize": "56px", "fontWeight": "700", "marginTop": "4px"}),
                    html.Div(style={"marginTop": "26px", "display": "flex", "justifyContent": "center"}, children=[dots_icon]),
                    html.Div("Keep Guide", style={"fontSize": "20px", "fontStyle": "italic", "marginTop": "120px", "transform": "rotate(-90deg) translateX(-80px)", "transformOrigin": "left top"}),
                ],
                style={"color": "#e7f0f4", "textAlign": "center", "marginTop": "54px"},
            ),
        ],
        style={"width": "120px", "backgroundColor": SIDEBAR, "borderRadius": "24px 0 0 24px", "padding": "28px 12px", "display": "flex", "flexDirection": "column", "alignItems": "center"},
    )


def overview_page():
    return html.Div(
        [
            html.Div([html.Div([html.H1("Marketing Campaign Performance", style={"margin": "0", "fontSize": "44px", "color": "#333333"}), html.Div("Weekly Overview | 2026 - Week 16", style={"fontSize": "24px", "color": "#444444", "marginTop": "10px"})]), html.Div([html.Div("<Full Name>", style={"fontSize": "18px", "textAlign": "right"}), html.Div("Logged In!", style={"fontSize": "18px", "color": "#1f9d3a", "marginTop": "4px", "textAlign": "right"})])], style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start"}),
            html.Div("Click KPI card to filter dashboard view", style={"fontSize": "18px", "fontStyle": "italic", "color": "#575757", "margin": "34px 0 18px 0"}),
            html.Div([kpi_card(row) for _, row in weekly_metrics.iterrows()], style={"display": "grid", "gridTemplateColumns": "repeat(3, minmax(0, 1fr))", "gap": "18px"}),
            html.Div([small_bar_card(audience, "Impressions by", "Target Audience"), small_bar_card(activity_type, "Impressions by", "Activity Type"), small_bar_card(visibility, "Impressions by", "Visibility"), heatmap_card(weekday_heatmap)], style={"display": "grid", "gridTemplateColumns": "1.1fr 1.1fr 1.1fr 1.6fr", "gap": "14px", "marginTop": "28px"}),
            html.Div([ranking_card(channel_rank_figure(channel_ranking), "Impressions Ranked by", "Channel & Week No", height="300px"), ranking_card(horizontal_bar_figure(channel_totals.rename(columns={"channel": "category"}), height=220), "Impressions by", "Channel", height="250px"), ranking_card(horizontal_bar_figure(traffic_source.rename(columns={"source": "category"}), height=220), "Impressions by", "Traffic Source", height="250px")], style={"display": "grid", "gridTemplateColumns": "2.2fr 1fr 1fr", "gap": "14px", "marginTop": "24px"}),
        ],
        style={"flex": "1", "padding": "34px 34px 28px"},
    )


def details_page():
    stage_counts = pd.DataFrame({"category": ["Consider", "Decision", "Aware"], "value": [43, 31, 25]})
    top_panel = html.Div(
        [
            detail_kpi_card("# of Campaigns", f"{len(campaign_details)}", "up 60% WoW", sparkline_figure([61, 59, 60, 58, 47, 53, 52, 53, 42, 48])),
            html.Div([html.Div("# of Campaigns by", style={"fontSize": "16px", "color": MUTED}), html.Div("Duration (days)", style={"fontSize": "18px", "fontWeight": "700", "color": TEXT, "marginTop": "2px"}), dcc.Graph(figure=duration_histogram(campaign_details), config={"displayModeBar": False}, style={"height": "140px", "marginTop": "18px"})], style={**card_style(), "padding": "20px 20px 10px"}),
            objective_summary(campaign_details, "objective", "Objective"),
            html.Div([html.Div("# of Campaigns by", style={"fontSize": "16px", "color": MUTED}), html.Div("Stage", style={"fontSize": "18px", "fontWeight": "700", "color": TEXT, "marginTop": "2px"}), dcc.Graph(figure=horizontal_bar_figure(stage_counts, height=150), config={"displayModeBar": False}, style={"height": "160px", "marginTop": "10px"})], style={**card_style(), "padding": "20px 20px 8px"}),
        ],
        style={"display": "grid", "gridTemplateColumns": "1.3fr 1fr 0.8fr 0.8fr", "gap": "16px", "backgroundColor": "#fbfaf8", "padding": "24px", "borderRadius": "28px"},
    )
    return html.Div(
        [
            html.Div([html.Div([html.H1("Marketing Campaign Details", style={"margin": "0", "fontSize": "44px", "color": "#333333"}), html.Div("Weekly Overview | 2026 - Week 16", style={"fontSize": "24px", "color": "#444444", "marginTop": "10px"})]), html.Div([html.Div("<Full Name>", style={"fontSize": "18px", "textAlign": "right"}), html.Div("Logged In!", style={"fontSize": "18px", "color": "#1f9d3a", "marginTop": "4px", "textAlign": "right"})])], style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start"}),
            html.Div([html.Div("Display by:", style={"fontSize": "18px", "color": "#444"}), html.Div("Last 10 Weeks", style={"fontSize": "18px", "color": "#444", "marginLeft": "10px"})], style={"display": "flex", "alignItems": "center", "margin": "18px 0 26px 0"}),
            top_panel,
            html.Div(details_table(campaign_details), style={**card_style(), "marginTop": "22px", "padding": "18px"}),
        ],
        style={"flex": "1", "padding": "34px 34px 28px"},
    )


def app_shell(pathname: str):
    return html.Div(
        [sidebar(pathname), details_page() if pathname == "/details" else overview_page(), info_modal()],
        style={"display": "flex", "backgroundColor": BG, "borderRadius": "24px", "boxShadow": "0 8px 24px rgba(20, 41, 61, 0.08)", "overflow": "hidden", "position": "relative"},
    )


app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "Part 2 Overview Recreation"
app.layout = html.Div([dcc.Location(id="url"), html.Div(id="page-content")], style={"minHeight": "100vh", "background": "linear-gradient(180deg, #fcfcfc 0%, #f4f4f2 100%)", "padding": "34px", "fontFamily": "Segoe UI, Arial, sans-serif"})


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    return app_shell(pathname)


@app.callback(
    Output("info-modal", "style"),
    Input("info-open", "n_clicks"),
    Input("info-close", "n_clicks"),
    State("info-modal", "style"),
    prevent_initial_call=True,
)
def toggle_info_modal(open_clicks, close_clicks, current_style):
    if not callback_context.triggered:
        return current_style or {"display": "none"}
    trigger = callback_context.triggered[0]["prop_id"].split(".")[0]
    if trigger == "info-open":
        return {"display": "block"}
    return {"display": "none"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8060))
    app.run(debug=False, host="0.0.0.0", port=port)




