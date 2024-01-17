import os
import pathlib
import json
from datetime import datetime
from conversion import process_folder

def extract_metadata(root_directory):
    metadata = []
    file_id = 1  # Initialize the counter for file IDs
    for folder_name, subfolders, filenames in os.walk(root_directory):
        for filename in filenames:
            file_path = os.path.join(folder_name, filename)
            if os.path.isfile(file_path):
                file_stats = os.stat(file_path)

                file_info = {
                    "File ID": file_id,  # Assign the file ID
                    "File Name": os.path.basename(file_path),
                    "File Path": file_path,
                    "File Type": pathlib.Path(file_path).suffix,
                    "File Size": file_stats.st_size,
                    "Date of Creation": datetime.fromtimestamp(
                        file_stats.st_ctime
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "Last Accessed": datetime.fromtimestamp(
                        file_stats.st_atime
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                }
                
                output_folder = os.path.join(root_directory, "converted_files") # Read folder for processing
                not_processed_folder = os.path.join(root_directory, "not_processed") # TODO
                
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                if not os.path.exists(not_processed_folder):
                    os.makedirs(not_processed_folder)
                    
                process_folder(filename==filename, folder_path=folder_name, output_folder=output_folder, not_processed_folder=not_processed_folder)
                metadata.append(file_info)
                
                file_id += 1  # Increment the file ID for the next file
    return metadata

def save_metadata_to_json(directory, metadata):
    metadata_dir = os.path.join(directory, "metadata", "common_metadata")
    os.makedirs(metadata_dir, exist_ok=True)
    json_path = os.path.join(metadata_dir, "metadata.json")
    with open(json_path, "w") as json_file:
        json.dump(metadata, json_file, indent=4)

# Usage example
# root_directory = "/path/to/your/directory"  # Root directory
# metadata = extract_metadata(root_directory)
# save_metadata_to_json(root_dire ctory, metadata)



