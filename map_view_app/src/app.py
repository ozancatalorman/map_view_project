from dash import Dash, dcc, html, Input, Output
from sqlalchemy import create_engine
import geopandas as gpd
import pandas as pd
import plotly.express as px
from monday_locations import get_monday_locations

# Map of funnel stage to display colour
cmap = {'Engaged':   'rgb(253, 171, 61)',
        'Enrolled':  'rgb(255, 100, 46)',
        'Matched':   'rgb(156, 211, 38)',
        'Activated': 'rgb(3, 127, 76)',
        'Lead':      'rgb(196, 196, 196)',
        'Contact':   'rgb(255, 203, 0)',
        'Churned':   'rgb(223, 47, 74)'}

# Read the geospatial data from the
g = gpd.read_parquet('na_eu_geo.parquet').set_index('name')

# Fetching the monday location data and maping the stages with colors
monday_locations = get_monday_locations("1431777117")
monday_locations['colour'] = monday_locations['stage'].map(cmap)

options = sorted(list(g['msa'].unique()))

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Geoscore and locations by MSA'),
    html.P('Select MSA'),
    dcc.Dropdown(
        id='msa',
        options=options,
        value=None
    ),
    dcc.Graph(id='graph'),
])

@app.callback(
    Output("graph", "figure"),
    Input("msa", "value"))
def create_plot(msa):
    if msa == '-- Select MSA --':
        return None
    g2 = g[g['msa'] == msa]
    min_lon, min_lat, max_lon, max_lat = g2['geom'].envelope.unary_union.envelope.bounds
    mx = max(max_lat - min_lat, max_lon - min_lon)
    # Set zoom level based on lat/lon range
    zoom = 8 if mx > 0.5 else 9
    # Filter locations
    rx = r[(r['lon'] > min_lon) & (r['lat'] > min_lat) & (r['lon'] < max_lon) & (r['lat'] < max_lat)]
    # Create choropleth plot
    fig = px.choropleth_mapbox(g2,
                               geojson=g2.geom,
                               locations=g2.index,
                               color='geoscore',
                               color_continuous_scale='ylorrd',
                               center={'lat': (min_lat + max_lat) / 2, 'lon': (min_lon + max_lon) / 2},
                               mapbox_style='carto-positron',
                               opacity=0.5,
                               # autosize=True,
                               # width=960,
                               height=800,
                               zoom=zoom)
    # Add locations as points
    fig.add_scattermapbox(lat=rx['lat'],
                          lon=rx['lon'],
                          mode='markers',
                          legend=None,
                          text=rx['name'],
                          marker_size=8,
                          marker_color=rx['colour'])
    return fig

app.run_server(debug=True)