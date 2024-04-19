import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd

# Load your dataset
df = pd.read_csv('data/Sunshine in Asian Cities.csv')

region_data = {
    'Fuzhou': 'East Asia', 'Guangzhou': 'East Asia', 'Hong Kong': 'East Asia',
    'Lhasa': 'Tibet', 'Macau': 'East Asia', 'Nanjing': 'East Asia', 'Ningbo': 'East Asia',
    'Qingdao': 'East Asia', 'Shanghai': 'East Asia', 'Tianjin': 'East Asia',
    'Ürümqi': 'Northwest China', 'Wuhan': 'East Asia', 'Xiamen': 'East Asia',
    'Delhi': 'South Asia', 'Kolkata': 'South Asia', 'Mumbai': 'South Asia',
    'Bangalore': 'South Asia', 'Chennai': 'South Asia', 
    'Denpasar': 'Southeast Asia', 'Jakarta': 'Southeast Asia', 'Makassar': 'Southeast Asia',
    'Medan': 'Southeast Asia', 'Bandar Abbas': 'Middle East', 'Isfahan': 'Middle East',
    'Mashhad': 'Middle East', 'Tehran': 'Middle East', 'Baghdad': 'Middle East',
    'Tel Aviv': 'Middle East', 'Sapporo': 'East Asia', 'Sendai': 'East Asia',
    'Tokyo': 'East Asia', 'Kanazawa': 'East Asia', 'Nagoya': 'East Asia',
    'Almaty': 'Central Asia', 'Astana': 'Central Asia', 'Ulaanbaatar': 'East Asia',
    'Pyongyang': 'East Asia', 'Muscat': 'Middle East', 'Karachi': 'South Asia',
    'Lahore': 'South Asia', 'Quetta': 'South Asia', 'Manila': 'Southeast Asia',
    'Dikson': 'Russia', 'Irkutsk': 'Russia', 'Omsk': 'Russia', 
    'Petropavlovsk-Kamchatsky': 'Russia', 'Vladivostok': 'Russia',
    'Yakutsk': 'Russia', 'Abha': 'Middle East', 'Riyadh': 'Middle East',
    'Singapore': 'Southeast Asia', 'Busan': 'East Asia', 'Seoul': 'East Asia',
    'Kaohsiung': 'East Asia', 'Taichung': 'East Asia', 'Taipei': 'East Asia',
    'Bangkok': 'Southeast Asia', 'Chiang Mai': 'Southeast Asia',
    'Hat Yai': 'Southeast Asia', 'Nakhon Ratchasima': 'Southeast Asia',
    'Ankara': 'Middle East', 'Dubai': 'Middle East', 'Tashkent': 'Central Asia',
    'Da Lat': 'Southeast Asia', 'Da Nang': 'Southeast Asia', 
    'Hanoi': 'Southeast Asia', 'Ho Chi Minh City': 'Southeast Asia',
    'Kabul': 'Central Asia', 'Baku': 'Caucasus', 'Beirut': 'Middle East',
    'Dhaka': 'South Asia', 'Beijing': 'East Asia', 'Chongqing': 'East Asia'
}


df['Region'] = df['City'].apply(lambda x: region_data.get(x, 'Unknown'))
df['City_Region'] = df.apply(lambda row: f"{row['City']} ({row['Region']})", axis=1)

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Assuming first two columns are 'City' and 'Region'
months = df.columns[1:-2]
sorting_options = [{'label': 'Ascending', 'value': 'asc'}, {'label': 'Descending', 'value': 'desc'}]

app.layout = html.Div([
    html.H1("Sunshine Hours in Asian Cities", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Button("Select All", id="select-all", n_clicks=0, style={'margin': '5px'}),
            html.Button("Deselect All", id="deselect-all", n_clicks=0, style={'margin': '5px'}),
            dcc.Checklist(
                id='city-checklist',
                options=[{'label': city_region, 'value': city} for city_region, city in zip(df['City_Region'], df['City'])],
                value=df['City'].tolist(),
                style={'textAlign': 'center', 'padding': '10px', 'display': 'block'}
            ),
        ], style={'flex': '1', 'padding': '10px'}),

        html.Div([
            dcc.Graph(id='sunshine-line-chart'),
            html.Div([
                dcc.Dropdown(
                    id='month-selector',
                    options=[{'label': 'No Sorting', 'value': 'no_sort'}] + [{'label': month, 'value': month} for month in months],
                    value='no_sort',  # Default to no sorting
                    style={'width': '150px', 'margin': '5px', 'display': 'inline-block'}
                ),
                dcc.Dropdown(
                    id='sort-order',
                    options=[
                        {'label': 'Ascending', 'value': 'asc'},
                        {'label': 'Descending', 'value': 'desc'}
                    ],
                    value='asc',  # Default sort order
                    style={'width': '150px', 'margin': '5px', 'display': 'inline-block'}
                )
            ], style={'textAlign': 'center', 'margin': '10px'}),
            dcc.Graph(id='sunshine-heatmap'),
            dcc.Graph(id='total-sunshine-bar-chart')            
        ], style={'flex': '3', 'padding': '10px'}),
    ], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'flex-start'})
])


