# CurnexaHealthAI

## Overview

CurnexaHealthAI is a healthcare AI platform designed to integrate with Epic EMR systems, utilize federated learning, and leverage advanced NLP capabilities through Meta's LLaMA. This platform aims to provide AI-driven clinical decision support by analyzing medical data and literature.

## Project Structure

- `app/`: Core application code.
- `data/`: Datasets, including data fetched from PubMed or Epic EMR.
- `utils/`: Utility scripts and helper functions.
- `tests/`: Unit tests and integration tests.
- `docs/`: Additional documentation, API guides, etc.

## Setup

### Prerequisites

- Python 3.x
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SGJIII/CurnexaHealthAI.git
   cd CurnexaHealthAI
   ```

## PubMed API Integration

Our project integrates with the PubMed API to fetch relevant medical articles. This integration allows us to extract and parse various pieces of information from the articles, which can be used for further analysis and integration into our system.

# Data Extracted

The following data points are extracted from each PubMed article:

- Title: The title of the article.
- Abstract: A summary of the article's content.
- Authors: Names of the authors.
- Publication Date: When the article was published.
- Journal Name: The journal in which the article appeared.
- Keywords: Key topics covered in the article.
- DOI: Digital Object Identifier for the article.
- Affiliations: Author affiliations.
- MeSH Terms: Medical Subject Headings associated with the article.
- Citations: Number of times the article has been cited.
- Full Text Links: URLs to access the full text of the article.
- PMID: PubMed's unique identifier for the article.
  Usage
  To use the PubMed API integration, run the pubmed_fetch.py script with a query term. For example:

`python utils/pubmed_fetch.py "diabetes"`

This will fetch articles related to diabetes and output the extracted data to the console.

## Customer Research Needed

- Work with dr. to understand what info from health record should be used for automatically creating a query to pubmed
- Work with dr. to understand what data points to extract from each PubMed articl

## TODO

- Move Hugging Face API key to env variable
