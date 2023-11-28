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

PORT = 1555

HOST = '127.0.0.1'

EPIC_CLIENT_ID_PROD = 'c147f9ee-2e8a-41fc-acbf-c57e0a228172'
EPIC_CLIENT_ID_DEV = '79360b8f-615c-40d4-b6b2-23b7174af456'
EPIC_AUTH_ENDPOINT = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize"
EPIC_TOKEN_ENDPOINT = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
REDIRECT_URI = "your_redirect_uri"
# Add other configuration variables as needed
