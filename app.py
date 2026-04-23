import os
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html


DATA_FILE = Path(__file__).with_name("Alipay_data.csv")
START_MONTH = pd.Timestamp("2025-04-01")
END_MONTH = pd.Timestamp("2026-03-01")
CNY_SYMBOL = "\uFFE5"


def load_monthly_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    df["Month"] = pd.to_datetime(df["Date"], format="%b-%y")
    df["Sent"] = pd.to_numeric(df["Sent"], errors="coerce")
    df = df.dropna(subset=["Month", "Sent"]).sort_values("Month").reset_index(drop=True)
    df = df.loc[df["Month"].between(START_MONTH, END_MONTH)].reset_index(drop=True)
    df["MonthLabel"] = df["Month"].dt.strftime("%b-%y")
    return df


def build_figure(df: pd.DataFrame) -> go.Figure:
    average_payment = df["Sent"].mean()
    y_max = df["Sent"].max()
    default_color = "#1f77b4"

    figure = go.Figure()
    figure.add_trace(
        go.Bar(
            x=df["MonthLabel"],
            y=df["Sent"],
            name="Monthly Payment",
            marker_color=default_color,
            hovertemplate=f"Month: %{{x}}<br>Payment: {CNY_SYMBOL}%{{y:,.2f}}<extra></extra>",
            showlegend=False,
        )
    )
    figure.add_hline(
        y=average_payment,
        line_dash="dash",
        line_color="#ff9f1c",
        line_width=2,
    )
    figure.add_annotation(
        x="Feb-26",
        y=average_payment,
        text=f"Avg: {CNY_SYMBOL}{average_payment:,.2f}",
        showarrow=False,
        xshift=90,
        yshift=16,
        bgcolor="rgba(255, 255, 255, 0.78)",
        font={"color": "#000000", "size": 18},
    )
    figure.update_layout(
        title={
            "text": (
                "<b>Monthly Alipay Payments Over Time</b>"
                "<br><sup style='font-size:18px;'>Monthly payments from Apr-25 to Mar-26</sup>"
            ),
            "x": 0.5,
            "xanchor": "center",
            "y": 0.90,
            "yanchor": "top",
            "font": {"size": 26, "color": "#17324d"},
        },
        template="plotly_white",
        hovermode="x unified",
        bargap=0.25,
        height=850,
        yaxis_title="Total Payment (CNY)",
        margin={"l": 100, "r": 100, "t": 180, "b": 120},
    )
    figure.update_xaxes(title_text=None, tickfont={"size": 17}, ticklabelstandoff=14)
    figure.update_yaxes(
        title_font={"size": 24},
        tickfont={"size": 15},
        tickprefix=CNY_SYMBOL,
        separatethousands=True,
        range=[0, y_max * 1.28],
    )
    return figure


