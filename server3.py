import os
import re
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
# import sqlite3
from datetime import datetime
import duckdb

duck = duckdb.connect()

app = dash.Dash(__name__)

# Define options for the subfolder dropdown
subfolders = ["Customer", "Product"]  # replace with your actual subfolder names
subfolder_options = [{'label': subfolder, 'value': subfolder} for subfolder in subfolders]
# Define a layout with a datepicker and a dropdown menu for selecting the CSV file
app.layout = html.Div([
    dcc.DatePickerSingle(
        id='date-picker',
        date=datetime.today(),
        display_format='YYYYMMDD',
        style={'marginBottom': 10}
    ),
    dcc.Dropdown(id='subfolder-dropdown',
                 options=[{'label': f, 'value': f} for f in os.listdir('data')],
                 placeholder='Select a subfolder...',
                 style={'marginBottom': 10}
    ),
    dcc.Dropdown(id='csv-dropdown',
                 placeholder='Select a CSV file...',
                 style={'marginBottom': 10}
    ),
    dcc.Textarea(
        id='query-input',
        placeholder='Enter SQL query...',
        style={'width': '100%', 'height': 200}
    ),
    html.Button('Submit', id='submit-button'),
    html.Div(id='query-output')
])

# Define a callback function to update the CSV file dropdown menu when the date is changed
@app.callback(
    dash.dependencies.Output('csv-dropdown', 'options'),
    [dash.dependencies.Input('date-picker', 'date'),
     dash.dependencies.Input('subfolder-dropdown', 'value')])
def update_csv_dropdown(date, subfolder):
    csv_folder = os.path.join('data', subfolder)
    # Use regular expression to filter the CSV files by date
    pattern = re.compile(f"{date.replace('-', '')}.*\.csv")
    csv_files = [f for f in os.listdir(csv_folder) if pattern.match(f)]
    options = [{'label': f, 'value': f} for f in csv_files]
    return options

# Define a callback function to execute the SQL query when the Submit button is clicked
@app.callback(
    dash.dependencies.Output('query-output', 'children'),
    [dash.dependencies.Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('subfolder-dropdown', 'value'),
     dash.dependencies.State('csv-dropdown', 'value'),
     dash.dependencies.State('query-input', 'value')])
def execute_query(n_clicks, selected_subfolder, selected_csv, query):
    if not query:
        return html.Div('Please enter a query')
    csv_path = os.path.join('data', selected_subfolder, selected_csv)
    # Use pandas to read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)
    # Use pandas to execute the SQL query and get the result as a DataFrame
    result = pd.read_sql_query(query, con=sqlite3.connect(":memory:"), parse_dates=True)
    # Convert the result to an HTML table and return it as the output
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in result.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(result.iloc[i][col]) for col in result.columns
            ]) for i in range(len(result))
        ])
    ])

if __name__ == '__main__':
    app.run_server(debug=True)