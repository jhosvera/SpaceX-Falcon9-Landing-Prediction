"""Tablero interactivo con Plotly Dash – lanzamientos de SpaceX.

Ejecutar:  python dash_app/spacex_dash_app.py   y abrir http://127.0.0.1:8050
"""
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
spacex_df = pd.read_csv(URL)
min_payload = spacex_df["Payload Mass (kg)"].min()
max_payload = spacex_df["Payload Mass (kg)"].max()

app = Dash(__name__)

site_options = [{"label": "Todos los sitios", "value": "ALL"}] + [
    {"label": s, "value": s} for s in sorted(spacex_df["Launch Site"].unique())
]

app.layout = html.Div([
    html.H1("Panel de lanzamientos de SpaceX", style={"textAlign": "center"}),
    dcc.Dropdown(id="site-dropdown", options=site_options, value="ALL",
                 placeholder="Selecciona un sitio de lanzamiento", searchable=True),
    html.Br(),
    dcc.Graph(id="success-pie-chart"),
    html.P("Rango de masa de carga útil (kg):"),
    dcc.RangeSlider(id="payload-slider", min=0, max=10000, step=1000,
                    marks={i: str(i) for i in range(0, 10001, 2500)},
                    value=[min_payload, max_payload]),
    dcc.Graph(id="success-payload-scatter-chart"),
])


@app.callback(Output("success-pie-chart", "figure"), Input("site-dropdown", "value"))
def update_pie(site):
    if site == "ALL":
        data = spacex_df[spacex_df["class"] == 1]
        return px.pie(data, names="Launch Site", title="Aterrizajes exitosos por sitio")
    filtered = spacex_df[spacex_df["Launch Site"] == site]
    counts = filtered["class"].value_counts().rename_axis("class").reset_index(name="count")
    counts["Resultado"] = counts["class"].map({1: "Exitoso", 0: "Fallido"})
    return px.pie(counts, values="count", names="Resultado", title=f"Resultados en {site}")


@app.callback(Output("success-payload-scatter-chart", "figure"),
              [Input("site-dropdown", "value"), Input("payload-slider", "value")])
def update_scatter(site, payload_range):
    low, high = payload_range
    data = spacex_df[spacex_df["Payload Mass (kg)"].between(low, high)]
    if site != "ALL":
        data = data[data["Launch Site"] == site]
    title = "Carga útil vs. resultado – " + ("todos los sitios" if site == "ALL" else site)
    return px.scatter(data, x="Payload Mass (kg)", y="class", color="Booster Version Category", title=title)


if __name__ == "__main__":
    app.run(debug=True)
