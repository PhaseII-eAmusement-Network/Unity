from flask_restful import Resource
from api.constants import APIConstants, AppIntents, ValidatedDict
from api.precheck import RequestPreCheck
from api.data.endpoints.session import UserSession
from api.data.endpoints.team import TeamData
from api.data.endpoints.team_member import TeamMemberData
from api.data.endpoints.application import ApplicationData

class OAuthApplication(Resource):
    def get(self):
        session_state, session = RequestPreCheck.get_session()
        if not session_state:
            return session
        
        args_state, args = RequestPreCheck.check_args({'oauthId': str})
        if not args_state:
            return args
                
        oauth_id = args.get_str('oauthId')

        app = ApplicationData.get_app_from_oauth(oauth_id)
        if not app:
            return APIConstants.badEnd('failed to find application')
        
        team = TeamData.get_team(app.get_int('teamId'))
        app['team'] = team
        app['internal'] = False
        if team.get_int('owner') == 0:
            app['internal'] = True
        
        app_data = app.get_dict('data')
        intents = app.get_int('intents', None)
        if intents:
            app_data['intents'] = AppIntents.reverse_intents_bitmask(intents)
        app.replace_dict('data', app_data)
        
        return APIConstants.goodEnd(app)
    
class OAuthCheck(Resource):
    def post(self, oauth_id: str):
        session_state, session = RequestPreCheck.get_session()
        if not session_state:
            return session
        
        data_state, data = RequestPreCheck.check_data({'apiKey': str})
        if not data_state:
            return data
        
        encrypted_key = data.get_str('apiKey')
        client_secret = UserSession.AES.decrypt(encrypted_key)

        app_state = ApplicationData.verify_app_from_oauth(oauth_id, client_secret)
        if not app_state:
            return APIConstants.badEnd('failed to verify application')
        
        app = ApplicationData.get_app_from_oauth(oauth_id)
        if not app:
            return APIConstants.badEnd('failed to find application')
        
        return APIConstants.goodEnd({'intents': app.get_int('intents')})