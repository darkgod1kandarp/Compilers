import os 
def get_folder_data(folder_path):
    folder_data = {}
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            with open(file_path, 'rb') as f:
                file_data = f.read()
            folder_data[file_path] = file_data
        if dirs:
            print(dirs)
    # return folder_data
print(get_folder_data("."))