from flask_restful import Resource

from api.constants import APIConstants
from api.precheck import RequestPreCheck

from external.restfulsleep import RestfulSleepAPI

class UserAccount(Resource):
    def get(self):
        sessionState, session = RequestPreCheck.get_session()
        if not sessionState:
            return session
        
        (user_state, user_data) = RestfulSleepAPI.get_user_from_token(session.get_str("access_token"))
        if not user_state:
            return user_data
        
        return APIConstants.goodEnd(user_data)
