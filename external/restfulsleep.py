import requests
from typing import Dict, Any, Tuple
from api.constants import APIConstants, ValidatedDict

class RestfulSleepAPI:
    RS_URL = None
    RS_PSK  = None

    @staticmethod
    def update_config(rs_config: Dict[str, Any]) -> None:
        server = rs_config.get('server', None)
        if server is None:
            raise Exception("Failed to initialize rs 'server'")
        
        psk = rs_config.get('psk', None)
        if psk is None:
            raise Exception("Failed to initialize rs 'psk'")
        
        RestfulSleepAPI.RS_URL = server
        RestfulSleepAPI.RS_PSK  = psk

    @staticmethod
    def build_headers(token: str = None) -> dict:
        headers = {
            "X-Unity-Key": RestfulSleepAPI.RS_PSK,
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    @staticmethod
    def _send_request(url: str, method: str, headers: dict, **kwargs) -> Tuple[bool, Any]:
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
        except requests.RequestException as e:
            return False, APIConstants.badEnd(str(e))
        
        if not response:
            return False, APIConstants.badEnd('No response from RS')
        
        return True, ValidatedDict(response.json())
    
    @staticmethod
    def _process_response(data: ValidatedDict) -> Tuple[bool, Any]:
        if data.get_str('status') != "success":
            return False, APIConstants.badEnd(f'RS Error: {data.get_str("error_code")}')
        
        return True, ValidatedDict(data.get_dict('data'))
    
    @classmethod
    def get_token_from_code(cls, code: int) -> Tuple[bool, Any]:
        request_data = {"code": code}
        success, response = cls._send_request(f"{cls.RS_URL}/v1/oauth/token/unity", "POST", cls.build_headers(), json=request_data)
        
        if not success:
            return success, response
        
        success, data = cls._process_response(response)
        token = data.get('token', None)
        user_id = data.get('userId', None)
        if not token or not user_id:
            return False, APIConstants.badEnd('No token or userId provided!')
        
        return success, ValidatedDict(data)
    
    @classmethod
    def delete_token(cls, token: str) -> Tuple[bool, Any]:
        success, _ = cls._send_request(f"{cls.RS_URL}/v1/oauth/token/unity", "DELETE", cls.build_headers(token))
        
        return success, None
    
    @classmethod
    def get_user_from_token(cls, token: str) -> Tuple[bool, ValidatedDict]:
        success, response = cls._send_request(f"{cls.RS_URL}/v1/user?noScores=true", "GET", cls.build_headers(token))
        
        if not success:
            return success, response
        
        return cls._process_response(response)
    
    @classmethod
    def get_user_from_id(cls, token: str, user_id: int, min: bool = False) -> Tuple[bool, ValidatedDict]:
        success, response = cls._send_request(f"{cls.RS_URL}/v1/user{'/minified' if min else ''}?noScores=true&userId={user_id}", "GET", cls.build_headers(token))
        
        if not success:
            return success, response
        
        return cls._process_response(response)
    
    @classmethod
    def get_user_from_name(cls, token: str, name: str) -> Tuple[bool, ValidatedDict]:
        success, response = cls._send_request(f"{cls.RS_URL}/v1/user/minified?noScores=true&username={name}", "GET", cls.build_headers(token))
        
        if not success:
            return success, response
        
        return cls._process_response(response)