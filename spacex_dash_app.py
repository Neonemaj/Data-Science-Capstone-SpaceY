import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

app = dash.Dash(__name__)

app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(id='site-dropdown',
                                    options=[{'label': 'All sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}],
                                        value='ALL', placeholder='Select a Launch Site here',
                                        searchable=True),
                                html.Br(),
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                                    marks={i: str(i) for i in range(0, 10001, 1000)},
                                    value=[min_payload, max_payload]),
                                html.Div(dcc.Graph(id='success-payload-scatter-chart'))
                                ])

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def pie_chart(input_site):
    if input_site == 'ALL':
        fig = px.pie(df := spacex_df.groupby('Launch Site')[['class']].mean(),
            values='class', names=df.index, title='Success rate for all sites')
        del df
    else:
        percentage = spacex_df[spacex_df['Launch Site'] == input_site]['class'].mean()
        fig = px.pie(values=[percentage, 1-percentage], names=['Success', 'Failure'],
        title=f'Succes rate for {input_site}')
        del percentage
    return fig

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
             [Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value')])
def scatter_chart(input_site, input_range):
    filtered_df = spacex_df.query(f'{input_range[0]} <= `Payload Mass (kg)` <= {input_range[1]}').copy()
    filtered_df.reset_index(drop=True, inplace=True)
    if input_site == 'ALL':
        fig = px.scatter(data_frame=filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category', title='Outcomes of missions from all launch sites')
    else:
        fig = px.scatter(data_frame=filtered_df[filtered_df['Launch Site'] == input_site],
            x='Payload Mass (kg)', y='class', color='Booster Version Category',
            title=f'Outcomes of missions from {input_site}')
    del filtered_df
    return fig

if __name__ == '__main__':
    app.run_server()