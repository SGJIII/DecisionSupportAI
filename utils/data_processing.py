import csv

def load_emr_data(file_path):
    emr_data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            emr_data.append(row)
    return emr_data
