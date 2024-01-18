import pickle
# type_dict=[]
# with open('data_extensions.pkl', 'wb') as file:
#     pickle.dump(type_dict, file)
   
file_data = {
    "total_file" : 23,
        "file_types_len" : 20,
        "file_types" : [],
        "file_types_distribution" : [8, 4, 2, 9],
        "max" : 24.24,
        "min" : 0,
        "size0" : 5,
        "size1" : 8,
        "size2" : 11,
        "size3" : 0
} 
with open('analytics_file.pkl', 'wb') as file:
    pickle.dump(file_data, file)


# with open('analytics_file.pkl', 'rb') as file:
#     analytics = pickle.load(file)
    
# print(analytics["size0"])
# analytics["min"]+=1
# print(analytics["min"])