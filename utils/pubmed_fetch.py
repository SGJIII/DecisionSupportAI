import requests
import xml.etree.ElementTree as ET
import time
import sys  # Import sys to handle command-line arguments
from dotenv import load_dotenv
import os
from utils.data_processing import load_emr_data

load_dotenv()
api_key = os.getenv('PUBMED_API_KEY')

def fetch_pubmed_data(age, gender, medications=None, allergies=None, conditions=None, social_history=None, max_results=1):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    api_key = os.getenv('PUBMED_API_KEY')

    # Constructing a detailed query
    query_parts = [f"age:{age}", f"gender:{gender}"]
    if medications:
        query_parts.extend(medications)  # Assuming medications is a list of strings
    if allergies:
        query_parts.extend(allergies)  # Assuming allergies is a list of strings
    if conditions:
        query_parts.extend(conditions)  # Assuming conditions is a list of strings
    if social_history:
        query_parts.extend(social_history)  # Assuming social_history is a list of strings

    detailed_query = " AND ".join([part for part in query_parts if part])
    encoded_query = requests.utils.quote(detailed_query)

    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={encoded_query}&retmax={max_results}&apikey={api_key}"
    
    try:
        response = requests.get(search_url)
        time.sleep(0.1)  # Adjusted rate limiting for 10 requests per second
        response.raise_for_status()

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            article_ids = [id_elem.text for id_elem in root.findall('.//IdList/Id')]
            return article_ids
        else:
            print(f"Error: {response.status_code}")
            return None
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    return None
    
def fetch_article_details(article_ids):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    ids_string = ','.join(article_ids)
    fetch_url = f"{base_url}efetch.fcgi?db=pubmed&id={ids_string}&retmode=xml&apikey={api_key}"
    
    try:
        response = requests.get(fetch_url)
        time.sleep(0.1)  # Adjusted rate limiting for 10 requests per second
        response.raise_for_status()

        if response.status_code == 200:
            try:
                # Parse the XML response
                root = ET.fromstring(response.content)
                articles = []
                for article in root.findall('.//PubmedArticle'):
                    title = article.find('.//ArticleTitle').text
                    abstract_element = article.find('.//Abstract/AbstractText')
                    abstract = abstract_element.text if abstract_element is not None else "No abstract available"
                    articles.append({'title': title, 'abstract': abstract})
                return articles
            except ET.ParseError as e:
                print("Error parsing XML:", e)
                return None
        else:
            print(f"Error: {response.status_code}")
            return None
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    return None

if __name__ == "__main__":
    emr_data = load_emr_data('../data/mock_emr.csv')
    if emr_data is not None:
        for index, row in emr_data.iterrows():
            # Assuming there's a column 'query' in your CSV
            query = row['query']
            article_ids = fetch_pubmed_data(query)
            if article_ids:
                articles = fetch_article_details(article_ids)
                for article in articles:
                    print("Title:", article['title'])
                    print("Abstract:", article['abstract'])
                    print("-----")
