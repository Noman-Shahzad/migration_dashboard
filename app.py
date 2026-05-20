import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback

# ── COLOURS ──
DARK_BG   = "#0d1117"
CARD_BG   = "#161b22"
BORDER    = "#30363d"
ACCENT    = "#58a6ff"
ACCENT2   = "#f78166"
TEXT      = "#e6edf3"
MUTED     = "#8b949e"
GRID      = "#21262d"
HIGHLIGHT = "#f0e68c"
GREEN     = "#3fb950"

# ── DATA ──
df = pd.read_parquet("table1.parquet", engine="fastparquet")
df = df[
    (df["destination_code"] < 900) &
    (df["origin_code"]      < 900) &
    (df["sex"] == "both_sexes")
].copy()
df["migrant_stock"] = pd.to_numeric(df["migrant_stock"], errors="coerce")
df["year"] = df["year"].astype(int)

YEARS     = sorted(df["year"].unique())
COUNTRIES = sorted(df["destination"].dropna().unique())

# ── Unique colour per country ──
QUAL_COLORS = (
    px.colors.qualitative.Alphabet +
    px.colors.qualitative.Light24 +
    px.colors.qualitative.Dark24 +
    px.colors.qualitative.Vivid +
    px.colors.qualitative.Safe
)
COUNTRY_COLOR = {
    c: QUAL_COLORS[i % len(QUAL_COLORS)]
    for i, c in enumerate(COUNTRIES)
}

# ── Country centroids ──
CENTROIDS = {
    "Afghanistan": (33.9, 67.7), "Albania": (41.2, 20.2),
    "Algeria": (28.0, 1.7), "Angola": (11.2, 17.9),
    "Argentina": (-38.4, -63.6), "Australia": (-25.3, 133.8),
    "Austria": (47.5, 14.6), "Azerbaijan": (40.1, 47.6),
    "Bangladesh": (23.7, 90.4), "Belarus": (53.7, 28.0),
    "Belgium": (50.5, 4.5), "Brazil": (-14.2, -51.9),
    "Bulgaria": (42.7, 25.5), "Cambodia": (12.6, 104.9),
    "Cameroon": (3.8, 11.5), "Canada": (56.1, -106.3),
    "Chile": (-35.7, -71.5), "China": (35.9, 104.2),
    "China, Hong Kong SAR": (22.3, 114.2),
    "Colombia": (4.6, -74.3), "Croatia": (45.1, 15.2),
    "Cuba": (21.5, -79.0), "Czech Republic": (49.8, 15.5),
    "Denmark": (56.3, 9.5), "Ecuador": (-1.8, -78.2),
    "Egypt": (26.8, 30.8), "Ethiopia": (9.1, 40.5),
    "Finland": (61.9, 25.7), "France": (46.2, 2.2),
    "Germany": (51.2, 10.5), "Ghana": (8.0, -1.0),
    "Greece": (39.1, 21.8), "Hungary": (47.2, 19.5),
    "India": (20.6, 78.9), "Indonesia": (-0.8, 113.9),
    "Iran (Islamic Republic of)": (32.4, 53.7),
    "Iraq": (33.2, 43.7), "Ireland": (53.4, -8.2),
    "Israel": (31.0, 34.9), "Italy": (41.9, 12.6),
    "Japan": (36.2, 138.3), "Jordan": (30.6, 36.2),
    "Kazakhstan": (48.0, 66.9), "Kenya": (-0.0, 37.9),
    "Kuwait": (29.3, 47.5), "Lebanon": (33.9, 35.9),
    "Libya": (26.3, 17.2), "Malaysia": (4.2, 101.9),
    "Mexico": (23.6, -102.6), "Morocco": (31.8, -7.1),
    "Mozambique": (-18.7, 35.5), "Myanmar": (16.9, 96.1),
    "Nepal": (28.4, 84.1), "Netherlands": (52.1, 5.3),
    "New Zealand": (-40.9, 174.9), "Nigeria": (9.1, 8.7),
    "Norway": (60.5, 8.5), "Pakistan": (30.4, 69.3),
    "Peru": (-9.2, -75.0), "Philippines": (12.9, 121.8),
    "Poland": (51.9, 19.1), "Portugal": (39.4, -8.2),
    "Qatar": (25.4, 51.2), "Romania": (45.9, 24.9),
    "Russian Federation": (61.5, 105.3),
    "Saudi Arabia": (23.9, 45.1), "Senegal": (14.5, -14.5),
    "Serbia": (44.0, 21.0), "Somalia": (5.2, 46.2),
    "South Africa": (-30.6, 22.9), "South Sudan": (7.9, 29.7),
    "Spain": (40.5, -3.7), "Sri Lanka": (7.9, 80.8),
    "Sudan": (12.9, 30.2), "Sweden": (60.1, 18.6),
    "Switzerland": (46.8, 8.2),
    "Syrian Arab Republic": (34.8, 38.9),
    "Thailand": (15.9, 101.0), "Tunisia": (33.9, 9.5),
    "Türkiye": (38.9, 35.2), "Uganda": (1.4, 32.3),
    "Ukraine": (48.4, 31.2),
    "United Arab Emirates": (23.4, 53.8),
    "United Kingdom": (55.4, -3.4),
    "United States of America": (37.1, -95.7),
    "Uruguay": (-32.5, -55.8),
    "Venezuela (Bolivarian Republic of)": (6.4, -66.6),
    "Viet Nam": (14.1, 108.3), "Yemen": (15.6, 48.5),
    "Zambia": (-13.1, 27.8), "Zimbabwe": (-19.0, 29.2),
}

