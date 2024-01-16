from flask import Flask, request, jsonify, render_template
import os, datetime, psycopg2
from flask_sqlalchemy import SQLAlchemy
from datetime import date as dt
from datetime import datetime
from flask_cors import CORS
import json

ext_dir=[[".jpg", ".png", ".jpeg"], [".pdf"],[".txt"], [".py", ".cpp", ".js", ".java", ".css", ".html", ".json"], [".xlsx"], [".csv"], [".pptx"], [".doc"]]
ext_dir_names = ["Image", "PDF", "Text", "Code Files", "Excel", "CSV", "Presentation", "Documentation"]

def convertDate(timestamp):
    d = datetime.datetime.utcfromtimestamp(timestamp)
    formatedDate = d.strftime('%b %d, %Y')

    return formatedDate

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost/dataducks'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    size = db.Column(db.String(50))
    location = db.Column(db.String(255))
    date_of_creation = db.Column(db.String(50))
    type = db.Column(db.String(50))
    
    def __init__(self, name, size, location, date_of_creation, type):
        self.name = name
        self.size = size
        self.location = location
        self.date_of_creation = date_of_creation
        self.type = type

# # Create the database tables
# db.create_all()

@app.route("/")
def index():
    return "Welcome Dataducks back-end Server"  

@app.route("/upload", methods=["POST"])
def add_dir():
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
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                date = dt(2024,1,8)
                ext = os.path.splitext(file)[1]
                print(ext)
                file_type = "Others"
                for i in range(len(ext_dir)):
                    if ext in ext_dir[i]:
                        file_type = ext_dir_names[i]                   
                
                file_metadata = {
                    "Name": file,
                    "Location": file_path,
                    "Size": size,
                    "Date of creation": date,
                    "Type": file_type
                }
                with app.app_context():
                    new_user = User(
                        name=file,
                        size=size,
                        location=file_path,
                        date_of_creation="2024-01-08",
                        type=file_type
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    print(new_user)
                
                dir_metadata.append(file_metadata)
                
         
        return jsonify(response_data2)
    
@app.route("/get_database")
def get_files():
    # Retrieve all rows from the table
    all_users = User.query.all()

    formatted_data = [{'id': user.id, 'name': user.name, 'size': user.size, 'location': user.location, 'date_of_creation': user.date_of_creation, 'type': user.type} for user in all_users]

    # Return the data as JSON
    return jsonify(users=formatted_data)

if __name__ == "__main__":
    app.run(debug=True)
    

