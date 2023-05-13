from flask import Flask, request, jsonify
import os
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# Define the path to the data folder
data_folder = "/home/rewreu/Projects/exploration/filebrowser/data"

# Define the database connection string
db_url = "sqlite:///:memory:"

# Function to get a list of subfolders in the data folder
def get_subfolders():
    subfolders = [f.name for f in os.scandir(data_folder) if f.is_dir()]
    return subfolders

# Function to get a list of CSV files in a subfolder
def get_csv_files(subfolder):
    csv_files = [f.name for f in os.scandir(os.path.join(data_folder, subfolder)) if f.name.endswith('.csv')]
    return csv_files

# Function to execute an SQL query on a CSV file and return the results
def execute_query(subfolder, csv_file, query):
    csv_path = os.path.join(data_folder, subfolder, csv_file)
    df = pd.read_csv(csv_path)
    engine = create_engine(db_url)
    df.to_sql('data', engine)
    result_df = pd.read_sql_query(query, engine)
    result = result_df.to_dict('records')
    return result

# Route to display a list of subfolders
@app.route('/')
def index():
    subfolders = get_subfolders()
    return jsonify(subfolders)

# Route to get a list of CSV files in a subfolder
@app.route('/csv_files')
def csv_files():
    subfolder = request.args.get('subfolder')
    csv_files = get_csv_files(subfolder)
    return jsonify(csv_files)

# Route to execute an SQL query on a CSV file
@app.route('/query')
def query():
    subfolder = request.args.get('subfolder')
    csv_file = request.args.get('csv_file')
    query = request.args.get('query')
    result = execute_query(subfolder, csv_file, query)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
