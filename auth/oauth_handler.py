import requests
from urllib.parse import urlencode
import os
from flask import current_app
from config import EPIC_CLIENT_ID_DEV, EPIC_AUTH_ENDPOINT, EPIC_TOKEN_ENDPOINT, REDIRECT_URI_DEV

# Load client secret from environment variables
EPIC_CLIENT_SECRET = os.environ.get('EPIC_CLIENT_SECRET')

def get_auth_url(state):
    """
    Generates the authorization URL for the OAuth flow.
    """
    params = {
        "response_type": "code",
        "client_id": current_app.config['EPIC_CLIENT_ID_DEV'],  # Use the sandbox client ID
        "redirect_uri": current_app.config['REDIRECT_URI_DEV'],  # Use the sandbox redirect URI
        "state": state,
        "scope": "patient.read"  # Add other scopes as needed
    }
    return f"{current_app.config['EPIC_AUTH_ENDPOINT']}?{urlencode(params)}"

def exchange_code_for_token(code):
    """
    Exchanges the authorization code for an access token.
    """
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": current_app.config['REDIRECT_URI_DEV'],  # Use the sandbox redirect URI
        "client_id": current_app.config['EPIC_CLIENT_ID_DEV'],  # Use sandbox client ID
        "client_secret": current_app.config['EPIC_CLIENT_SECRET']  # Use the client secret from config
    }
    response = requests.post(current_app.config['EPIC_TOKEN_ENDPOINT'], data=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to exchange code for token: {response.text}")

# Additional functions or code related to OAuth can be added here if needed


