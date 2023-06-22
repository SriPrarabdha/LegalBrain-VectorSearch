import json
import os
import shutil
import os.path
import zipfile
#Path where all the jsons to be merged are kept
json_path = "C:/TensorLabsAI/Merge Json"
new_json = []
sum = 0
year_names = []
def create_zip_file(json_file_path):
    # Get the directory path and the JSON file name
    directory, json_file_name = os.path.split(json_file_path)

    # Create a ZIP file name based on the JSON file name
    zip_file_name = os.path.splitext(json_file_name)[0] + '.zip'

    # Create a new compressed ZIP file
    with zipfile.ZipFile(zip_file_name, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        # Add the JSON file to the ZIP file
        zipf.write(json_file_path, json_file_name)

    print(f'Created {zip_file_name} containing {json_file_name}.')
for files in os.listdir(json_path):
    (name, extension) = os.path.splitext(files)
    j = json_path + '/' + name + extension
    if extension == '.json':
        year_names.append(name[-4:])
        f = open(j)
        data = json.load(f)
        sum += len(data)
        print(len(data))
        for dics in data:
            new_json.append(dics)
year_names.sort()
with open("Json_data_" + year_names[0] + "_" + year_names[-1] +".json", "w") as file:
  data_j = json.dump(new_json , file, indent=4)
file.close()
k = open("Json_data_" + year_names[0] + "_" + year_names[-1] +".json")
hey = json.load(k)
print(len(hey), sum)
create_zip_file(json_path + '/' + "Json_data_" + year_names[0] + "_" + year_names[-1] +".json")