def shorten(name):
    return (name
        .replace("United States of America", "USA")
        .replace("United Kingdom", "UK")
        .replace("Russian Federation", "Russia")
        .replace("Syrian Arab Republic", "Syria")
        .replace("Venezuela (Bolivarian Republic of)", "Venezuela")
        .replace("Iran (Islamic Republic of)", "Iran")
        .replace("China, Hong Kong SAR", "HK")
        .replace("Viet Nam", "Vietnam")
        .replace("Türkiye", "Turkey"))

def btn_style(active, color):
    if active:
        return dict(
            background=color, color=DARK_BG,
            border="none", borderRadius="4px",
            padding="3px 8px", cursor="pointer",
            fontSize="9px", fontWeight="700",
            fontFamily="monospace",
        )
    return dict(
        background=CARD_BG, color=color,
        border=f"1px solid {color}",
        borderRadius="4px", padding="3px 8px",
        cursor="pointer", fontSize="9px",
        fontWeight="700", fontFamily="monospace",
    )

# ── APP ──
app = Dash(__name__, suppress_callback_exceptions=True)

app.index_string = '''
<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>Migration Flows Dashboard</title>
{%favicon%}
{%css%}
<style>
  /* ── Dropdown dark theme ── */
  .Select-control {
    background-color: #0d1117 !important;
    border-color: #30363d !important;
    color: #e6edf3 !important;
    border-radius: 4px !important;
    min-height: 28px !important;
  }
  .Select-input, .Select-input input {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
    font-family: monospace !important;
    font-size: 10px !important;
  }
  .Select-value, .Select-value-label {
    color: #e6edf3 !important;
    background-color: #0d1117 !important;
    line-height: 28px !important;
  }
  .Select-single-value {
    color: #e6edf3 !important;
    background-color: #0d1117 !important;
  }
  .Select-placeholder {
    color: #8b949e !important;
    background-color: #0d1117 !important;
    line-height: 28px !important;
  }
  .Select-arrow-zone {
    background-color: #0d1117 !important;
  }
  .Select-arrow {
    border-top-color: #8b949e !important;
  }
  .Select-clear-zone {
    background-color: #0d1117 !important;
    color: #8b949e !important;
  }
  .Select-menu-outer {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    z-index: 9999 !important;
    margin-top: 2px !important;
    border-radius: 4px !important;
  }
  .Select-menu {
    background-color: #161b22 !important;
    max-height: 200px !important;
  }
  .Select-option {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
    font-size: 10px !important;
    font-family: monospace !important;
    padding: 6px 10px !important;
    cursor: pointer !important;
  }
  .Select-option:hover,
  .Select-option.is-focused {
    background-color: #21262d !important;
    color: #58a6ff !important;
  }
  .Select-option.is-selected {
    background-color: #1f4e8c !important;
    color: #ffffff !important;
  }
  .VirtualizedSelectOption {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
    font-size: 10px !important;
    font-family: monospace !important;
  }
  .VirtualizedSelectFocusedOption {
    background-color: #21262d !important;
    color: #58a6ff !important;
  }
  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: #0d1117; }
  ::-webkit-scrollbar-thumb {
    background: #30363d;
    border-radius: 2px;
  }
</style>
{%scripts%}
</head>
<body>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>
'''

