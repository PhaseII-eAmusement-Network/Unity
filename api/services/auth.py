from flask import make_response
from flask_restful import Resource
from api.constants import APIConstants, ValidatedDict
from api.precheck import RequestPreCheck
from api.data.endpoints.session import UserSession
from external.restfulsleep import RestfulSleepAPI

class OAuthCallback(Resource):
    def post(self):
        (data_state, data) = RequestPreCheck.checkData({'code': int})
        if not data_state:
            return APIConstants.badEnd('data not provided')
        
        code = data.get_int('code')
        if not code:
            return APIConstants.badEnd('code not provided in data')
        
        token_data: ValidatedDict = None
        try:
            (token_state, token_data) = RestfulSleepAPI.get_token_from_code(code)
            if not token_state:
                return token_data
        except Exception as e:
            return APIConstants.badEnd(e)
        
        session_token = UserSession.create_session(token_data.get_int('userId'), token_data.get_str('token'))
        
        payload = APIConstants.goodEnd({'userId': token_data.get_int('userId')})
        resp = make_response(payload)
        resp.set_cookie(
            "Unity-Auth-Key",
            UserSession.AES.encrypt(session_token),
            (90 * 86400),
            httponly=True,
            samesite="Strict",
            secure=UserSession.SECURE_COOKIE
        )
        return resp

class AuthSession(Resource):
    def get(self):
        session_state, session = RequestPreCheck.get_session()
        if not session_state:
            return session
        
        return {'status': 'success', 'activeSession': session.get_bool('active'), 'userId': session.get_int('id')}
    
    def delete(self):
        session_state, session = RequestPreCheck.get_session()
        if not session_state:
            return session
        
        token_state, result = RestfulSleepAPI.delete_token(session.get_str('access_token'))
        if not token_state:
            return result
        UserSession.delete_session(session['token'])

        return APIConstants.goodEnd({})
