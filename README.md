### CurnexaHealthAI

## Overview

CurnexaHealthAI is a healthcare AI platform designed to integrate with Epic EMR systems, utilize federated learning, and leverage advanced NLP capabilities through Meta's LLaMA. This platform aims to provide AI-driven clinical decision support by analyzing medical data and literature, and it now includes OAuth integration for secure access to Epic's FHIR API.

## Project Structure

app/: Core application code, including Flask web server for OAuth integration.
data/: Datasets, including data fetched from PubMed or Epic EMR.
utils/: Utility scripts and helper functions.
models/: Includes the LLaMA chat model integration.
fhir/: FHIR API client for interacting with Epic EMR systems.
tests/: Unit tests and integration tests.
docs/: Additional documentation, API guides, etc.

## Setup

# Prerequisites

Python 3.x
pip (Python package manager)
Flask
Access to Epic's FHIR API and Meta's LLaMA
Installation
Clone the repository:

```
git clone https://github.com/SGJIII/CurnexaHealthAI.git
cd CurnexaHealthAI
```

#Install dependencies:

```
pip install -r requirements.txt
```

# Auth Integration with Epic EMR

The project now includes OAuth integration for secure access to Epic's FHIR API. This allows the platform to fetch patient data directly from Epic EMR systems, ensuring data privacy and security.

# PubMed API Integration

Our project integrates with the PubMed API to fetch relevant medical articles. This integration allows us to extract and parse various pieces of information from the articles, which can be used for further analysis and integration into our system.

# Data Extracted

The following data points are extracted from each PubMed article:

Title, Abstract, Authors, Publication Date, Journal Name, Keywords, DOI, Affiliations, MeSH Terms, Citations, Full Text Links, PMID.
Usage
To use the PubMed API integration, run the pubmed_fetch.py script with a query term. For example:

python utils/pubmed_fetch.py "diabetes"

This will fetch articles related to diabetes and output the extracted data to the console.

## Next Steps

Implement and Test fhir.fhir_client: Complete the implementation of the FHIR API client and test its functionality.
Integrate and Test New Functions: Ensure that all new functions are properly integrated and tested within the application.
Run and Test Flask Application: Test the OAuth flow and the overall functionality of the Flask application.
Perform End-to-End Testing: Simulate the complete workflow from OAuth authentication to data processing and output.
Enhance Error Handling and Logging: Implement robust error handling and add logging for better monitoring.
Ensure Security and Compliance: Review security aspects and ensure compliance with healthcare regulations.
Optimize and Refactor Code: Look for opportunities to optimize and refactor the code.
Document and Prepare for Deployment: Update documentation and prepare the application for deployment.
Gather Feedback and Iterate: Collect feedback and iterate on the application based on user input.

## TODO

Implement fhir.fhir_client module for fetching patient data.
Define and test fetch_articles_for_record and generate_unique_state functions.
Enhance error handling and security measures.
Document the OAuth flow and FHIR API integration.
Prepare for deployment and conduct thorough testing.
This updated README reflects the current state of your project and outlines the next steps to take your application towards completion and deployment.