# ── Dropdown options ──
COUNTRY_OPTIONS = [{"label": c, "value": c} for c in COUNTRIES]

app.layout = html.Div(style=dict(
    background=DARK_BG,
    height="100vh",
    width="100vw",
    overflow="hidden",
    display="flex",
    flexDirection="column",
    fontFamily="monospace",
    color=TEXT,
    boxSizing="border-box",
), children=[

    dcc.Store(id="selected-country", data=None),
    dcc.Store(id="bar-mode", data="receivers"),

    # ── TOP NAV BAR ──
    html.Div(style=dict(
        background=CARD_BG,
        borderBottom=f"1px solid {BORDER}",
        padding="5px 16px",
        display="flex",
        justifyContent="space-between",
        alignItems="center",
        flexShrink="0",
    ), children=[
        html.Div(style=dict(
            display="flex", flexDirection="column", gap="1px"
        ), children=[
            html.Div("◈ MIGRATION FLOWS DASHBOARD", style=dict(
                fontSize="13px", fontWeight="700",
                letterSpacing="3px", color=TEXT,
            )),
            html.Div("Noman Shahzad · Visiliki · Stephan",
                     style=dict(fontSize="9px", color=MUTED,
                                letterSpacing="1px")),
        ]),
        html.Div(id="stat-cards", style=dict(
            display="flex", gap="10px", alignItems="center",
        )),
        html.Div("UN IMS · 1990–2024 · 233 Countries",
                 style=dict(fontSize="10px", color=MUTED)),
    ]),

    # ── MAIN BODY ──
    html.Div(style=dict(
        display="flex", flex="1",
        overflow="hidden", gap="6px", padding="6px",
    ), children=[

        # ── SIDEBAR ──
        html.Div(style=dict(
            width="170px", minWidth="170px",
            background=CARD_BG,
            border=f"1px solid {BORDER}",
            borderRadius="6px",
            padding="12px 10px",
            display="flex", flexDirection="column",
            gap="10px", flexShrink="0", overflowY="auto",
        ), children=[

            html.Div("FILTERS", style=dict(
                color=TEXT, fontSize="9px",
                letterSpacing="2px",
                borderBottom=f"1px solid {BORDER}",
                paddingBottom="6px", fontWeight="700",
            )),

            # Year slider
            html.Div([
                html.Label("Year", style=dict(
                    color=TEXT, fontSize="11px",
                    fontWeight="600", marginBottom="4px",
                    display="block",
                )),
                dcc.Slider(
                    id="year-slider",
                    min=YEARS[0], max=YEARS[-1], step=None,
                    marks={int(y): dict(
                        label=str(y),
                        style=dict(fontSize="10px",
                                   color=TEXT,
                                   fontWeight="600")
                    ) for y in YEARS},
                    value=2024,
                    tooltip=dict(placement="right",
                                 always_visible=False),
                    vertical=True, verticalHeight=180,
                ),
            ]),

            # Top N slider
            html.Div([
                html.Label("Top N", style=dict(
                    color=TEXT, fontSize="11px",
                    fontWeight="600", marginBottom="4px",
                    display="block",
                )),
                dcc.Slider(
                    id="topn-slider",
                    min=5, max=20, step=5,
                    marks={i: dict(
                        label=str(i),
                        style=dict(fontSize="10px",
                                   color=TEXT,
                                   fontWeight="600")
                    ) for i in [5, 10, 15, 20]},
                    value=10,
                    tooltip=dict(placement="right",
                                 always_visible=False),
                    vertical=True, verticalHeight=80,
                ),
            ]),

            # Country filter section
            html.Div("COUNTRY FILTER", style=dict(
                color=TEXT, fontSize="9px",
                letterSpacing="2px",
                borderBottom=f"1px solid {BORDER}",
                paddingBottom="6px", fontWeight="700",
                marginTop="4px",
            )),

            # Receiver dropdown
            html.Div([
                html.Label("🟢 Receiver", style=dict(
                    color=GREEN, fontSize="10px",
                    fontWeight="700", marginBottom="4px",
                    display="block",
                )),
                dcc.Dropdown(
                    id="recv-filter",
                    options=COUNTRY_OPTIONS,
                    value=None,
                    placeholder="All receivers...",
                    clearable=True,
                    style=dict(
                        backgroundColor=DARK_BG,
                        fontSize="10px",
                    ),
                    className="dark-dd",
                ),
            ]),

            # Sender dropdown
            html.Div([
                html.Label("🟠 Sender", style=dict(
                    color=ACCENT2, fontSize="10px",
                    fontWeight="700", marginBottom="4px",
                    display="block",
                )),
                dcc.Dropdown(
                    id="send-filter",
                    options=COUNTRY_OPTIONS,
                    value=None,
                    placeholder="All senders...",
                    clearable=True,
                    style=dict(
                        backgroundColor=DARK_BG,
                        fontSize="10px",
                    ),
                    className="dark-dd",
                ),
            ]),

            # Reset button
            html.Button(
                "⟳ Reset All", id="reset-btn", n_clicks=0,
                style=dict(
                    background=DARK_BG, color=ACCENT,
                    border=f"1px solid {ACCENT}",
                    borderRadius="4px", padding="6px 10px",
                    cursor="pointer", fontSize="11px",
                    marginTop="4px", width="100%",
                ),
            ),

            html.Div(id="selected-label", style=dict(
                color=ACCENT2, fontSize="9px",
                textAlign="center", wordBreak="break-word",
                marginTop="4px",
            )),

        ]),

        # ── CENTRE ──
        html.Div(style=dict(
            display="flex", flexDirection="column",
            gap="6px", overflow="hidden",
            width="42%", flexShrink="0",
        ), children=[

            # Sankey
            html.Div(style=dict(
                flex="2", background=CARD_BG,
                border=f"1px solid {BORDER}",
                borderRadius="6px", padding="8px",
                display="flex", flexDirection="column",
                overflow="hidden",
            ), children=[
                html.Div("🔀 ORIGIN → DESTINATION FLOWS",
                         style=dict(color=MUTED, fontSize="9px",
                                    letterSpacing="1px",
                                    marginBottom="4px")),
                dcc.Graph(id="sankey",
                          style=dict(flex="1", minHeight="0"),
                          config=dict(displayModeBar=False)),
            ]),

            # Bar + Donut row
            html.Div(style=dict(
                flex="1", display="flex",
                gap="6px", overflow="hidden",
            ), children=[

                # Bar card
                html.Div(style=dict(
                    flex="3", background=CARD_BG,
                    border=f"1px solid {BORDER}",
                    borderRadius="6px", padding="8px",
                    display="flex", flexDirection="column",
                    overflow="hidden",
                ), children=[
                    # Header row with title + toggle buttons
                    html.Div(style=dict(
                        display="flex",
                        justifyContent="space-between",
                        alignItems="center",
                        marginBottom="6px",
                    ), children=[
                        html.Div("🏆 TOP 5 SENDERS & RECEIVERS",
                                 style=dict(color=MUTED,
                                            fontSize="9px",
                                            letterSpacing="1px")),
                        html.Div(style=dict(
                            display="flex", gap="4px",
                        ), children=[
                            html.Button(
                                "🟢 Receivers",
                                id="btn-recv", n_clicks=0,
                                style=btn_style(True, GREEN),
                            ),
                            html.Button(
                                "🟠 Senders",
                                id="btn-send", n_clicks=0,
                                style=btn_style(False, ACCENT2),
                            ),
                        ]),
                    ]),
                    dcc.Graph(id="bar-compare",
                              style=dict(flex="1", minHeight="0"),
                              config=dict(displayModeBar=False)),
                ]),

                # Donut
                html.Div(style=dict(
                    flex="2", background=CARD_BG,
                    border=f"1px solid {BORDER}",
                    borderRadius="6px", padding="8px",
                    display="flex", flexDirection="column",
                    overflow="hidden",
                ), children=[
                    html.Div("🍩 TOP 5 SHARE (%)",
                             style=dict(color=MUTED, fontSize="9px",
                                        letterSpacing="1px",
                                        marginBottom="4px")),
                    dcc.Graph(id="donut",
                              style=dict(flex="1", minHeight="0"),
                              config=dict(displayModeBar=False)),
                ]),

            ]),

        ]),

        # ── RIGHT: Map + Time Series ──
        html.Div(style=dict(
            flex="1", display="flex",
            flexDirection="column", gap="6px",
            overflow="hidden",
        ), children=[

            # Map
            html.Div(style=dict(
                flex="3", background=CARD_BG,
                border=f"1px solid {BORDER}",
                borderRadius="6px", padding="8px",
                display="flex", flexDirection="column",
                overflow="hidden",
            ), children=[
                html.Div(
                    "🌍 GLOBAL MIGRANT STOCK · click country to filter",
                    style=dict(color=MUTED, fontSize="9px",
                               letterSpacing="1px",
                               marginBottom="4px")),
                dcc.Graph(id="choropleth",
                          style=dict(flex="1", minHeight="0"),
                          config=dict(displayModeBar=False)),
            ]),

            # Time series
            html.Div(style=dict(
                flex="2", background=CARD_BG,
                border=f"1px solid {BORDER}",
                borderRadius="6px", padding="8px",
                display="flex", flexDirection="column",
                overflow="hidden",
            ), children=[
                html.Div("📈 MIGRANT STOCK TRENDS",
                         style=dict(color=MUTED, fontSize="9px",
                                    letterSpacing="1px",
                                    marginBottom="4px")),
                dcc.Graph(id="time-series",
                          style=dict(flex="1", minHeight="0"),
                          config=dict(displayModeBar=False)),
            ]),

        ]),

    ]),

])