from dash.exceptions import PreventUpdate

@app.callback(
    Output('city-checklist', 'value'),
    [Input('select-all', 'n_clicks'),
     Input('deselect-all', 'n_clicks')],
    [State('city-checklist', 'options'),
     State('city-checklist', 'value')]
)
def update_city_selection(select_all_clicks, deselect_all_clicks, options, current_values):
    ctx = dash.callback_context
    if not ctx.triggered:
        # If no button was clicked, do nothing.
        raise PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == "select-all":
        return [option['value'] for option in options]
    elif trigger_id == "deselect-all":
        return []
    raise PreventUpdate  # Prevent update if the current state is already aligned with the trigger


@app.callback(
    Output('sunshine-line-chart', 'figure'),
    [Input('city-checklist', 'value')],
    [State('sunshine-line-chart', 'figure')]  # Add the current figure as state if needed
)
def update_line_chart(selected_cities, current_figure):
    if not selected_cities:
        return px.line(title="Select cities to view data")
    
    # Similar adjustments can be made for other callbacks
    filtered_df = df[df['City'].isin(selected_cities)].drop(columns=['Region', 'City_Region'])
    melted_df = filtered_df.melt(id_vars='City', var_name='Month', value_name='Sunshine Hours')
    fig = px.line(melted_df, x='Month', y='Sunshine Hours', color='City', title='Monthly Sunshine Hours by City')
    return fig


@app.callback(
    Output('sunshine-heatmap', 'figure'),
    [Input('city-checklist', 'value'),
     Input('month-selector', 'value'),
     Input('sort-order', 'value')]
)
def update_heatmap(selected_cities, selected_month, sort_order):
    if not selected_cities:
        return px.imshow([[None]], labels={'color': 'No Data'},
                         title="Select cities to view data", color_continuous_scale=[(0, "white"), (1, "white")])

    filtered_df = df[df['City'].isin(selected_cities)].drop(columns=['Region', 'City_Region'])
    filtered_df = filtered_df.set_index('City')
    filtered_df = filtered_df.apply(pd.to_numeric, errors='coerce')

    if selected_month == 'no_sort':
        fig = px.imshow(filtered_df,
                        labels=dict(x="Month", y="City", color="Sunshine Hours"),
                        x=filtered_df.columns, y=filtered_df.index,
                        title="Heatmap of Monthly Sunshine Hours",
                        aspect="auto")
    else:
        sorted_df = filtered_df.sort_values(by=selected_month, ascending=sort_order == 'asc')
        fig = px.imshow(sorted_df,
                        labels=dict(x="Month", y="City", color="Sunshine Hours"),
                        x=sorted_df.columns, y=sorted_df.index,
                        title="Heatmap of Monthly Sunshine Hours",
                        aspect="auto")
    return fig



@app.callback(
    Output('total-sunshine-bar-chart', 'figure'),
    [Input('city-checklist', 'value')]
)
def update_total_sunshine_chart(selected_cities):
    if not selected_cities:
        return px.bar(title="Select cities to view data")
    
    # Filter data based on selected cities
    filtered_df = df[df['City'].isin(selected_cities)]

    # Attempt to convert all columns (except for 'City') to numeric, coercing errors
    numeric_df = filtered_df.set_index('City')
    numeric_df = numeric_df.apply(pd.to_numeric, errors='coerce')

    # Sum the numeric values across the columns (months in this case)
    total_sunshine = numeric_df.sum(axis=1).reset_index()
    total_sunshine.columns = ['City', 'Total Sunshine Hours']

    # Sort the resulting DataFrame in ascending order of total sunshine hours
    total_sunshine = total_sunshine.sort_values(by='Total Sunshine Hours', ascending=True)

    # Create the bar chart
    fig = px.bar(total_sunshine, x='City', y='Total Sunshine Hours',
                 title='Total Annual Sunshine Hours by City',
                 labels={'Total Sunshine Hours': 'Total Sunshine Hours', 'City': 'City'})

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