def build_ranking_figure(df: pd.DataFrame) -> go.Figure:
    ranking_df = df.sort_values("Sent", ascending=False).reset_index(drop=True)
    average_payment = ranking_df["Sent"].mean()
    highest_row = ranking_df.iloc[0]
    lowest_row = ranking_df.iloc[-1]
    x_max = ranking_df["Sent"].max()
    default_color = "#1f77b4"
    highest_color = "#ef553b"
    lowest_color = "#00a676"
    bar_colors = [
        highest_color
        if month == highest_row["MonthLabel"]
        else lowest_color
        if month == lowest_row["MonthLabel"]
        else default_color
        for month in ranking_df["MonthLabel"]
    ]

    figure = go.Figure()
    figure.add_trace(
        go.Bar(
            x=ranking_df["Sent"],
            y=ranking_df["MonthLabel"],
            orientation="h",
            marker_color=bar_colors,
            hovertemplate=f"Month: %{{y}}<br>Payment: {CNY_SYMBOL}%{{x:,.2f}}<extra></extra>",
            showlegend=False,
        )
    )
    figure.add_vline(
        x=average_payment,
        line_dash="dash",
        line_color="#ff9f1c",
        line_width=2,
    )
    figure.add_annotation(
        x=average_payment,
        y=0.5,
        xref="x",
        yref="paper",
        text=f"Avg: {CNY_SYMBOL}{average_payment:,.2f}",
        showarrow=False,
        xshift=38,
        yshift=-16,
        bgcolor="rgba(255, 255, 255, 0.78)",
        font={"color": "#000000", "size": 18},
    )
    figure.add_annotation(
        x=highest_row["Sent"],
        y=highest_row["MonthLabel"],
        text=f"Highest: {CNY_SYMBOL}{highest_row['Sent']:,.2f}",
        showarrow=False,
        xshift=100,
        bgcolor="rgba(255, 255, 255, 0.72)",
        font={"color": "#000000", "size": 18},
    )
    figure.add_annotation(
        x=lowest_row["Sent"],
        y=lowest_row["MonthLabel"],
        text=f"Lowest: {CNY_SYMBOL}{lowest_row['Sent']:,.2f}",
        showarrow=False,
        xshift=96,
        bgcolor="rgba(255, 255, 255, 0.72)",
        font={"color": "#000000", "size": 18},
    )
    figure.update_layout(
        title={
            "text": (
                "<b>Monthly Payment Ranking</b>"
                "<br><sup style='font-size:18px;'>Payments sorted from highest to lowest (Apr-25 to Mar-26)</sup>"
            ),
            "x": 0.5,
            "xanchor": "center",
            "y": 0.92,
            "yanchor": "top",
            "font": {"size": 24, "color": "#17324d"},
        },
        template="plotly_white",
        hovermode="y unified",
        height=780,
        margin={"l": 130, "r": 120, "t": 150, "b": 100},
        xaxis_title="Payment Amount (CNY)",
        yaxis_title="Month",
    )
    figure.update_xaxes(
        tickfont={"size": 16},
        title_font={"size": 22},
        tickprefix=CNY_SYMBOL,
        separatethousands=True,
        range=[0, x_max * 1.33],
    )
    figure.update_yaxes(
        tickfont={"size": 17},
        title_font={"size": 22},
        categoryorder="array",
        categoryarray=ranking_df["MonthLabel"][::-1],
    )
    return figure


def raw_data_table(df: pd.DataFrame) -> html.Div:
    table_header_style = {
        "backgroundColor": "#17324d",
        "color": "#ffffff",
        "padding": "12px 16px",
        "fontSize": "16px",
        "textAlign": "left",
    }
    table_cell_style = {
        "padding": "12px 16px",
        "fontSize": "15px",
        "borderBottom": "1px solid #dce7f3",
        "textAlign": "left",
    }

    return html.Div(
        [
            html.H2(
                "Raw Data",
                style={"color": "#17324d", "marginBottom": "14px", "fontSize": "28px"},
            ),
            html.P(
                "Monthly Alipay payment records used in the visualizations.",
                style={"color": "#5c6b7a", "marginTop": 0, "marginBottom": "18px", "fontSize": "17px"},
            ),
            html.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Month", style=table_header_style),
                                html.Th("Payment Amount (CNY)", style=table_header_style),
                            ]
                        )
                    ),
                    html.Tbody(
                        [
                            html.Tr(
                                [
                                    html.Td(row["MonthLabel"], style=table_cell_style),
                                    html.Td(f"{CNY_SYMBOL}{row['Sent']:,.2f}", style=table_cell_style),
                                ]
                            )
                            for _, row in df.iterrows()
                        ]
                    ),
                ],
                style={
                    "width": "100%",
                    "borderCollapse": "collapse",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "14px",
                    "overflow": "hidden",
                    "boxShadow": "0 10px 25px rgba(31, 119, 180, 0.08)",
                },
            ),
        ],
        style={"marginTop": "24px"},
    )


