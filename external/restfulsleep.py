import requests
from requests import Response
from typing import Dict, Any
from api.constants import APIConstants, ValidatedDict

class RestfulSleepAPI():
    RS_URL = None
    RS_PSK = None

    @staticmethod
    def update_config(rs_config: Dict[str, Any]) -> None:
        server = rs_config.get('server', None)
        if server == None:
            raise Exception("Failed to initialize rs 'server'")
        
        psk = rs_config.get('psk', None)
        if psk == None:
            raise Exception("Failed to initialize rs 'psk'")
        
        RestfulSleepAPI.RS_URL = server
        RestfulSleepAPI.RS_PSK = psk

    @staticmethod
    def build_headers(token: str = None) -> dict:
        headers = {
            "X-Unity-Key": RestfulSleepAPI.RS_PSK,
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    @staticmethod
    def get_token_from_code(code: int) -> tuple[bool, Any]:
        request_data = {
            "code": code
        }
        response: Response = None
        try:
            response = requests.post(
                f"{RestfulSleepAPI.RS_URL}/v1/oauth/token/unity",
                json=request_data,
                headers=RestfulSleepAPI.build_headers()
            )
        except requests.RequestException as e:
            return (False, APIConstants.badEnd(str(e)))
        
        if not response:
            return (False, APIConstants.badEnd('No response from RS'))
        
        responseData = ValidatedDict(response.json())
        if responseData.get_str('status') != "success":
            return (False, APIConstants.badEnd(f'RS Error: {responseData.get_str('error_code')}'))
        
        data = responseData.get_dict('data')
        token = data.get_str('token', None)
        if not token:
            return (False, APIConstants.badEnd('No token provided!'))
        user_id = data.get_int('userId', None)
        if not user_id:
            return (False, APIConstants.badEnd('No userId provided!'))
        return (True, data)

    @staticmethod
    def delete_token(token: str) -> tuple[bool, Any]:
        response: Response = None
        try:
            response = requests.delete(
                f"{RestfulSleepAPI.RS_URL}/v1/oauth/token/unity",
                headers=RestfulSleepAPI.build_headers(token)
            )
        except requests.RequestException as e:
            return (False, APIConstants.badEnd(str(e)))
        
        if not response:
            return (False, APIConstants.badEnd('No response from RS'))
        
        return (True, None)

    @staticmethod
    def get_user_from_token(token: str) -> tuple[bool, dict]:
        response: Response = None
        try:
            response = requests.get(f"{RestfulSleepAPI.RS_URL}/v1/user?noScores=true", headers=RestfulSleepAPI.build_headers(token))
        except requests.RequestException as e:
            return (False, APIConstants.badEnd(str(e)))
        
        responseData = ValidatedDict(response.json())
        if responseData.get_str('status') != "success":
            return (False, APIConstants.badEnd(f'RS Error: {responseData.get_str('error_code')}'))
        
        data = responseData.get_dict('data')
        return (True, data)