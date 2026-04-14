from flask_restful import Resource
from api.constants import APIConstants
from api.precheck import RequestPreCheck
from api.data.endpoints.team import TeamData
from api.data.endpoints.team_member import TeamMemberData
from api.data.endpoints.application import ApplicationData
from external.restfulsleep import RestfulSleepAPI

class Team(Resource):
    def get(self, team_id):
        sessionState, session = RequestPreCheck.get_session()
        if not sessionState:
            return session
        
        user_id = session.get_int('id')
        if not user_id:
            return APIConstants.badEnd('user not provided')
        access_token = session.get_str('access_token')

        try:
            team_id = int(team_id)
        except:
            return APIConstants.badEnd('team is not int compatible!')
        
        team = TeamData.get_team(team_id)
        if not team:
            return APIConstants.badEnd('team not found')
        
        owner_id = team['owner']

        if owner_id != 0:
            state, owner_data = RestfulSleepAPI.get_user_from_id(access_token, owner_id, True)
            if not state:
                return owner_data
            team['ownerData'] = owner_data
        else:
            team['ownerData'] = {
                'name': 'PhaseII'
            }
        
        if user_id != owner_id:
            member = TeamMemberData.get_member_state(team_id, user_id)
            if not member:
                admin_state, error = RequestPreCheck.check_admin(session)
                if not admin_state:
                    return APIConstants.badEnd(error)
        
        members = TeamMemberData.get_team_members(team_id)
        if members:
            juiced_members = []
            for member in members:
                state, member_data = RestfulSleepAPI.get_user_from_id(access_token, member, True)
                if state:
                    member_data['email'] = None
                    member_data['data'] = None
                    juiced_members.append(member_data)
            team['members'] = juiced_members

        applications = ApplicationData.get_all_apps(team_id)
        if len(applications):
            team['applications'] = applications

        return APIConstants.goodEnd(team)

    def post(self, team_id):
        sessionState, session = RequestPreCheck.get_session()
        if not sessionState:
            return session
        
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
            member = TeamMemberData.get_member_state(team_id, user_id)
            if not member:
                admin_state, error = RequestPreCheck.check_admin(session)
                if not admin_state:
                    return APIConstants.badEnd(error)
        
        data_state, data = RequestPreCheck.check_data({'name': str, 'about':  str})
        if not data_state:
            return APIConstants.badEnd('data not provided')

        new_name = data.get_str('name')
        if not len(new_name):
            return APIConstants.badEnd('no name provided')
        
        new_about = data.get_str('about')
        if not len(new_about):
            return APIConstants.badEnd('no about provided')

        update_result = TeamData.update_team(
            team_id,
            data.get_str('name'),
            {
                'about': data.get_str('about')
            }
        )

        if update_result:
            return APIConstants.goodEnd({})
        else:
            return APIConstants.badEnd('Failed to update team!')

class NewTeam(Resource):
    def put(self):
        sessionState, session = RequestPreCheck.get_session()
        if not sessionState:
            return session
        
        data_state, data = RequestPreCheck.check_data({'name': str, 'about':  str})
        if not data_state:
            return APIConstants.badEnd('data not provided')
        
        user_id = session.get_int('id')
        if not user_id:
            return APIConstants.badEnd('user not provided')
        
        internal = data.get_bool('internal', False)
        if internal:
            admin_state, error = RequestPreCheck.check_admin(session)
            if not admin_state:
                return APIConstants.badEnd(error)
            user_id = 0 # Internal apps are tied to user_id 0

        team_id = TeamData.new_team(
            data.get_str('name'),
            user_id,
            {
                'about': data.get_str('about')
            }
        )

        if team_id:
            return APIConstants.goodEnd({'teamId': team_id})
        else:
            return APIConstants.badEnd('Failed to create team!')
        