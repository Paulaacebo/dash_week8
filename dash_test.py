import requests
import pprint
import pandas as pd
import datetime
import json
import os

from dotenv import dotenv_values
from dotenv import load_dotenv
from sqlalchemy import create_engine, types
from sqlalchemy.dialects.postgresql import JSON as postgres_json

import plotly.express as px
import dash
from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc

load_dotenv()
weather_api_key = os.getenv("weatherapi")
username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PW')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
db_climate = os.getenv('DB_CLIMATE')

#weather_api_key = config['weatherapi']
#username = config['POSTGRES_USER']
#password = config['POSTGRES_PW']
#host = config['POSTGRES_HOST']
#port = config['POSTGRES_PORT']
#db_climate = config['DB_CLIMATE']

url = f'postgresql://{username}:{password}@{host}:{port}/climate'
engine = create_engine(url, echo=True)
#Defining DF
df_mart_week = pd.read_sql_query('SELECT * FROM mart_conditions_week', url)  
df_mart_week.sort_values('week_of_year',inplace=True)

df_day = pd.read_sql_query('SELECT * FROM mart_forecast_day', url) 

df_month = pd.read_sql_query('SELECT * FROM mart_conditions_month', url) 

df_iso = pd.read_csv('./data/iso_codes.csv')
countries_of_interest = ['Spain', 'Germany']
df_iso_selected = df_iso[df_iso['country'].isin(countries_of_interest)]

df_merged=pd.merge(df_mart_week, df_iso_selected, on='country')
df_avg_temp = df_merged.groupby(['country', 'alpha-3', 'year_and_week'])['max_temp_c'].mean().reset_index()
df_merged['max_temp_c'] = df_merged['max_temp_c'].round(2)

#Graph 1 - Max temp per city
fig = px.line(df_mart_week, 
           x="week_of_year", 
           y="max_temp_c", 
           # animation_frame="week_of_year", # time as animation frame
           color="city",
           title="Weekly maximum temperature per city",
           )

graph_weekly_max_temp = dcc.Graph(figure=fig)

#Graph 2
fig = px.bar(df_month, 
             x='city', 
             y=['sunny_days','rainy_days','snowy_days'],  
             # color=,
             animation_frame='week_of_year',
             barmode='stack',
             orientation='v',
             #height=800,
             title="Number of sunny/cloudy/rainy/snowy days per week")

graph_type_of_days = dcc.Graph(figure=fig)

#Graph 3
fig = px.scatter_mapbox(df_day,
                        lat="lat", lon="lon",
                        hover_name="max_temp_c",
                        color="max_temp_c",
                        animation_frame='date',
                        size='uv',
                        # start location and zoom level
                        zoom=2, 
                        center={'lat': 51.1657, 'lon': 10.4515}, # defining the staring coordinate of map
                        mapbox_style='carto-positron') # map style 

graph_map = dcc.Graph(figure=fig)

#Graph 4
fig = px.choropleth(
    df_merged,
    locations='alpha-3',           # Column containing ISO alpha-3 codes
    color='max_temp_c',            # Column to map to color
    hover_name='country',          # Column to use for hover information
    animation_frame='year_and_week',  # Column to use for animation
    projection='natural earth',    # Projection type for the map
    color_continuous_scale='thermal',  # Color scale
    title='Average temperature'
)
fig.update_geos(
    showcoastlines=True,           # Mostrar líneas costeras
    coastlinecolor="Black",        # Color de las líneas costeras
    showland=True,                 # Mostrar tierra
    landcolor="white",             # Color de la tierra
    showcountries=True,            # Mostrar límites de los países
    countrycolor="gray",           # Color de los límites de los países
    showframe=False,               # Ocultar el marco del mapa
    showocean=True,                # Mostrar el océano
    oceancolor="LightBlue",        # Color del océano
    showlakes=True,                # Mostrar lagos
    lakecolor="LightBlue",         # Color de los lagos
    projection_scale=50            # Ajustar la escala de la proyección
)
fig.update_layout(
    title_text='Average weekly temp',
    coloraxis_colorbar=dict(
        title="Temperature (°C)"
    ),
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_scale=50  # Ajustar la escala de la proyección
    ),
    height=600,  # Altura del gráfico
    width=800    # Ancho del gráfico
)
graph_avr_week_temp = dcc.Graph(figure=fig)

#Creating Dash
#https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR])
server = app.server

#Dash components https://dash.plotly.com/dash-html-components
app.layout = html.Div([
    html.H1('Weather Dashboard 2024', style={'textAlign': 'center', 'color': 'black'}),
    html.H2('Project Challenge', style={'paddingLeft': '30px'}),
    html.H3('Graphs', style={'paddingLeft': '30px'}),
    html.Div([
        html.Div('Analyzed cities: Barcelona, Berlin, Madrid, Tenerife', 
                 style={'backgroundColor': 'coral', 'color': 'white', 'padding': '10px', 'margin': '10px'}),
        html.Div([
            graph_weekly_max_temp, 
            graph_type_of_days, 
            graph_avr_week_temp, 
            graph_map
        ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px'})
    ], style={'padding': '20px'})
])

# Ejecuta la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)