# ── CALLBACKS ──

@callback(
    Output("bar-mode", "data"),
    Output("btn-recv", "style"),
    Output("btn-send", "style"),
    Input("btn-recv",  "n_clicks"),
    Input("btn-send",  "n_clicks"),
)
def toggle_bar_mode(r_clicks, s_clicks):
    from dash import ctx
    trigger = ctx.triggered_id
    if trigger == "btn-send":
        return (
            "senders",
            btn_style(False, GREEN),
            btn_style(True,  ACCENT2),
        )
    return (
        "receivers",
        btn_style(True,  GREEN),
        btn_style(False, ACCENT2),
    )


@callback(
    Output("selected-country", "data"),
    Input("choropleth",  "clickData"),
    Input("bar-compare", "clickData"),
    Input("reset-btn",   "n_clicks"),
    State("selected-country", "data"),
)
def update_selected(map_click, bar_click, reset, current):
    from dash import ctx
    trigger = ctx.triggered_id
    if trigger == "reset-btn":
        return None
    if trigger == "choropleth" and map_click:
        pts     = map_click["points"][0]
        country = pts.get("location") or pts.get("text")
        return None if country == current else country
    if trigger == "bar-compare" and bar_click:
        country = bar_click["points"][0].get("y")
        return None if country == current else country
    return current


