import os
dir_path = "/home/skycoder/Videos/Webcam"
isdir = bool(os.path.isdir(dir_path))
pathExists = bool(os.path.exists(dir_path))
isFile = bool(os.path.isfile(dir_path))
print("isdir: ", isdir)
print("pathExists: ", pathExists)
print("isFile: ", isFile)
print()