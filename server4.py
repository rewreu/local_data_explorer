import os
import re
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import pandas as pd
# import sqlite3
from datetime import datetime, timedelta
import duckdb
import glob

duck = duckdb.connect()

app = dash.Dash(__name__)

# Define options for the subfolder dropdown
subfolders = ["Customer", "Product"]  # replace with your actual subfolder names
subfolder_options = [{'label': subfolder, 'value': subfolder} for subfolder in subfolders]
# Define a layout with a datepicker and a dropdown menu for selecting the CSV file
app.layout = html.Div([

    
    dcc.Dropdown(id='subfolder-dropdown',
                 options=[{'label': f, 'value': f} for f in os.listdir('data')],
                 placeholder='Select a subfolder...',
                 style={'marginBottom': 10,'marginTop': 50}
    ),
    dcc.Textarea(
        id='add-folder',
        placeholder='Add a new parent folder...',
        style={'width': '50%', 'height': 20}
    ),
    # html.Button('Add folder', id='add-foler-button'), # line up this button with the add-folder textarea
 # line up this button vertically with the add-folder textarea, 
    html.Button('Add folder', id='add-foler-button', style={'verticalAlign': 'top', 'height': 25}),
    
    dcc.DatePickerSingle(
        id='date-picker',
        date=datetime.today(),
        display_format='YYYYMMDD',
        style={'marginBottom': 40,'marginTop': 10, 'height': 5, 'fontSize': 15, 'width': '50%'}
    ),
    # add text to the right of date picker
    html.Div(id='date-picker-text', children='Select a date from the calendar above',style={'marginBottom': 40}),

    dcc.Textarea(
        id='query-input',
        placeholder="Enter SQL query. Use 'tb' as table name, for example:  \n SELECT * FROM tb",
        style={'width': '100%', 'height': 200}
    ),
    html.Button('Query', id='submit-button'),
    html.Div(id='query-output')
])


def remove_duplicate_dicts(list_of_dicts):
    # Convert dictionaries to frozensets
    frozen_sets = [frozenset(d.items()) for d in list_of_dicts]

    # Create a set of frozensets to remove duplicates
    unique_frozen_sets = set(frozen_sets)

    # Convert frozensets back to dictionaries
    unique_dicts = [dict(fs) for fs in unique_frozen_sets]

    return unique_dicts

# Define a callback function to update the  subfolder_options
@app.callback(
    dash.dependencies.Output('subfolder-dropdown', 'options'),
    [dash.dependencies.Input('add-folder', 'value'),
     dash.dependencies.Input('add-foler-button', 'n_clicks')],
)
def update_subfolder_options(add_folder, n_clicks):
    if not add_folder:
        return dash.no_update
    
    # check if folder path is valid
    if not add_folder or (not os.path.exists(add_folder)):
        return dash.no_update
    else:
        foler_name = add_folder.split('/')[-1]

        subfolder_options.append({'label': foler_name, 'value': add_folder})
        # make sure subfolder_options does not contain duplicate values
        # subfolder_options = [dict(t) for t in {tuple(d.items()) for d in subfolder_options}]
        return remove_duplicate_dicts(subfolder_options)
    
# Define a callback function to update the date-picker, once a subfolder is selected,
# this function checks the available CSV files in the selected subfolder and updates the date-picker options
@app.callback(
    dash.dependencies.Output('date-picker', 'disabled_days'),
     dash.dependencies.Output('date-picker', 'max_date_allowed'),
     dash.dependencies.Output('date-picker', 'min_date_allowed'),
    [dash.dependencies.Input('subfolder-dropdown', 'value')]
)
def update_date_picker_options(selected_subfolder):
    if not selected_subfolder:
        return dash.no_update
    
    # get all CSV files in the selected subfolder
    csv_files = glob.glob(os.path.join('data', selected_subfolder, '*.csv'))
    # get the list of dates from the CSV file names
    dates = []
    for csv_file in csv_files:
        dt_strs = re.findall(r'\d{8}', csv_file)
        if dt_strs:
            # parse the date string to a datetime object
            dt = datetime.strptime(dt_strs[0], '%Y%m%d')
            dates.append(dt)

    end, start = max(dates),min(dates)
    dates_not_available = []
    for i in range((end - start).days):
        day = start + timedelta(days=i)
        if day not in dates:
            dates_not_available.append(day)
    dates_not_available = [date.strftime('%Y-%m-%d') for date in dates_not_available]
    return dates_not_available, end.strftime('%Y-%m-%d'), start.strftime('%Y-%m-%d')


# Define a callback function to execute the SQL query when the Submit button is clicked
@app.callback(
    dash.dependencies.Output('query-output', 'children'),
    [dash.dependencies.Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('subfolder-dropdown', 'value'),
    #  dash.dependencies.State('csv-dropdown', 'value'),
     dash.dependencies.State('query-input', 'value'),
     dash.dependencies.State('date-picker', 'date')])
def execute_query(n_clicks, selected_subfolder, query, date):
    if not query:
        return html.Div('Please enter a query')
    
    file_name = f"{date.replace('-', '')}.csv"
    csv_path = os.path.join('data', selected_subfolder, file_name)
    # Use pandas to read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)
    global duck
    # tablename = "tb"csv_path.split('.')[0]
    tablename = "tb"
    duck.register(tablename, df)
    result = duck.execute(query).fetchdf()

    # return pandas DataFrame as an HTML table
    result_top50 = result.head(50)
    data =  result_top50.to_dict('records')
    columns =  [{"name": i, "id": i,} for i in (result_top50.columns)]
    return dt.DataTable(data=data, columns=columns)

if __name__ == '__main__':
    app.run_server(debug=True)