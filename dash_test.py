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
from dash.dependencies import Input, Output
import plotly.graph_objs as go

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
from dash import Dash, html, dcc, Input, Output, State
from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc

# Cargar variables de entorno
load_dotenv()
weather_api_key = os.getenv("weatherapi")
username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PW')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
db_climate = os.getenv('DB_CLIMATE')

# Conexión a la base de datos
url = f'postgresql://{username}:{password}@{host}:{port}/climate'
engine = create_engine(url, echo=True)

# Definir DataFrames
df_mart_week = pd.read_sql_query('SELECT * FROM mart_conditions_week', url)
df_mart_week.sort_values('week_of_year', inplace=True)
df_day = pd.read_sql_query('SELECT * FROM mart_forecast_day', url)
df_month = pd.read_sql_query('SELECT * FROM mart_conditions_month', url)
df_iso = pd.read_csv('./data/iso_codes.csv')
countries_of_interest = ['Spain', 'Germany']
df_iso_selected = df_iso[df_iso['country'].isin(countries_of_interest)]
df_merged = pd.merge(df_mart_week, df_iso_selected, on='country')
df_avg_temp = df_merged.groupby(['country', 'alpha-3', 'year_and_week'])['max_temp_c'].mean().reset_index()
df_merged['max_temp_c'] = df_merged['max_temp_c'].round(2)

# Graph 1: average temperature per city
fig = px.line(
    df_day, 
    x='date', 
    y='avg_temp_c', 
    color='city',
    title='Average Temperature(°C) per city',
    labels={
        'date': 'Date', 
        'avg_temp_c': 'Temperature(°C)', 
        'city': 'City'
    }
)
fig.update_layout(
    plot_bgcolor="#222222", 
    paper_bgcolor="#222222", 
    font_color="white",
    title_font_size=20,
    legend_title_text='City',
    legend_title_font_size=14,
    legend_font_size=12
)
fig.update_traces(
    line=dict(width=2),
    marker=dict(size=8)
)
fig.update_xaxes(
    title_text='Month',
    title_font=dict(size=14, color='white'),
    tickfont=dict(color='white'),
    gridcolor='gray'
)
fig.update_yaxes(
    title_text='Average Temperature(°C) per city',
    title_font=dict(size=14, color='white'),
    tickfont=dict(color='white'),
    gridcolor='gray'
)
graph_avr = dcc.Graph(figure=fig)

# Gráfico 2 - Maximum Temperature per City
fig = px.scatter(
    df_day,
    x="month_of_year",
    y="max_temp_c",
    color="city",
    title="Maximum Temperature(°C) per city",
    labels={'month_of_year': 'Month of the Year', 'max_temp_c': 'Temperature (°C)', 'city': 'City'}
)
fig.update_layout(
    plot_bgcolor="#222222",
    paper_bgcolor="#222222",
    font_color="white",
    title_font_size=20,
    legend_title_text='City',
    legend_title_font_size=14,
    legend_font_size=12
)
fig.update_xaxes(
    title_text='Month',
    title_font=dict(size=14, color='white'),
    tickfont=dict(color='white'),
    gridcolor='gray'
)
fig.update_yaxes(
    title_text='Temperature (°C)',
    title_font=dict(size=14, color='white'),
    tickfont=dict(color='white'),
    gridcolor='gray'
)
graph_monthly_max_temp = dcc.Graph(figure=fig)

# Gráfico 3 - Minimum Temperature per City
fig = px.scatter(
    df_day,
    x="month_of_year",
    y="min_temp_c",
    color="city",
    title="Minimum Temperature(°C) per city",
    labels={'month_of_year': 'Month of the Year', 'min_temp_c': 'Temperature (°C)', 'city': 'City'}
)
fig.update_layout(
    plot_bgcolor="#222222",
    paper_bgcolor="#222222",
    font_color="white",
    title_font_size=20,
    legend_title_text='City',
    legend_title_font_size=14,
    legend_font_size=12
)
fig.update_xaxes(
    title_text='Month of the Year',
    title_font=dict(size=14, color='white'),
    tickfont=dict(color='white'),
    gridcolor='gray'
)
fig.update_yaxes(
    title_text='Temperature (°C)',
    title_font=dict(size=14, color='white'),
    tickfont=dict(color='white'),
    gridcolor='gray'
)
graph_monthly_min_temp = dcc.Graph(figure=fig)

# Graph 4 daylight hours
# Convert 'sunrise' and 'sunset' columns to datetime.time
df_day['sunrise_n'] = pd.to_datetime(df_day['sunrise_n'], format='%H:%M:%S').dt.time
df_day['sunset_n'] = pd.to_datetime(df_day['sunset_n'], format='%H:%M:%S').dt.time

# Ensure 'date' column is in datetime format
df_day['date'] = pd.to_datetime(df_day['date'])

# Convert 'sunrise' and 'sunset' to timedelta
df_day['sunrise_timedelta'] = pd.to_timedelta(df_day['sunrise_n'].astype(str))
df_day['sunset_timedelta'] = pd.to_timedelta(df_day['sunset_n'].astype(str))

