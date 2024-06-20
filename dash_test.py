import pandas as pd 
import dash
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import dash_table
import dash_bootstrap_components as dbc

df = px.data.gapminder()
df_germany = df[df['country']=='Germany']
df_germany = df_germany[['year', 'lifeExp', 'pop', 'gdpPercap']]
df_countries =df[df['country'].isin(['Germany', 'Belgium', 'Denmark'])]

# table
table = dash_table.DataTable(df_germany.to_dict('records'),
                                  [{"name": i, "id": i} for i in df_germany.columns],
                               style_data={'color': 'white','backgroundColor': "#222222"},
                              style_header={
                                  'backgroundColor': 'rgb(210, 210, 210)',
                                  'color': 'black','fontWeight': 'bold'}, 
                                     style_table={ 
                                         'minHeight': '400px', 'height': '400px', 'maxHeight': '400px',
                                         'minWidth': '900px', 'width': '900px', 'maxWidth': '900px',
                                         'marginLeft': 'auto', 'marginRight': 'auto',
                                         'marginTop': 0, 'marginBottom': "30"}
                                     )

# Bar graph
fig1 = px.bar(df_countries, 
             x='year', 
             y='lifeExp',  
             color='country',
             barmode='group',
             height=300, title = "Germany vs Denmark & Belgium",)

fig1 = fig1.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white", 
    #margin=dict(l=20, r=20, t=0, b=20)
)
    

graph1 = dcc.Graph(figure=fig1)

# Line graph
fig2 = px.line(df_germany, x='year', y='lifeExp', height=300, title="Life Expectancy in Germany", markers=True)
fig2 = fig2.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white"
    )
graph2 = dcc.Graph(figure=fig2)

# Map
fig3 = px.choropleth(df_countries, locations='iso_alpha', 
                    projection='natural earth', animation_frame="year",
                    scope='europe',  # we are adding the scope as europe
                    color='lifeExp', locationmode='ISO-3', 
                    color_continuous_scale=px.colors.sequential.ice)

fig3 = fig3.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white", geo_bgcolor="#222222"
    )

# here we needed to change the geo color also to make the world black

graph3 = dcc.Graph(figure=fig3)

# Our app

app =dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

dropdown = dcc.Dropdown(options=['Germany', 'Belgium', 'Denmark'], value='Belgium', clearable=False)


app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])
server = app.server
app.layout = html.Div([html.H1('Gap Minder Analysis of Germany', style={'textAlign': 'center', 'color': '#636EFA'}), 
                       html.Div(html.P("Using the gapminder data we take a look at Germany's profile"), 
                                style={'marginLeft': 50, 'marginRight': 25}),
                       html.Div([html.Div('Germany', 
                                          style={'backgroundColor': '#636EFA', 'color': 'white', 
                                                 'width': '900px', 'marginLeft': 'auto', 'marginRight': 'auto'}),
                                 table, dropdown, graph1,  graph2, graph3])
                      ])

# Output(component_id='my-output', component_property='children'),
# Input(component_id='my-input', component_property='value')

# decorator - decorate functions
@callback(
    Output(graph1, "figure"),
    Input(dropdown, "value"))
def update_bar_chart(country): 
    mask = df_countries["country"] == country # coming from the function parameter
    fig =px.bar(df_countries[mask], 
             x='year', 
             y='lifeExp',  
             color='country',
             color_discrete_map = {'Germany': '#7FD4C1', 'Denmark': '#8690FF', 'Belgium': '#F7C0BB'},
             barmode='group',
             height=300, title = "Germany vs Denmark & Belgium",)
    fig = fig.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white"
    )

    return fig # whatever you are returning here is connected to the component property of the output

if __name__ == "__main__":
    app.run_server(port=8088)
# you can change the port for the dashboard like this (be careful of reserved ports)

