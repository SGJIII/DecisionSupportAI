import pandas as pd
import csv

def load_emr_data(file_path):
    data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

# Example usage
if __name__ == "__main__":
    emr_data = load_emr_data('../data/mock_emr.csv')
    if emr_data:
        # Print first few records
        for record in emr_data[:5]:  # Adjust the number to print as many records as you want
            print(record)
