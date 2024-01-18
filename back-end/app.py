from flask import Flask, request, jsonify, render_template
import os, datetime, psycopg2
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from datetime import date as dt
from datetime import datetime
from flask_cors import CORS
import json
from metadata_tables import Common_Metadata, Geojson_Metadata, Tiff_Metadata, Las_Metadata, db as db_
from file_parser import process_files, type_dict, size_dict, analytics
# from 

import pickle
from search_tool import search_files, all

with open('data_extensions.pkl', 'rb') as file:
    type_dict = pickle.load(file)

with open('data_size.pkl', 'rb') as file:
    size_dict = pickle.load(file)


global_database = ""
ext_dir=[[".jpg", ".png", ".jpeg"], [".pdf"],[".txt"], [".py", ".cpp", ".js", ".java", ".css", ".html", ".json"], [".xlsx"], [".csv"], [".pptx"], [".doc"]]
ext_dir_names = ["Image", "PDF", "Text", "Code Files", "Excel", "CSV", "Presentation", "Documentation"]
conn = ""

query_ = ""
location_ = ""
coordinate_ = ""
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

@app.route("/search", methods=["POST"])
def search():
    input=request.get_json()
    print()
    print(input)
    print()
    
    query = input.get("query", "")
    latitude=input.get("latitude", "")
    longitude=input.get("longitude", "")
    coordinate=latitude+longitude
    location=input.get("location", "")
    data=[]
    query_=query
    location_=location
    coordinate_=coordinate
    if query=="" and location=="" and coordinate=="":
        data = all()
        result = [{'file_name': i[1], 'file_type': i[3], 'file_size': i[4], 'creation_date': i[6]} for i in data]
        
        
        return jsonify(result)
    elif location == "" or coordinate=="":
        data = search_files(query=query, location1=location, coordinate1=coordinate)
    print(data)
    result = [{'file_name': i[1], 'file_type': i[2], 'file_size': i[3], 'creation_date': i[4]} for i in data]
        
        
    return jsonify(result)
    

    
@app.route("/filter", methods=["POST"])
def filter():
    input=request.get_json()
    min_size=int(input.get("min_size", ""))
    max_size=int(input.get("max_size", ""))
    file_types = list(input.get("file_types", ""))
    
    print("min size", min_size)
    print("max_size", max_size)
    print("file types", file_types)
    
    if query_=="" and location_=="" and coordinate_=="":
        data = all()
        result = [{'file_name': i[1], 'file_type': i[3], 'file_size': i[4], 'creation_date': i[6]} for i in data]
        
    elif location_ == "" or coordinate_=="":
        data = search_files(query=query_, location1=location_, coordinate1=coordinate_)
        print(data)
        result = [{'file_name': i[1], 'file_type': i[2], 'file_size': i[3], 'creation_date': i[4]} for i in data]
    
    final_result = []
    for i in result:
        if i["file_size"] > max_size or i["file_size"] <min_size:
            continue
        if i["file_type"] in file_types or len(file_types) == 0:
            final_result.append(i)
    return jsonify(final_result)
    
    
    

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

@app.route("/analytics", methods=["GET"])
def get_analytics():
    file = {
        "total_files" : analytics["total_file"],
        "file_types_len" : analytics["file_types_len"],
        "file_types" : analytics["file_types"],
        "file_type_distribution" : analytics["file_types_distribution"],
        "max" : analytics["max"],
        "min" : analytics["min"],
        "size0" : analytics["size0"],
        "size1" : analytics["size1"],
        "size2" : analytics["size2"],
        "size3" : analytics["size3"]
    }    
    return jsonify(file)

def setting_global_database():
    #global_database
    return "21"

if __name__ == "__main__":
    setting_global_database()
    app.run(debug=True)
    

