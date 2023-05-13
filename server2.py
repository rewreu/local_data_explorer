import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
# import sqlite3
import duckdb

duck = duckdb.connect()

app = dash.Dash(__name__)

# Define options for the subfolder dropdown
subfolders = ["Customer", "Product"]  # replace with your actual subfolder names
subfolder_options = [{'label': subfolder, 'value': subfolder} for subfolder in subfolders]

# Define a callback function to update the CSV file options when the subfolder dropdown changes
@app.callback(
    dash.dependencies.Output('csv-dropdown', 'options'),
    [dash.dependencies.Input('subfolder-dropdown', 'value')])
def update_csv_options(selected_subfolder):
    csv_files = os.listdir(f"data/{selected_subfolder}")
    csv_options = [{'label': csv_file, 'value': csv_file} for csv_file in csv_files if csv_file.endswith('.csv')]
    return csv_options

# Define the layout of the app
app.layout = html.Div([
    dcc.Dropdown(
        id='subfolder-dropdown',
        options=subfolder_options,
        value=subfolders[0]  # set the default selected subfolder
    ),
    dcc.Dropdown(
        id='csv-dropdown',
        options=[],
    value=None  # no CSV file selected initially
    ),
    dcc.Textarea(
        id='query-input',
        placeholder='Enter SQL query...',
        style={'width': '100%', 'height': 200}
    ),
    html.Button('Submit', id='submit-button'),
    html.Div(id='query-output')
])

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
    csv_path = f"data/{selected_subfolder}/{selected_csv}"
    # Use pandas to read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)
    global duck
    tablename = selected_csv.split('.')[0]
    duck.register(tablename, df)
    result = duck.execute(query).fetchdf()
    # Use pandas to execute the SQL query and get the result as a DataFrame
    # result = pd.read_sql_query(query, con=sqlite3.connect(":memory:"), parse_dates=True)
    # Convert the result to an HTML table and return it as the output
    # return dcc.Markdown(result_df.to_markdown())
    # return result_df.to_html()
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
