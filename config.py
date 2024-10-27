#config.py
# On production, all html/js/less are compiled and pre-minified and code-reload is not enabled.
PRODUCTION = False
# alias for the opposite of PRODUCTION state
DEVELOPMENT = not PRODUCTION

# Statement for enabling the development environment in flask
DEBUG = not PRODUCTION

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
APP_DIR = BASE_DIR + '/app'
VIEWS_DIR = APP_DIR + '/views'
MIN_DIR = APP_DIR + '/build'

PORT = 8080

HOST = '127.0.0.1'

EPIC_CLIENT_ID_PROD = 'e4a1fcac-86fc-40b4-b1ab-a8e34f5d626e'
EPIC_CLIENT_ID_DEV = 'dac06186-2fc7-46f6-9d52-c700e0555077'
EPIC_AUTH_ENDPOINT = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize"
EPIC_TOKEN_ENDPOINT = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
REDIRECT_URI_DEV = "https://939d-104-232-123-102.ngrok-free.app/callback"  # Update with your actual redirect URI
REDIRECT_URI_PROD = "https://cds.curnexa.org/callback"


# Add the Epic FHIR API base URL
# Default EPIC FHIR Base URL
DEFAULT_EPIC_FHIR_BASE_URL = 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/'

# Update the Epic FHIR API base URL
EPIC_FHIR_BASE_URL = DEFAULT_EPIC_FHIR_BASE_URL  # This will be overridden per user session