@callback(
    Output("selected-label", "children"),
    Input("selected-country", "data"),
)
def update_label(country):
    if not country:
        return "Click chart to filter"
    return f"● {country}"


@callback(
    Output("stat-cards", "children"),
    Input("year-slider",      "value"),
    Input("selected-country", "data"),
)
def update_stats(year, country):
    yr = df[df["year"] == year]
    if country:
        total = yr[yr["destination"] == country]["migrant_stock"].sum()
        sent  = yr[yr["origin"] == country]["migrant_stock"].sum()
        recv  = f"{total/1e6:.1f}M received"
        send  = f"{sent/1e6:.1f}M sent"
        label = country[:16]
    else:
        total = yr.groupby("destination")["migrant_stock"].sum().sum()
        recv  = yr.groupby("destination")["migrant_stock"].sum().idxmax()
        send  = yr.groupby("origin")["migrant_stock"].sum().idxmax()
        label = f"{total/1e6:.0f}M total"

    def pill(text, color):
        return html.Div(text, style=dict(
            background=DARK_BG,
            border=f"1px solid {color}",
            borderRadius="4px",
            padding="4px 10px",
            fontSize="11px",
            color=color,
            whiteSpace="nowrap",
        ))

    return [
        pill(label, ACCENT),
        pill(recv,  GREEN),
        pill(send,  ACCENT2),
    ]


