import requests
import os
from flask import current_app, session
from config import EPIC_CLIENT_ID_DEV, EPIC_AUTH_ENDPOINT, EPIC_TOKEN_ENDPOINT, REDIRECT_URI_DEV
import hashlib
import base64
from urllib.parse import urlencode
from supabase import create_client, Client

# Load client secret from environment variables
EPIC_CLIENT_SECRET = os.environ.get('EPIC_CLIENT_SECRET')

# Supabase configuration (ensure this is accessible)
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_code_verifier():
    """
    Generates a 'code_verifier' for PKCE.
    """
    return base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8').rstrip("=")

def generate_code_challenge(code_verifier):
    """
    Generates a 'code_challenge' based on the 'code_verifier'.
    """
    sha256 = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(sha256).decode('utf-8').rstrip("=")

def get_auth_url(state, code_challenge):
    epic_user_id = session.get('epic_user_id')
    if epic_user_id:
        # Fetch user from Supabase
        response = supabase.table('users').select('*').eq('epic_user_id', epic_user_id).execute()
        if response.data:
            user = response.data[0]
            base_url = user.get('hospital_endpoint', current_app.config['DEFAULT_EPIC_FHIR_BASE_URL'])
        else:
            base_url = current_app.config['DEFAULT_EPIC_FHIR_BASE_URL']
    else:
        # Use endpoint from session or default
        base_url = session.get('hospital_endpoint', current_app.config['DEFAULT_EPIC_FHIR_BASE_URL'])

    params = {
        "response_type": "code",
        "client_id": current_app.config['EPIC_CLIENT_ID_DEV'],
        "redirect_uri": current_app.config['REDIRECT_URI_DEV'],
        "state": state,
        "scope": "openid",
        # "code_challenge": code_challenge,
        # "code_challenge_method": "S256",
        "aud": base_url
    }
    return f"{current_app.config['EPIC_AUTH_ENDPOINT']}?{urlencode(params)}"

def exchange_code_for_token(code, code_verifier):
    """
    Exchanges the authorization code for an access token.
    """
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": current_app.config['REDIRECT_URI_DEV'],
        "client_id": current_app.config['EPIC_CLIENT_ID_DEV'],
        "client_secret": os.environ.get('EPIC_CLIENT_SECRET'),
        "code_verifier": code_verifier
    }
    response = requests.post(current_app.config['EPIC_TOKEN_ENDPOINT'], data=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to exchange code for token: {response.text}")
