import os
import yaml
def read_yaml_file(file_path):
    if not os.path.exists(file_path):
        raise ValueError("The provided source path does not exist")
    with open(file_path, 'r') as file:
        data = list(yaml.safe_load_all(file))
    return data
def read_placement_file(file_path):
    file_data = read_yaml_file(file_path)
    for placement in file_data:
        print(f"Placement Names {placement['company']['name']}")

read_placement_file("data/CV_Resources/Personal/placements.yaml")