@callback(
    Output("choropleth", "figure"),
    Input("year-slider",      "value"),
    Input("selected-country", "data"),
)
def update_choropleth(year, selected):
    agg = (
        df[df["year"] == year]
        .groupby("destination", as_index=False)["migrant_stock"].sum()
        .dropna()
    )
    max_val = agg["migrant_stock"].max()
    traces  = []

    for _, row in agg.iterrows():
        country = row["destination"]
        val     = row["migrant_stock"]
        is_sel  = selected and country == selected
        opacity = 1.0 if not selected or is_sel else 0.2
        color   = HIGHLIGHT if is_sel else COUNTRY_COLOR.get(
            country, ACCENT)
        traces.append(go.Choropleth(
            locations=[country],
            locationmode="country names",
            z=[val], zmin=0, zmax=max_val,
            colorscale=[[0, color], [1, color]],
            showscale=False, showlegend=False,
            marker=dict(
                opacity=opacity,
                line=dict(
                    color=HIGHLIGHT if is_sel else BORDER,
                    width=2 if is_sel else 0.3,
                ),
            ),
            hovertemplate=(
                f"<b>{country}</b><br>"
                f"Migrants: {val:,.0f}<extra></extra>"
            ),
        ))

    # Country name labels
    lats, lons, texts = [], [], []
    for _, row in agg.iterrows():
        c = row["destination"]
        if c in CENTROIDS:
            lat, lon = CENTROIDS[c]
            lats.append(lat)
            lons.append(lon)
            texts.append(shorten(c))

    traces.append(go.Scattergeo(
        lat=lats, lon=lons, text=texts, mode="text",
        textfont=dict(size=7, color="white",
                      family="monospace"),
        hoverinfo="skip", showlegend=False,
    ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, size=10),
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            showland=True, landcolor="#1a2332",
            showocean=True, oceancolor="#0d1117",
            showcountries=True, countrycolor="#30363d",
            bgcolor="rgba(0,0,0,0)",
            projection_type="equirectangular",
            showframe=False,
            lataxis=dict(range=[-60, 85]),
            lonaxis=dict(range=[-180, 180]),
        ),
    )
    return fig