def assignment_context() -> html.Div:
    section_title_style = {
        "fontSize": "30px",
        "fontWeight": "700",
        "color": "#17324d",
        "marginBottom": "16px",
    }
    heading_style = {
        "fontSize": "22px",
        "fontWeight": "700",
        "color": "#17324d",
        "marginBottom": "8px",
    }
    paragraph_style = {
        "fontSize": "18px",
        "lineHeight": "1.7",
        "color": "#334e68",
        "marginTop": 0,
        "marginBottom": "18px",
    }

    return html.Div(
        [
            html.H1("Part 1 Visualization", style=section_title_style),
            html.H2("Problem Statement", style=heading_style),
            html.P(
                (
                    "The audience for this visualization is myself, because I am the person most interested "
                    "in understanding how much I spent through Alipay over time. This is relevant to me "
                    "because it helps me review my monthly payment habits, identify spending peaks and low "
                    "points, and better understand my overall personal payment pattern."
                ),
                style=paragraph_style,
            ),
            html.H2("Brief Description of the Findings", style=heading_style),
            html.P(
                (
                    "The time-based visualization shows how my Alipay payments changed from Apr-25 to Mar-26, "
                    "while the ranking visualization highlights which months had the highest and lowest payment "
                    "amounts. April 2025 had the highest payment at "
                    f"{CNY_SYMBOL}4,136.35, while July 2025 had the lowest payment at {CNY_SYMBOL}75.20. "
                    f"The average monthly payment was {CNY_SYMBOL}1,205.97, and the data shows that spending "
                    "varied considerably across the year rather than staying consistent month to month."
                ),
                style=paragraph_style,
            ),
        ],
        style={"marginBottom": "28px"},
    )


def summary_cards(df: pd.DataFrame) -> html.Div:
    total_payment = df["Sent"].sum()
    average_payment = df["Sent"].mean()
    highest_row = df.loc[df["Sent"].idxmax()]
    lowest_row = df.loc[df["Sent"].idxmin()]

    card_style = {
        "flex": "1",
        "minWidth": "220px",
        "backgroundColor": "#ffffff",
        "padding": "20px",
        "borderRadius": "14px",
        "boxShadow": "0 10px 25px rgba(31, 119, 180, 0.08)",
        "border": "1px solid #dce7f3",
    }

    label_style = {
        "fontSize": "14px",
        "color": "#5c6b7a",
        "marginBottom": "8px",
        "textTransform": "uppercase",
        "letterSpacing": "0.08em",
    }

    value_style = {"fontSize": "28px", "fontWeight": "700", "color": "#17324d", "margin": 0}

    return html.Div(
        [
            html.Div(
                [
                    html.Div("Total Payment", style=label_style),
                    html.P(f"{CNY_SYMBOL}{total_payment:,.2f}", style=value_style),
                ],
                style=card_style,
            ),
            html.Div(
                [
                    html.Div("Average Per Month", style=label_style),
                    html.P(f"{CNY_SYMBOL}{average_payment:,.2f}", style=value_style),
                ],
                style=card_style,
            ),
            html.Div(
                [
                    html.Div("Highest Payment", style=label_style),
                    html.P(
                        f"{CNY_SYMBOL}{highest_row['Sent']:,.2f}",
                        style={**value_style, "color": "#000000"},
                    ),
                ],
                style=card_style,
            ),
            html.Div(
                [
                    html.Div("Lowest Payment", style=label_style),
                    html.P(
                        f"{CNY_SYMBOL}{lowest_row['Sent']:,.2f}",
                        style={**value_style, "color": "#000000"},
                    ),
                ],
                style=card_style,
            ),
        ],
        style={"display": "flex", "gap": "18px", "flexWrap": "wrap", "marginBottom": "24px"},
    )


df = load_monthly_data()
app = Dash(__name__)
app.title = "Alipay Monthly Dashboard"

app.layout = html.Div(
    [
        assignment_context(),
        dcc.Graph(figure=build_figure(df), config={"displayModeBar": False}),
        dcc.Graph(figure=build_ranking_figure(df), config={"displayModeBar": False}),
        raw_data_table(df),
    ],
    style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "56px 20px 48px",
        "fontFamily": "Segoe UI, Arial, sans-serif",
        "background": "linear-gradient(180deg, #f4f9ff 0%, #edf4fb 100%)",
        "minHeight": "100vh",
    },
)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)
