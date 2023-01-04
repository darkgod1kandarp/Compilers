def converting_data_uri_file(encoded_file_data  ,  file_name):

    
    with  open(file_name , 'w') as f:
        f.write(encoded_file_data)
    
converting_data_uri_file( "checking.py",  "op.py")


