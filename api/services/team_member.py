from flask_restful import Resource
from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.endpoints.team import TeamData
from api.data.endpoints.team_member import TeamMemberData
from external.restfulsleep import RestfulSleepAPI

class TeamMember(Resource):
    def put(self, team_id: int):
        session_state, session = RequestPreCheck.get_session()
        if not session_state:
            return session
        
        data_state, data = RequestPreCheck.check_data({'username': str})
        if not data_state:
            return APIConstants.badEnd('data not provided')
        
        user_id = session.get_int('id')
        if not user_id:
            return APIConstants.badEnd('user not provided')
        
        try:
            team_id = int(team_id)
        except:
            return APIConstants.badEnd('team is not int compatible!')
        
        team = TeamData.get_team(team_id)
        if not team:
            return APIConstants.badEnd('team not found')
        
        if user_id != team['owner']:
            admin_state, error = RequestPreCheck.check_admin(session)
            if not admin_state:
                return APIConstants.badEnd(error)

        user_state, found_user = RestfulSleepAPI.get_user_from_name(
            session.get_str('access_token'),
            data.get_str('username')
        )
        if not user_state:
            return found_user

        member_state = TeamMemberData.put_member(team_id, found_user.get_int('id'))
        if member_state:
            return APIConstants.goodEnd({})
        else:
            return APIConstants.badEnd('Failed to update team member!')
        
    def delete(self, team_id: int):
        session_state, session = RequestPreCheck.get_session()
        if not session_state:
            return session
        
        data_state, data = RequestPreCheck.check_data({'userId': int})
        if not data_state:
            return APIConstants.badEnd('data not provided')
        
        user_id = session.get_int('id')
        if not user_id:
            return APIConstants.badEnd('user not provided')
        
        try:
            team_id = int(team_id)
        except:
            return APIConstants.badEnd('team is not int compatible!')
        
        team = TeamData.get_team(team_id)
        if not team:
            return APIConstants.badEnd('team not found')
        
        if user_id != team['owner']:
            admin_state, error = RequestPreCheck.check_admin(session)
            if not admin_state:
                return APIConstants.badEnd(error)

        member_state = TeamMemberData.remove_member(team_id, data.get_int('userId'))
        if member_state:
            return APIConstants.goodEnd({})
        else:
            return APIConstants.badEnd('Failed to update team member!')