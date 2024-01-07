from flask import Flask
import os, datetime

path = "/home/skycoder/Documents/Fitlivs"
dir_metadata = []
isdir = os.path.isdir(path)
pathExists = os.path.exists(path)
isFile = os.path.isfile(path)
ext_dir=[[".jpg", ".png", ".jpeg"], [".pdf"],[".txt"], [".py", ".cpp", ".js", ".java", ".css", ".html", ".json"], [".xlsx"], [".csv"], [".pptx"], [".doc"]]
ext_dir_names = ["Image", "PDF", "Text", "Code Files", "Excel", "CSV", "Presentation", "Documentation"]

def convertDate(timestamp):
    d = datetime.datetime.utcfromtimestamp(timestamp)
    formatedDate = d.strftime('%b %d, %Y')

    return formatedDate

app = Flask(__name__)

@app.route("/")
def index():
    if not pathExists:
        return "Invalid Path"
    elif isFile:
        return "Path should a directory not a File"
    else:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                date = convertDate(os.path.getmtime(file_path))
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
                
                dir_metadata.append(file_metadata)
            
        return dir_metadata

if __name__ == "__main__":
    app.run(debug=True)
    

