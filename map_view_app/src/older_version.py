

from dash import Dash, dcc, html, Input, Output
import geopandas as gpd
import pandas as pd
import plotly.express as px

# Map of RE funnel stage to display colour
cmap = {'Engaged':   'rgb(255, 255, 0)',    # Yellow
        'Enrolled':  'rgb(0, 255, 0)',      # Green
        'Matched':   'rgb(0, 127, 0)',      # Dark Green
        'Activated': 'rgb(0, 127, 127)',    # Teal
        'Lead':      'rgb(192, 192, 192)',  # Light Grey
        'Contact':   'rgb(255, 75, 0)',     # Bright Orange
        'Churned':   'rgb(255, 0, 0)'}      # Red

# Read data (from files for demo)
g = gpd.read_parquet('na_eu_geo.parquet').set_index('name')
r = pd.read_csv('full_monday_locations.csv')
r['colour'] = r['stage'].map(cmap)
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