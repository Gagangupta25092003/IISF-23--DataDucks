import pickle
# type_dict=[]
# with open('data_extensions.pkl', 'wb') as file:
#     pickle.dump(type_dict, file)
    
with open('data_extensions.pkl', 'rb') as file:
    type_dict = list(pickle.load(file))
    
print(type_dict)