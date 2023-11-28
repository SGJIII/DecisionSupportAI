# auth/oauth_handler.py
import requests
from config import EPIC_CLIENT_ID, EPIC_AUTH_ENDPOINT, EPIC_TOKEN_ENDPOINT, REDIRECT_URI

def get_auth_url(state):
    params = {
        "response_type": "code",
        "client_id": EPIC_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": state
    }
    return f"{EPIC_AUTH_ENDPOINT}?{urlencode(params)}"

def exchange_code_for_token(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": EPIC_CLIENT_ID
    }
    response = requests.post(EPIC_TOKEN_ENDPOINT, data=data)
    return response.json()