# Calculate daylight hours
df_day['daylight_hours'] = (df_day['sunset_timedelta'] - df_day['sunrise_timedelta']).dt.total_seconds() / 3600
fig = px.line(
    df_day, 
    x='date', 
    y='daylight_hours', 
    color='city',
    title='Daylight Hours',
    labels={
        'date': 'Date', 
        'daylight_hours': 'Daylight Hours', 
        'city': 'City'
    }
)
fig.update_layout(
    plot_bgcolor="#222222", 
    paper_bgcolor="#222222", 
    font_color="white",
    title_font_size=20,
    legend_title_text='City',
    legend_title_font_size=14,
    legend_font_size=12
)
fig.update_traces(
    line=dict(width=2),
    marker=dict(size=8)
)
fig.update_xaxes(
    title_text='Month',
    title_font=dict(size=14, color='white'),
    tickfont=dict(color='white'),
    gridcolor='gray'
)
fig.update_yaxes(
    title_text='Daylight hours',
    title_font=dict(size=14, color='white'),
    tickfont=dict(color='white'),
    gridcolor='gray'
)
graph_daylight_hours = dcc.Graph(figure=fig)

# Gráfico 5 - Weather Type
fig = px.bar(
    df_month,
    x='city',
    y=['sunny_days', 'rainy_days', 'snowy_days'],
    barmode='stack',
    labels={'value': 'Number of Days', 'city': 'City'},
    title="Type of weather",
    height=400,
    color_discrete_map={
        'sunny_days': 'orange',
        'rainy_days': 'blue',
        'snowy_days': 'gray'
    }
)
fig.for_each_trace(lambda t: t.update(name={
    'sunny_days': 'Sunny days',
    'rainy_days': 'Rainy days',
    'snowy_days': 'Snowy days'
}[t.name]))
fig.update_layout(
    plot_bgcolor="#222222",
    paper_bgcolor="#222222",
    font_color="white",
    title_font_size=20,
    legend_title_text='Type of weather',
    legend_title_font_size=14,
    legend_font_size=12
)
fig.update_xaxes(title_text='City')
fig.update_yaxes(title_text='Days')
graph_weather_type = dcc.Graph(figure=fig)

# Gráfico 1 - Average Temperature
fig = px.choropleth(
    df_merged,
    locations='alpha-3',
    color='max_temp_c',
    hover_name='country',
    animation_frame='year_and_week',
    projection='natural earth',
    color_continuous_scale='thermal',
    title='Average Temperature (°C)'
)
fig.update_geos(
    showcoastlines=True,
    coastlinecolor="Black",
    showland=True,
    landcolor="white",
    showcountries=True,
    countrycolor="gray",
    showframe=False,
    showocean=True,
    oceancolor="LightBlue",
    showlakes=True,
    lakecolor="LightBlue",
    projection_scale=1.1
)
fig.update_layout(
    plot_bgcolor="#222222",
    paper_bgcolor="#222222",
    font_color="white",
    title_text='Average Weekly Temperature(°C)',
    title_font_size=20,
    coloraxis_colorbar=dict(
        title="Temperature (°C)",
        titlefont=dict(size=14, color='white'),
        tickfont=dict(color='white')
    ),
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_scale=1.1
    ),
    height=600,
    width=800
)
graph_avr_week_temp = dcc.Graph(figure=fig)

#Creating Dash
#https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
# Creando Dash
app = dash.Dash(external_stylesheets=[dbc.themes.SLATE])
server = app.server

# Dash components https://dash.plotly.com/dash-html-components
app.layout = html.Div([
html.H1('WEATHER DASHBOARD', className='display-4', style={'textAlign': 'center', 'color': 'white', 'fontFamily': 'Montserrat, Arial, sans-serif',}),
    html.H2('Analyzing weather data in different cities', style={'textAlign': 'center','padding': '5px', 'color': 'white', 'fontFamily': 'Lato, sans-serif'}),
    html.Div([
        html.Div('Cities: Barcelona, Berlin, Madrid, Tenerife',
                 style={'backgroundColor': '#9467bd', 'color': 'white', 'padding': '10px', 'margin': '10px'}),
        html.Div(id='city-selection-div'),
        html.Div(graph_avr, id='graph_avr', style={'padding': '20px', 'width': '100%'}),  # Full-width graph
        html.Div([
                html.Hr(),  # Horizontal line for separation
                html.P('Temperature variations are more pronounced in Madrid and Berlin due to their continental climates, featuring cold winters and hot summers. \n Barcelona and Tenerife, with their more temperate climates, experience milder and more consistent temperatures throughout the year.',
                       style={'textAlign': 'center', 'color': 'white', 'fontSize': 14})
            ], style={'padding': '20px'})
             ]),
        html.Div([
            html.Div([
                html.Div(graph_monthly_max_temp),
                html.Div(graph_monthly_min_temp)
            ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px', 'padding': '20px'}),
               html.Div([
            html.Div(graph_daylight_hours, style={'padding': '20px', 'width': '100%'}),  # Added comma here
            html.Div([
                html.Div(graph_weather_type),
                html.Div(graph_avr_week_temp)
            ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px', 'padding': '20px'}),
        ])
    ], style={'padding': '20px'})
])

if __name__ == '__main__':
    app.run_server(debug=True)