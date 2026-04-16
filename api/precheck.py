from flask import request
from typing import Tuple
import validators
from api.constants import APIConstants, AppIntents, ValidatedDict
from api.data.endpoints.session import UserSession
from external.restfulsleep import RestfulSleepAPI

class RequestPreCheck:
    def get_session() -> Tuple[bool, ValidatedDict]:
        token = request.cookies.get('Unity-Auth-Key')
        if not token:
            auth = RequestPreCheck.get_authorization()
            if auth:
                return auth
            return (False, APIConstants.softEnd('No Unity-Auth-Key provided!'))
        
        session = UserSession.check_session(token)
        if not session or session.get('active') != True:
            return (False, APIConstants.badEnd('No session found!'))
        session['token'] = token
        return (True, session)
    
    def get_authorization() -> Tuple[bool, ValidatedDict]:
        rs_key = None
        try:
            rs_key = request.headers['X-RS-Key']
        except Exception as e:
            return (False, APIConstants.badEnd(str(e)))
        
        if rs_key:
            if rs_key != RestfulSleepAPI.RS_PSK:
                return (False, APIConstants.softEnd('X-RS-Key provided is incorrect'))
            return (True, ValidatedDict({'id': 0, 'appId': 'rs'}))
    
    def check_admin(session: ValidatedDict) -> Tuple[bool, ValidatedDict]:
        '''
        Check if a user is an admin. Returns a bool and a response dict.
        '''
        state, user = RestfulSleepAPI.get_user_from_token(session.get_str('access_token'))
        if not state:
            return user

        if not user.get_bool("admin", False):
            return (False, APIConstants.badEnd('You must have administrative rights.'))
        
        return (True, None)
    
    def check_data(keys: dict[str, type] = {}) -> Tuple[bool, ValidatedDict]:
        '''
        Check if JSON data was sent. If found, return it as a ValidatedDict.

        Optionally can be given a dict of {key: type} to check for specific elements.
        Returns an error for the missing/incorrect keys.
        '''
        data = request.get_json(silent=True)
        if data is None:
            return False, APIConstants.badEnd("No JSON data was sent!")

        data = ValidatedDict(data)

        type_getters = {
            str: data.get_str,
            int: data.get_int,
            bool: data.get_bool,
            bytes: data.get_bytes,
        }

        for key, key_type in keys.items():
            getter = type_getters.get(key_type)
            if getter and getter(key, None) is None:
                try:
                    changed_val = key_type(data.get(key, None))
                    data[key] = changed_val
                except:
                    return False, APIConstants.badEnd(f"`{key}` type {key_type.__name__} not found!\nFailed to find and convert type.")

        return True, data
    
    def check_args(keys: dict[str, type] = {}) -> Tuple[bool, ValidatedDict]:
        '''
        Check if args were sent. If found, return them as a ValidatedDict.

        Optionally can be given a dict of {key: type} to check for specific elements.
        Returns an error for the missing/incorrect keys.
        '''
        data = request.args
        if data is None:
            return False, APIConstants.badEnd("No args sent!")

        data = ValidatedDict(data)

        type_getters = {
            str: data.get_str,
            int: data.get_int,
            bool: data.get_bool,
            bytes: data.get_bytes,
        }

        for key, key_type in keys.items():
            getter = type_getters.get(key_type)
            if getter and getter(key, None) is None:
                try:
                    changed_val = key_type(data.get(key, None))
                    data[key] = changed_val
                except:
                    return False, APIConstants.badEnd(f"`{key}` type {key_type.__name__} not found!\nFailed to find and convert type.")

        return True, data
    
    def is_valid_url(url: str, force_https: bool = False) -> bool:
        prefixes = ("http://", "https://")
        if (force_https or APIConstants.FORCE_HTTPS_CALLBACKS):
            prefixes = ("https://")

        if not url.startswith(prefixes):
            return False

        if APIConstants.BYPASS_CALLBACK_VALIDATION:
            return True

        return validators.url(url)
    
    def validate_intents(intent_dict: dict):
        if not isinstance(intent_dict, dict):
            return False, "intents must be a dictionary"

        for key, value in intent_dict.items():
            if key not in AppIntents.INTENT_MAP:
                return False, f"invalid intent: {key}"
            
            if not isinstance(value, bool):
                return False, f"intent '{key}' must be boolean"

        return True, None