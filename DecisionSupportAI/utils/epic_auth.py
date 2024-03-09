from requests_oauthlib import OAuth2Session
from flask import current_app

def get_epic_token():
    client_id = current_app.config['EPIC_CLIENT_ID']
    client_secret = current_app.config['EPIC_CLIENT_SECRET']
    token_url = current_app.config['EPIC_TOKEN_URL']

    epic = OAuth2Session(client_id)
    token = epic.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)

    return token['access_token']
