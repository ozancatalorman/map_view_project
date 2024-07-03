import os
from dash import Dash, dcc, html, Input, Output
import dash_auth
import geopandas as gpd
import plotly.express as px
from src.monday_locations import get_monday_locations

# Map of funnel stage to display colour
cmap = {'Engaged':   'rgb(253, 171, 61)',
        'Enrolled':  'rgb(255, 100, 46)',
        'Matched':   'rgb(156, 211, 38)',
        'Activated': 'rgb(3, 127, 76)',
        'Lead':      'rgb(196, 196, 196)',
        'Contact':   'rgb(255, 203, 0)',
        'Churned':   'rgb(223, 47, 74)'}

# Get the geo parquet file for geospatial data from S3
geo = gpd.read_parquet('s3://map-view-reef/data/full_geo.parquet').set_index('name')
# Get the real estate locations from monday
re = get_monday_locations("1431777117")
# Map stages with colours
re['colour'] = re['stage'].map(cmap)

msa_options = sorted(list(geo['msa'].unique()))

# Variables for app radio button
geo_data_options = [
    "GeoScore",
    "Population Density",
    "Average Household Size",
    "Food and Beverage Spend(€/capita)",
    "Food and Beverage Spend(country index)"
]

# Map of the column names and variable options
dmap = {'GeoScore': 'geoscore',
        'Population Density': 'pop_sqkm',
        'Average Household Size': 'avg_household_size',
        'Food and Beverage Spend(€/capita)': 'food_bev_spend_euro',
        'Food and Beverage Spend(country index)': 'food_bev_spend_index'
}

# Scales for each variable
rmap = {'GeoScore': [1,10],
        'Population Density': [0,7500],
        'Average Household Size': [1,3],
        'Food and Beverage Spend(€/capita)': [0,5000],
        'Food and Beverage Spend(country index)': [0,250]
}

app = Dash(__name__)
# App authentication
credentials = {
    'reef-map-view' : os.getenv('REEF_MAP_VIEW'),
}
dash_auth.BasicAuth(app,
                    credentials,
                    secret_key = os.getenv('REEF_MAP_VIEW_SKEY')
                    )

# App Layout with components and graph
app.layout = html.Div(style={'backgroundColor': '#E5E5E5', 'fontFamily': 'Arial, sans-serif'}, children=[
    html.H1('Geospatial Data and Real Estate Locations by MSA', style={'textAlign': 'center', 'color': '#333333', 'paddingTop':'10px'}),
    html.Div(style={'margin': '30px'}, children=[
        html.Div(style={'padding': '10px', 'display': 'inline-block', 'verticalAlign': 'top'}, children=[
            html.Label('Select Geo Data:', style={'marginBottom': '10px', 'color': '#333333'}),
            dcc.RadioItems(
                id='geo_data',
                options=[{'label': option, 'value': option} for option in geo_data_options],
                value="GeoScore",
                labelStyle={'display': 'block', 'margin': '5px', 'color': '#333333'},
            ),
        ]),
        html.Div(style={'paddingLeft':'50px', 'display': 'inline-block', 'verticalAlign': 'top', 'width':'500px'}, children=[
            html.Label('Select MSA:', style={'color': '#333333'}),
            dcc.Dropdown(
                id='msa',
                options=[{'label': msa, 'value': msa} for msa in msa_options],
                placeholder='Select MSA',
                style={'width': '75%', 'color': '#333333', 'fontSize': '16px', 'height': '40px'},
            ),
        ]),
        html.Div([
            dcc.Graph(id='graph')
        ]),
    ]),
])

#
@app.callback(
    Output("graph", "figure"),
    Input("msa", "value"),
    Input("geo_data", "value"))
def create_plot(msa, geo_data):
    if msa == '-- Select MSA --':
        return None

    # Select the MSA and Geospatial data to be displayed from the geo data frame
    geo_plot = geo[geo['msa'] == msa]
    data = dmap[geo_data]
    range = rmap[geo_data]
    # Extract the MSA boundaries
    min_lng, min_lat, max_lng, max_lat = geo_plot['geom'].envelope.unary_union.envelope.bounds
    # Calculate the lat/lng range
    mx = max(max_lat - min_lat, max_lng - min_lng)
    # Set zoom level based on lat/lng range
    zoom = 8 if mx > 0.5 else 9
    # Filter real estate locations via lat/lng
    re_x = re[(re['lng'] > min_lng) & (re['lat'] > min_lat) & (re['lng'] < max_lng) & (re['lat'] < max_lat)]

    # Create choropleth plot
    fig = px.choropleth_mapbox(geo_plot,
                               geojson=geo_plot.geom,
                               locations=geo_plot.index,
                               color=data,
                               range_color=range,
                               labels={v2: v1 for v1, v2 in dmap.items()},
                               color_continuous_scale='ylorrd',
                               center={'lat': (min_lat + max_lat) / 2, 'lon': (min_lng + max_lng) / 2},
                               mapbox_style='carto-positron',
                               opacity=0.5,
                               height=800,
                               zoom=zoom)
    # Add real estate locations as points
    fig.add_scattermapbox(lat=re_x['lat'],
                          lon=re_x['lng'],
                          mode='markers',
                          legend=None,
                          text=re_x['name'],
                          marker_size=15,
                          marker_color=re_x['colour'])
    return fig


app.run_server(debug=True)