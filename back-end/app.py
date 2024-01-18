from flask import Flask, request, jsonify, render_template
import os, datetime, psycopg2
from flask_sqlalchemy import SQLAlchemy
from datetime import date as dt
from datetime import datetime
from flask_cors import CORS
import json
from metadata_tables import Common_Metadata, Geojson_Metadata, Tiff_Metadata, Las_Metadata, db as db_
from file_parser import process_files, type_dict, size_dict

import pickle

with open('data_extensions.pkl', 'rb') as file:
    type_dict = pickle.load(file)

with open('data_size.pkl', 'rb') as file:
    size_dict = pickle.load(file)



ext_dir=[[".jpg", ".png", ".jpeg"], [".pdf"],[".txt"], [".py", ".cpp", ".js", ".java", ".css", ".html", ".json"], [".xlsx"], [".csv"], [".pptx"], [".doc"]]
ext_dir_names = ["Image", "PDF", "Text", "Code Files", "Excel", "CSV", "Presentation", "Documentation"]
conn = ""
def convertDate(timestamp):
    d = datetime.datetime.utcfromtimestamp(timestamp)
    formatedDate = d.strftime('%b %d, %Y')

    return formatedDate

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost/postgres'
# db = SQLAlchemy(app)
db_.init_app(app)

def connect_to_db():
    params = {
        "database": "geospatial",
        "user": "postgres",
        "password": "12345678",
        "host": "localhost",
        "port": 5432,
    }
    conn = psycopg2.connect(**params)
    return conn



@app.route("/")
def index():
    return "Welcome Dataducks back-end Server"  


@app.route("/upload", methods=["POST"])
def add_directory():    
    input = request.get_json()                        
    dir_path = input.get('dir_path', '')
    print(dir_path)
    dir_metadata = []
    isdir = bool(os.path.isdir(dir_path))
    pathExists = bool(os.path.exists(dir_path))
    isFile = bool(os.path.isfile(dir_path))
    print("isdir: ", isdir)
    print("pathExists: ", pathExists)
    print("isFile: ", isFile)
    print()
    response_data = {'key': 'Invalid Path'}  
    response_data1 = {'key': 'Path should a directory not a File'}  
    response_data2 = {'key': 'Done Uploading'}  
    if pathExists == False:
        return jsonify(response_data)
    elif isFile:
        return jsonify(response_data1)
    else:
        print("\nReached correct Place \n")
    process_files(dir_path, db_)                     
    print("Folder's Files Added Succesfull")
    return jsonify(response_data2)
    
@app.route("/gettype_info", methods=["GET"])
def get_type():
    output = list(type_dict)
    return jsonify(output)

@app.route("/getsize_info", methods=["GET"])
def get_size():
    
    return jsonify(size_dict)

if __name__ == "__main__":
    app.run(debug=True)
    

