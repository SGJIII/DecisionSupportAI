from models.clinical_bert import query_clinicalbert
from utils.data_processing import load_emr_data

def main():
    emr_data = load_emr_data("data/fake_emr_data.csv")
    for record in emr_data:
        result = query_clinicalbert(record['text_field'])
        print(result)

if __name__ == "__main__":
    main()
