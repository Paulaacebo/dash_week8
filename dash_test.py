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


# Graph 1 - Weekly Maximum Temperature per City
fig = px.line(
    df_mart_week, 
    x="week_of_year", 
    y="max_temp_c", 
    color="city",
    title="Weekly Maximum Temperature per City",
    labels={'week_of_year': 'Week of the Year', 'max_temp_c': 'Max Temperature (°C)', 'city': 'City'}
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
    title_text='Week of the Year',
    title_font=dict(size=14, color='white'),
    tickfont=dict(color='white'),
    gridcolor='gray'
)
fig.update_yaxes(
    title_text='Max Temperature (°C)',
    title_font=dict(size=14, color='white'),
    tickfont=dict(color='white'),
    gridcolor='gray'
)
graph_weekly_max_temp = dcc.Graph(figure=fig)

#Graph 2 
fig = px.bar(
    df_month, 
    x='city', 
    y=['sunny_days', 'rainy_days', 'snowy_days'],  
    barmode='stack',
    labels={'value': 'Number of Days', 'city': 'City'},
    title="Number of Sunny, Rainy, and Snowy Days per Week",
    height=400,
    color_discrete_map={
        'sunny_days': 'orange',
        'rainy_days': 'blue',
        'snowy_days': 'gray'
    }
)

# Actualizar las etiquetas de la leyenda
fig.for_each_trace(lambda t: t.update(name={
    'sunny_days': 'Sunny days',
    'rainy_days': 'Rainy days',
    'snowy_days': 'Snowy days'
}[t.name]))

# Actualizar el layout para cambiar colores de fondo y fuentes
fig.update_layout(
    plot_bgcolor="#222222", 
    paper_bgcolor="#222222", 
    font_color="white",
    title_font_size=20,
    legend_title_text='Weather Type',
    legend_title_font_size=14,
    legend_font_size=12
)

# Agregar estilos adicionales si es necesario
fig.update_xaxes(title_text='City')
fig.update_yaxes(title_text='Number of Days')

# Crear el gráfico con Dash
graph_weather_type = dcc.Graph(figure=fig)

# Graph 3 Average Temperature
fig = px.choropleth(
    df_merged,
    locations='alpha-3',           # Column containing ISO alpha-3 codes
    color='max_temp_c',            # Column to map to color
    hover_name='country',          # Column to use for hover information
    animation_frame='year_and_week',  # Column to use for animation
    projection='natural earth',    # Projection type for the map
    color_continuous_scale='thermal',  # Color scale
    title='Average Temperature'
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
    projection_scale=1.1           # Ajustar la escala de la proyección
)

# Actualizar el layout para cambiar colores de fondo y fuentes
fig.update_layout(
    plot_bgcolor="#222222",        # Fondo del gráfico
    paper_bgcolor="#222222",       # Fondo del papel
    font_color="white",            # Color de la fuente
    title_text='Average Weekly Temperature',
    title_font_size=20,
    coloraxis_colorbar=dict(
        title="Temperature (°C)",
        titlefont=dict(size=14, color='white'),  # Color y tamaño del título
        tickfont=dict(color='white')  # Color de las etiquetas
    ),
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_scale=1.1  # Ajustar la escala de la proyección
    ),
    height=600,  # Altura del gráfico
    width=800    # Ancho del gráfico
)
graph_avr_week_temp = dcc.Graph(figure=fig)

#Creating Dash
#https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
app = dash.Dash(external_stylesheets=[dbc.themes.SLATE])
server = app.server

#Dash components https://dash.plotly.com/dash-html-components
app.layout = html.Div([
    html.H1('Weather Dashboard 2024', style={'textAlign': 'center', 'color': 'black'}),
    html.H2('Project Challenge', style={'paddingLeft': '30px'}),
    html.H3('Graphs', style={'paddingLeft': '30px'}),
    html.Div([
        html.Div('Analyzed cities: Barcelona, Berlin, Madrid, Tenerife', 
                 style={'backgroundColor': 'coral', 'color': 'white', 'padding': '10px', 'margin': '10px'}),
        html.Div(graph_weekly_max_temp, style={'padding': '20px', 'width': '100%'}),  # Esta gráfica ocupa toda la pantalla
        html.Div([
            html.Div(graph_weather_type),
            html.Div(graph_avr_week_temp)
        ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px', 'padding': '20px'})
    ], style={'padding': '20px'})
])

# Ejecuta la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)