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

EPIC_CLIENT_ID = 'your_epic_client_id'
EPIC_CLIENT_SECRET = 'your_epic_client_secret'
EPIC_TOKEN_URL = 'https://example.epic.com/token'
EPIC_FHIR_URL = 'https://example.epic.com/fhir'
# Add other configuration variables as needed
