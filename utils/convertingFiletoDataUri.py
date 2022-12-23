def converting_file_data_uri(file_name:str) :
    with open(file_name, 'r') as f:
        data =  f.read()
    print(data)

converting_file_data_uri('testing.py')