"""
This module contains the function definitions used to retrieve log-in information and authentication tokens.
"""

import requests as rq
import json

def prepare_log_in_info() -> tuple[str, str]:
    """
    Loads login credentials from a local JSON config file.
    Switch to environmental variables if moving to a cloud VM or docker.
    """
    with open(r"path.json", 'r') as f:
        config = json.load(f)

    username = config['username']
    password = config['password']
    return(username, password)

def get_auth_token(username: str, password: str) -> str:
    '''
    Get an auth token. Note: This is how the API is designed. It expects the username and password as url parameters.
    '''
    url = f'https://www.tourmis.info/api.pl?id={username}&pw={password}'
    result = rq.get(url)
    token = result.content.decode('ISO-8859-1').split('<token>')[1].split('</token>')[0]
    return(token)