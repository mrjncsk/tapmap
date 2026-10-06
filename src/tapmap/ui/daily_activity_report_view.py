"""Daily Activity Report view rendering for the TapMap UI."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
from dash import dcc, html

from tapmap.state.daily_report import (
    HISTORY_WINDOW_DAYS,
    MIN_APPENDIX_HISTORY_DAYS,
    DailyReportData,
)

_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Courier New', monospace"


def _build_applications_figure(
    application_counts: dict[str, int],
) -> go.Figure:
    categories = list(application_counts.keys())
    values = list(application_counts.values())

    fig = go.Figure(
        go.Bar(
            x=values,
            y=categories,
            orientation="h",
            marker_color="rgba(148,226,213,0.55)",
            marker_line_color="rgba(30,80,80,0.9)",
            marker_line_width=2,
        )
    )
    fig.update_layout(
        paper_bgcolor="#0a1628",
        plot_bgcolor="#0a192f",
        font=dict(family=_MONO, color="#94e2d5"),
        height=320,
        margin=dict(l=140, r=40, t=20, b=40),
        yaxis=dict(
            automargin=True,
            ticklabelstandoff=20,
            gridcolor="rgba(148,226,213,0.15)",
            tickcolor="#94e2d5",
            fixedrange=True,
        ),
        xaxis=dict(
            title="Number of applications",
            showgrid=True,
            gridcolor="rgba(148,226,213,0.35)",
            gridwidth=1,
            zerolinecolor="rgba(148,226,213,0.5)",
            tickcolor="#94e2d5",
            fixedrange=True,
        ),
    )
    return fig


def _build_concentration_figure(
    total_providers: int,
    cumulative_pcts: list[float],
) -> go.Figure:
    fig = go.Figure()

    if total_providers > 0:
        fig.add_trace(
            go.Scatter(
                x=list(range(1, total_providers + 1)),
                y=cumulative_pcts,
                mode="lines",
                line=dict(color="rgba(148,226,213,0.90)", width=2),
                fill="tozeroy",
                fillcolor="rgba(148,226,213,0.12)",
                hovertemplate="Top %{x} providers: %{y:.0f}%<extra></extra>",
                showlegend=False,
            )
        )

    fig.update_layout(
        paper_bgcolor="#0a1628",
        plot_bgcolor="#0a192f",
        font=dict(family=_MONO, color="#94e2d5"),
        height=220,
        margin=dict(l=60, r=20, t=10, b=50),
        showlegend=False,
        shapes=[
            dict(
                type="line",
                x0=0,
                x1=max(total_providers, 1),
                y0=80,
                y1=80,
                line=dict(color="rgba(148,226,213,0.75)", width=1.5, dash="dot"),
            )
        ],
        annotations=[
            dict(
                x=1,
                y=80,
                xref="paper",
                yref="y",
                text="80%",
                showarrow=False,
                xanchor="right",
                yanchor="bottom",
                xshift=-12,
                font=dict(size=9, color="rgba(148,226,213,0.88)", family=_MONO),
            )
        ],
        xaxis=dict(
            title=dict(text="Providers (sorted by activity)", font=dict(color="#94e2d5")),
            showgrid=True,
            gridcolor="rgba(148,226,213,0.35)",
            gridwidth=1,
            showline=True,
            linecolor="rgba(148,226,213,0.5)",
            tickcolor="#94e2d5",
            tickfont=dict(color="#94e2d5"),
            zeroline=False,
            fixedrange=True,
        ),
        yaxis=dict(
            title=dict(text="Activity covered", font=dict(color="#94e2d5")),
            range=[0, 100],
            showgrid=True,
            gridcolor="rgba(148,226,213,0.35)",
            gridwidth=1,
            showline=True,
            linecolor="rgba(148,226,213,0.5)",
            tickcolor="#94e2d5",
            tickfont=dict(color="#94e2d5"),
            zeroline=False,
            ticksuffix="%",
            fixedrange=True,
        ),
    )
    return fig


def _build_countries_figure(
    country_map_points: list[dict[str, Any]],
) -> go.Figure:
    def _scale(active_days: int) -> float:
        return 40 * (active_days / HISTORY_WINDOW_DAYS) ** 0.5

    lats = [p["lat"] for p in country_map_points]
    lons = [p["lon"] for p in country_map_points]
    days = [p["active_days"] for p in country_map_points]
    codes = [p["code"] for p in country_map_points]

    fig = go.Figure(
        go.Scattergeo(
            lat=lats,
            lon=lons,
            mode="markers",
            marker=dict(
                size=[_scale(d) for d in days],
                color="#94e2d5",
                opacity=0.75,
                line=dict(width=1.5, color="rgba(30,60,60,0.85)"),
            ),
            hovertemplate="<b>%{customdata[0]}</b>: %{customdata[1]}d<extra></extra>",
            customdata=list(zip(codes, days, strict=True)),
        )
    )
    fig.update_layout(
        paper_bgcolor="#0a1628",
        height=420,
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        geo=dict(
            bgcolor="#0a1628",
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#1a4a3a",
            showland=True,
            landcolor="#1e5a3e",
            showocean=True,
            oceancolor="#0a192f",
            showlakes=False,
            showcountries=False,
            projection_type="natural earth",
            lataxis_range=[-60, 85],
        ),
        dragmode=False,
    )
    return fig


def _render_recurrence_examples(
    recurrence_examples: list[Any],
    recurrence_labels: dict[str, str],
    history_days: int,
) -> list[Any]:
    if history_days < MIN_APPENDIX_HISTORY_DAYS:
        return [
            html.P(
                f"Recurrence grouping and patterns are shown once "
                f"{MIN_APPENDIX_HISTORY_DAYS} days of connection history are available.",
                style={
                    "fontSize": "11px",
                    "color": "rgba(148,226,213,0.55)",
                    "marginLeft": "140px",
                    "fontStyle": "italic",
                },
            )
        ]

    rows = []
    for cat, name, days in recurrence_examples:
        label_span = html.Span(
            recurrence_labels.get(cat, cat),
            className="rpt-cat-label",
        )
        if name is not None:
            detail: list[Any] = [
                html.Span(
                    name,
                    style={"color": "rgba(148,226,213,0.85)", "fontSize": "11px"},
                ),
                html.Div(
                    [
                        html.Span(
                            "\u25a0" if active else "\u25a1",
                            className="rpt-day--on" if active else "rpt-day--off",
                        )
                        for active in days
                    ],
                    className="rpt-day-strip",
                ),
            ]
        else:
            detail = [
                html.Span(
                    "no examples yet",
                    style={
                        "color": "rgba(30,120,110,0.45)",
                        "fontSize": "11px",
                        "fontStyle": "italic",
                    },
                )
            ]

        rows.append(html.Div([label_span, *detail], style={"marginBottom": "6px"}))

    return [
        html.Div(
            [
                html.P(
                    "Example recurrence patterns",
                    style={
                        "fontSize": "12px",
                        "fontWeight": "600",
                        "color": "rgba(148,226,213,0.90)",
                        "margin": "0 0 10px 0",
                        "letterSpacing": "0.02em",
                    },
                ),
                *rows,
                html.P(
                    "Each square represents one day, with today on the right. "
                    "Filled squares show days where activity was recorded.",
                    style={
                        "fontSize": "11px",
                        "color": "rgba(148,226,213,0.85)",
                        "margin": "14px 0 0 0",
                        "lineHeight": "1.35",
                    },
                ),
            ],
            className="rpt-recurrence",
        )
    ]


def render_daily_activity_report(
    report: DailyReportData,
) -> list[Any]:
    """Render the Daily Activity Report modal content from pre-computed data."""
    history_days = report["history_days"]
    concentration = report["provider_concentration"]

    applications_figure = _build_applications_figure(report["application_counts"])
    concentration_figure = _build_concentration_figure(
        concentration["total_providers"],
        concentration["cumulative_pcts"],
    )
    countries_figure = _build_countries_figure(report["country_map_points"])

    children: list[Any] = [
        html.H1("Daily Activity Report"),
        html.P(report["intro_text"]),
        html.P(report["today_text"]),
    ]

    if report["activity_pattern_text"]:
        children.append(html.P(report["activity_pattern_text"]))

    children += [
        html.H2("Applications", className="rpt-h2"),
        html.P(report["applications_summary"]),
        dcc.Graph(figure=applications_figure, config={"displayModeBar": False}),
        *_render_recurrence_examples(
            report["recurrence_examples"],
            report["recurrence_labels"],
            history_days,
        ),
        html.H2("Providers", className="rpt-h2"),
        html.P(report["providers_summary"]),
        dcc.Graph(
            figure=concentration_figure,
            config={"displayModeBar": False},
        ),
        html.H2("Countries", className="rpt-h2"),
        html.P(report["countries_summary"]),
        dcc.Graph(figure=countries_figure, config={"displayModeBar": False}),
        html.P(
            "Dot size reflects how many days each country was observed in the connection history.",
            className="modal-subtitle",
        ),
    ]

    children += [
        html.H2("Log", className="rpt-h2"),
        html.P(
            "The detailed log includes complete activity timelines for "
            "applications, providers, countries and ports."
        ),
        html.Button(
            "Open detailed log",
            id="btn_view_log",
            n_clicks=0,
            className="mx-btn mx-btn--primary mx-btn--nowrap",
            type="button",
        ),
    ]

    return children
