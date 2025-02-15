import requests


async def api_authorization(username, password):
    _return = False

    data = {
        'client_id':'s21-open-api',
        'username':f'{username}',
        'password':f'{password}',
        'grant_type':'password'
    }

    response_api = requests.post("https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/token", data=data)
    
    if response_api.status_code == 200:
        _return = True
    
    return _return
