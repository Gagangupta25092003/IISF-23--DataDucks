from flask import Flask, request, jsonify, render_template
import os, datetime, psycopg2
from flask_sqlalchemy import SQLAlchemy
from datetime import date as dt
from datetime import datetime
from flask_cors import CORS
import json
from metadata_extraction_pipeline import extract_metadata
from metadata_tables import Common_Metadata, Geojson_Metadata, Tiff_Metadata, Las_Metadata, db as db_
from file_parser import process_files

ext_dir=[[".jpg", ".png", ".jpeg"], [".pdf"],[".txt"], [".py", ".cpp", ".js", ".java", ".css", ".html", ".json"], [".xlsx"], [".csv"], [".pptx"], [".doc"]]
ext_dir_names = ["Image", "PDF", "Text", "Code Files", "Excel", "CSV", "Presentation", "Documentation"]

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
        "database": "dataducks",
        "user": "postgres",
        "password": "12345678",
        "host": "localhost",
        "port": 5432,
    }
    conn = psycopg2.connect(**params)
    return conn

# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255))
#     size = db.Column(db.String(50))
#     location = db.Column(db.String(255))
#     date_of_creation = db.Column(db.String(50))
#     type = db.Column(db.String(50))
    
#     def __init__(self, name, size, location, date_of_creation, type):
#         self.name = name
#         self.size = size
#         self.location = location
#         self.date_of_creation = date_of_creation
#         self.type = type

# # Create the database tables
# db.create_all()

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
        conn = connect_to_db()
        process_files(dir_path, conn)               
                
    print("Folder's Files Added Succesfull")

def geojson(file_data):
    with app.app_context():
        new_file = Geojson_Metadata(
            file_location=file_data["File Location"],
            area = file_data["Area"],
            length = file_data["Length"],
            bounding_box= file_data["Bounding Box"],
            h3_index= file_data["File Data"]
        )                
        db_.session.add(new_file)
        db_.commit()
        
def tiff(file_data):
    with app.app_context():
        new_file = Tiff_Metadata(
            file_location=file_data["File Location"],
            geotransform=file_data["GeoTransform"],
            projection=file_data["Projection"],
            centerx=file_data["Center X"],
            centery=file_data["Center Y"],
            caption_conditional=file_data["Conditional Caption"],
            caption_unconditional=file_data["Unconditional Caption"],
            bounding_box=file_data["Bounding Box"]            
        )                
        db_.session.add(new_file)
        db_.commit()
        
def las(file_data):
    with app.app_context():
        new_file = Las_Metadata(
            file_location=file_data["File Location"],
            area = file_data["Area"],
            number_of_points=  file_data["Number Of Points"],
            offsets= file_data["Offsets"],
            min_bounds= file_data["Min Bounds"],
            scale_factors=file_data["Scale Factors"],
            max_bounds=file_data["Max Bounds"]
        )                
        db_.session.add(new_file)
        db_.commit()


if __name__ == "__main__":
    app.run(debug=True)
    

