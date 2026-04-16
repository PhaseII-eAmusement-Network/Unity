from flask_restful import Resource

from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.endpoints.team import TeamData
from api.data.endpoints.team_member import TeamMemberData
from external.restfulsleep import RestfulSleepAPI

class UserAccount(Resource):
    def get(self):
        session_state, session = RequestPreCheck.get_session()
        if not session_state:
            return session
        
        (user_state, user_data) = RestfulSleepAPI.get_user_from_token(session.get_str("access_token"))
        if not user_state:
            return user_data
        
        user_id = session.get_int('id')
        
        teams = TeamData.get_all_teams(owner_id=user_id)
        if teams and len(teams):
            user_data['myTeams'] = teams

        joined_teams = TeamMemberData.get_member_teams(user_id)
        if joined_teams and len(joined_teams):
            juiced_teams = []
            for team in joined_teams:
                team_data = TeamData.get_team(team)
                juiced_teams.append(team_data)
            user_data['joinedTeams'] = juiced_teams

        if user_data.get_bool('admin'):
            admin_teams = TeamData.get_all_teams(owner_id=0)
            user_data['adminTeams'] = admin_teams

        return APIConstants.goodEnd(user_data)
