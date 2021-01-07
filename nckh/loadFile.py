import json
def read_file(file_name):
    data = {}
    with open(file_name,'r') as fr:
       data = fr.readlines()
    return data
