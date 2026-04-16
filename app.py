from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

import dash
from dash import dcc, html
from dash.dependencies import Input, Output


def load_sales_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    return df


def daily_sales_for_region(df: pd.DataFrame, region: str) -> pd.DataFrame:
    if region != "all":
        df = df[df["Region"] == region]

    # Aggregate to answer "were sales higher" on each day in the selected region.
    daily = (
        df.groupby("Date", as_index=False)["Sales"]
        .sum()
        .sort_values("Date")
        .reset_index(drop=True)
    )
    return daily


def make_figure(
    daily: pd.DataFrame, cutoff: pd.Timestamp, *, region_label: str
) -> tuple[go.Figure, str]:
    before = daily[daily["Date"] < cutoff]
    after = daily[daily["Date"] >= cutoff]

    before_avg = float(before["Sales"].mean()) if not before.empty else float("nan")
    after_avg = float(after["Sales"].mean()) if not after.empty else float("nan")

    if after_avg > before_avg:
        conclusion = (
            f"Region: {region_label}. Average daily sales are higher after the price "
            f"increase on 15 Jan 2021 ({after_avg:.2f} vs {before_avg:.2f})."
        )
    else:
        conclusion = (
            f"Region: {region_label}. Average daily sales are higher before the price "
            f"increase on 15 Jan 2021 ({before_avg:.2f} vs {after_avg:.2f})."
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


CSV_PATH = Path(__file__).resolve().parent / "sales_data.csv"
CUTOFF_DATE = pd.Timestamp("2021-01-15")

sales_df = load_sales_data(str(CSV_PATH))

initial_daily = daily_sales_for_region(sales_df, "all")
fig, conclusion_text = make_figure(initial_daily, CUTOFF_DATE, region_label="All regions")

app = dash.Dash(__name__)
app.title = "Soul Foods Pink Morsel Sales Visualiser"

page_style = {
    "minHeight": "100vh",
    "background": "linear-gradient(180deg, #f4f7ff 0%, #ffffff 70%)",
    "padding": "24px 0",
}

card_style = {
    "maxWidth": "1100px",
    "margin": "0 auto",
    "padding": "22px",
    "background": "white",
    "borderRadius": "14px",
    "boxShadow": "0 10px 30px rgba(20, 40, 90, 0.08)",
    "border": "1px solid rgba(15, 23, 42, 0.06)",
}

header_style = {
    "fontFamily": "Arial, Helvetica, sans-serif",
    "fontSize": "26px",
    "marginBottom": "8px",
    "color": "#0f172a",
}

subheader_style = {"marginTop": 0, "color": "#475569"}

radio_container_style = {
    "padding": "14px 16px",
    "borderRadius": "12px",
    "background": "#f8fafc",
    "border": "1px solid rgba(15, 23, 42, 0.06)",
    "marginTop": "14px",
}

radio_style = {"marginLeft": "6px", "marginTop": "4px"}

graph_wrap_style = {
    "marginTop": "16px",
    "padding": "14px",
    "borderRadius": "12px",
    "background": "#ffffff",
    "border": "1px solid rgba(15, 23, 42, 0.06)",
}

conclusion_style = {
    "marginTop": "14px",
    "fontSize": "16px",
    "color": "#0f172a",
    "padding": "12px 14px",
    "borderRadius": "12px",
    "background": "rgba(2, 132, 199, 0.06)",
    "border": "1px solid rgba(2, 132, 199, 0.18)",
}

app.layout = html.Div(
    children=[
        html.Div(
            style=page_style,
            children=[
                html.Div(
                    style=card_style,
                    children=[
                        html.H1(
                            "Soul Foods Pink Morsel Sales Visualiser",
                            id="app-header",
                            style=header_style,
                        ),
                        html.P(
                            "Explore total daily sales and compare before vs after the "
                            "15 Jan 2021 Pink Morsel price increase.",
                            style=subheader_style,
                        ),
                        html.Div(
                            style=radio_container_style,
                            children=[
                                html.Div(
                                    "Filter by region:",
                                    style={"fontWeight": "600", "color": "#0f172a"},
                                ),
                                dcc.RadioItems(
                                    id="region-radio",
                                    options=[
                                        {"label": "north", "value": "north"},
                                        {"label": "east", "value": "east"},
                                        {"label": "south", "value": "south"},
                                        {"label": "west", "value": "west"},
                                        {"label": "all", "value": "all"},
                                    ],
                                    value="all",
                                    labelStyle=radio_style,
                                    inputStyle={"marginRight": "8px"},
                                ),
                            ],
                        ),
                        html.Div(style=graph_wrap_style, children=[
                            dcc.Graph(
                                id="sales-graph",
                                figure=fig,
                                config={"displayModeBar": False},
                            )
                        ]),
                        html.P(id="conclusion-text", children=conclusion_text, style=conclusion_style),
                    ],
                ),
            ],
        )
    ],
)

@app.callback(
    Output("sales-graph", "figure"),
    Output("conclusion-text", "children"),
    Input("region-radio", "value"),
)
def update_visualisation(region: str) -> tuple[go.Figure, str]:
    daily = daily_sales_for_region(sales_df, region)
    region_label = region if region != "all" else "All regions"
    return make_figure(daily, CUTOFF_DATE, region_label=region_label)


if __name__ == "__main__":
    # Dash dev server.
    app.run(debug=True, host="0.0.0.0", port=8050)