@callback(
    Output("sankey", "figure"),
    Input("year-slider",      "value"),
    Input("topn-slider",      "value"),
    Input("selected-country", "data"),
    Input("recv-filter",      "value"),
    Input("send-filter",      "value"),
)
def update_sankey(year, top_n, selected, recv_f, send_f):
    subset = df[df["year"] == year].dropna(
        subset=["migrant_stock"])
    if selected:
        subset = subset[
            (subset["origin"] == selected) |
            (subset["destination"] == selected)
        ]
    if recv_f:
        subset = subset[subset["destination"] == recv_f]
    if send_f:
        subset = subset[subset["origin"] == send_f]

    flows = (
        subset.sort_values("migrant_stock", ascending=False)
        .head(top_n)[["origin", "destination", "migrant_stock"]]
    )

    if flows.empty:
        return go.Figure(layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT),
        ))

    nodes     = list(pd.unique(
        flows[["origin", "destination"]].values.ravel()
    ))
    idx       = {n: i for i, n in enumerate(nodes)}
    node_cols = [COUNTRY_COLOR.get(n, ACCENT) for n in nodes]

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=6, thickness=12,
            line=dict(color=BORDER, width=0.5),
            label=nodes, color=node_cols,
            hovertemplate="%{label}<extra></extra>",
        ),
        link=dict(
            source=flows["origin"].map(idx),
            target=flows["destination"].map(idx),
            value=flows["migrant_stock"],
            color="rgba(88,166,255,0.18)",
            hovertemplate=(
                "%{source.label}→%{target.label}"
                "<br>%{value:,.0f}<extra></extra>"
            ),
        ),
        textfont=dict(color=TEXT, size=8),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT),
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig


@callback(
    Output("bar-compare", "figure"),
    Input("year-slider",      "value"),
    Input("selected-country", "data"),
    Input("recv-filter",      "value"),
    Input("send-filter",      "value"),
    Input("bar-mode",         "data"),
)
def update_bar(year, selected, recv_f, send_f, mode):
    n  = 5
    yr = df[df["year"] == year]

    if mode == "receivers":
        src = yr.copy()
        if recv_f:
            src = src[src["destination"] == recv_f]
        data = (
            src.groupby("destination")["migrant_stock"].sum()
            .nlargest(n).reset_index()
            .rename(columns={"destination": "country",
                             "migrant_stock": "value"})
        )
        bar_color_base = GREEN
    else:
        src = yr.copy()
        if send_f:
            src = src[src["origin"] == send_f]
        data = (
            src.groupby("origin")["migrant_stock"].sum()
            .nlargest(n).reset_index()
            .rename(columns={"origin": "country",
                             "migrant_stock": "value"})
        )
        bar_color_base = ACCENT2

    data["short"] = data["country"].apply(shorten)
    colors    = [
        HIGHLIGHT if selected and c == selected
        else COUNTRY_COLOR.get(c, bar_color_base)
        for c in data["country"]
    ]
    opacities = [
        1.0 if not selected or c == selected else 0.35
        for c in data["country"]
    ]

    fig = go.Figure(go.Bar(
        y=data["short"],
        x=data["value"],
        orientation="h",
        marker=dict(
            color=colors, opacity=opacities,
            line=dict(color=bar_color_base, width=1),
        ),
        text=data["value"].apply(lambda v: f"{v/1e6:.1f}M"),
        textposition="outside",
        textfont=dict(color=TEXT, size=10,
                      family="monospace"),
        hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT),
        xaxis=dict(
            tickformat=",.0f", gridcolor=GRID,
            tickfont=dict(size=8, color=MUTED),
            range=[0, data["value"].max() * 1.35],
        ),
        yaxis=dict(
            gridcolor=GRID, autorange="reversed",
            tickfont=dict(color=TEXT, size=9),
        ),
        margin=dict(l=0, r=60, t=4, b=0),
        showlegend=False,
        bargap=0.25,
    )
    return fig


