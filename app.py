from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

import dash
from dash import dcc, html


def load_daily_sales(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")

    # Aggregate across regions to answer "were sales higher" in total.
    daily = (
        df.groupby("Date", as_index=False)["Sales"]
        .sum()
        .sort_values("Date")
        .reset_index(drop=True)
    )
    return daily


def make_figure(daily: pd.DataFrame, cutoff: pd.Timestamp) -> tuple[go.Figure, str]:
    before = daily[daily["Date"] < cutoff]
    after = daily[daily["Date"] >= cutoff]

    before_avg = float(before["Sales"].mean()) if not before.empty else float("nan")
    after_avg = float(after["Sales"].mean()) if not after.empty else float("nan")

    conclusion = (
        "Average daily sales are higher after the price increase."
        if after_avg > before_avg
        else "Average daily sales are higher before the price increase."
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=before["Date"],
            y=before["Sales"],
            mode="lines",
            name="Before 15 Jan 2021",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=after["Date"],
            y=after["Sales"],
            mode="lines",
            name="On/After 15 Jan 2021",
        )
    )

    sales_max = float(daily["Sales"].max()) if not daily.empty else 0.0
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Total Sales ($)",
        hovermode="x unified",
        legend_title_text="Period",
        shapes=[
            dict(
                type="line",
                x0=cutoff,
                x1=cutoff,
                y0=0,
                y1=sales_max * 1.05,
                xref="x",
                yref="y",
                line=dict(dash="dash", width=2, color="firebrick"),
            )
        ],
        annotations=[
            dict(
                x=cutoff,
                y=sales_max * 1.02,
                xref="x",
                yref="y",
                text="Price increase date (15 Jan 2021)",
                showarrow=False,
                font=dict(size=12, color="firebrick"),
                align="left",
                bgcolor="rgba(255,255,255,0.8)",
            )
        ],
    )

    return fig, conclusion


CSV_PATH = "sales_data.csv"
CUTOFF_DATE = pd.Timestamp("2021-01-15")

daily_sales = load_daily_sales(CSV_PATH)
fig, conclusion_text = make_figure(daily_sales, CUTOFF_DATE)

app = dash.Dash(__name__)
app.title = "Soul Foods Pink Morsel Sales Visualiser"

app.layout = html.Div(
    style={"maxWidth": "1000px", "margin": "0 auto", "padding": "24px"},
    children=[
        html.H1("Soul Foods Pink Morsel Sales: Before vs After Price Increase"),
        dcc.Graph(figure=fig, style={"marginTop": "12px"}),
        html.P(
            conclusion_text,
            style={"fontSize": "16px", "marginTop": "12px"},
        ),
    ],
)


if __name__ == "__main__":
    # Dash dev server.
    app.run_server(debug=True, host="0.0.0.0", port=8050)

