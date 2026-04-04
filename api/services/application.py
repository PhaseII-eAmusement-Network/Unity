from flask_restful import Resource
from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.endpoints.team import TeamData
from api.data.endpoints.team_member import TeamMemberData
from external.restfulsleep import RestfulSleepAPI

class Application(Resource):
    def get(self, team_id, app_id):
        sessionState, session = RequestPreCheck.get_session()
        if not sessionState:
            return session
        
        print((team_id, app_id))