@callback(
    Output("donut", "figure"),
    Input("year-slider",      "value"),
    Input("selected-country", "data"),
    Input("recv-filter",      "value"),
    Input("send-filter",      "value"),
)
def update_donut(year, selected, recv_f, send_f):
    yr = df[df["year"] == year]

    if recv_f:
        agg = (
            yr[yr["destination"] == recv_f]
            .groupby("origin")["migrant_stock"].sum()
            .nlargest(5).reset_index()
            .rename(columns={"origin": "country",
                             "migrant_stock": "value"})
        )
        title = f"Into {recv_f[:10]}"
    elif send_f:
        agg = (
            yr[yr["origin"] == send_f]
            .groupby("destination")["migrant_stock"].sum()
            .nlargest(5).reset_index()
            .rename(columns={"destination": "country",
                             "migrant_stock": "value"})
        )
        title = f"From {send_f[:10]}"
    elif selected:
        agg = (
            yr[yr["destination"] == selected]
            .groupby("origin")["migrant_stock"].sum()
            .nlargest(5).reset_index()
            .rename(columns={"origin": "country",
                             "migrant_stock": "value"})
        )
        title = f"Into {selected[:10]}"
    else:
        agg = (
            yr.groupby("destination")["migrant_stock"].sum()
            .nlargest(5).reset_index()
            .rename(columns={"destination": "country",
                             "migrant_stock": "value"})
        )
        title = "Top 5 Receivers"

    total  = agg["value"].sum()
    labels = agg["country"].apply(shorten)
    colors = [COUNTRY_COLOR.get(c, ACCENT)
              for c in agg["country"]]

    fig = go.Figure(go.Pie(
        labels=labels, values=agg["value"], hole=0.55,
        marker=dict(colors=colors,
                    line=dict(color=DARK_BG, width=1)),
        textinfo="percent",
        textfont=dict(size=9, color=TEXT),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "%{value:,.0f} migrants<br>"
            "%{percent}<extra></extra>"
        ),
        direction="clockwise", sort=True,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, size=9),
        margin=dict(l=0, r=0, t=24, b=0),
        title=dict(
            text=title,
            font=dict(color=MUTED, size=9),
            x=0.5, xanchor="center",
        ),
        legend=dict(
            font=dict(color=TEXT, size=7),
            bgcolor="rgba(0,0,0,0)",
            orientation="v",
            x=1.0, y=0.5,
        ),
        annotations=[dict(
            text=f"{total/1e6:.1f}M",
            x=0.5, y=0.5,
            font=dict(size=12, color=ACCENT,
                      family="monospace"),
            showarrow=False,
        )],
    )
    return fig


@callback(
    Output("time-series", "figure"),
    Input("year-slider",      "value"),
    Input("selected-country", "data"),
    Input("recv-filter",      "value"),
    Input("send-filter",      "value"),
)
def update_timeseries(year, selected, recv_f, send_f):
    if recv_f:
        countries = [recv_f]
    elif send_f:
        countries = (
            df[df["origin"] == send_f]
            .groupby("destination")["migrant_stock"].sum()
            .nlargest(4).index.tolist()
        )
    elif selected:
        countries = [selected]
    else:
        countries = (
            df[df["year"] == year]
            .groupby("destination")["migrant_stock"].sum()
            .nlargest(5).index.tolist()
        )

    agg = (
        df[df["destination"].isin(countries)]
        .groupby(["destination", "year"], as_index=False)
        ["migrant_stock"].sum()
        .dropna()
    )
    colors = [COUNTRY_COLOR.get(c, ACCENT) for c in countries]

    fig = px.line(
        agg, x="year", y="migrant_stock",
        color="destination", markers=True,
        labels={"migrant_stock": "Migrants",
                "year": "", "destination": ""},
        color_discrete_sequence=colors,
    )
    fig.update_traces(line=dict(width=2), marker=dict(size=4))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, size=9),
        xaxis=dict(gridcolor=GRID, tickvals=YEARS,
                   tickfont=dict(size=8)),
        yaxis=dict(gridcolor=GRID, tickformat=",.0f",
                   tickfont=dict(size=8)),
        legend=dict(bgcolor="rgba(0,0,0,0)",
                    font=dict(size=8)),
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)