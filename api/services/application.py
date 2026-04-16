from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename
from api.constants import APIConstants, AppIntents, ValidatedDict
from api.precheck import RequestPreCheck
from api.data.data import BaseData
from api.data.upload import UploadData
from api.data.endpoints.session import UserSession
from api.data.endpoints.team import TeamData
from api.data.endpoints.team_member import TeamMemberData
from api.data.endpoints.application import ApplicationData
from external.backblaze import BackBlazeCDN

class Application(Resource):
    def get(self, team_id, app_id):
        session_state, session = RequestPreCheck.get_session()
        if not session_state:
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
                
        app = ApplicationData.get_app(team_id, app_id)
        if not app:
            return APIConstants.badEnd('failed to find application')
        
        app_data = app.get_dict('data')
        intents = app.get_int('intents', None)
        if intents:
            app_data['intents'] = AppIntents.reverse_intents_bitmask(intents)
        app.replace_dict('data', app_data)
        
        return APIConstants.goodEnd(app)
    
    def post(self, team_id, app_id):
        session_state, session = RequestPreCheck.get_session()
        if not session_state:
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
                
        app = ApplicationData.get_app(team_id, app_id)
        if not app:
            return APIConstants.badEnd('failed to find application')
        
        data_state, data = RequestPreCheck.check_data({'name': str, 'about':  str, 'oauthEnable': bool})
        if not data_state:
            return APIConstants.badEnd('data not provided')

        new_name = data.get_str('name')
        if not len(new_name):
            return APIConstants.badEnd('no name provided')
        
        new_about = data.get_str('about')
        if not len(new_about):
            return APIConstants.badEnd('no about provided')

        req_app_data = data.get_dict('data', None)
        if not req_app_data:
            return APIConstants.badEnd('no data provided')

        oauth_enable = data.get_bool('oauthEnable')
        app_data = app.get_dict('data')
        new_data = {}
        if oauth_enable:
            callback_uri = req_app_data.get_str('callbackUri')
            if not len(callback_uri):
                return APIConstants.badEnd('no callbackUri provided')
            
            if not RequestPreCheck.is_valid_url(callback_uri):
                return APIConstants.badEnd('callbackUri provided isn\'t valid' )
            new_data['callbackUri'] = callback_uri

            req_intents = req_app_data.get('intents', None)
            if req_intents:
                valid, error = RequestPreCheck.validate_intents(req_intents)
                if not valid:
                    return APIConstants.badEnd(error)
                
                intent_bits = AppIntents.build_intents_bitmask(req_intents)
                app['intents'] = intent_bits

        error_code = BaseData.update_data(app_data, new_data)
        if error_code:
            return error_code
            
        result = ApplicationData.update_app(
            team_id,
            app_id,
            new_name,
            new_about,
            oauth_enable,
            app['intents'],
            app_data
        )

        client_secret = None
        try:
            result, client_secret = result
            client_secret = UserSession.AES.encrypt(client_secret)
        except:
            pass

        if result:
            return APIConstants.goodEnd({'clientSecret': client_secret})
        else:
            return APIConstants.badEnd('Failed to update app!')

class NewApplication(Resource):
    def put(self, team_id):
        session_state, session = RequestPreCheck.get_session()
        if not session_state:
            return session
        
        data_state, data = RequestPreCheck.check_data({'name': str, 'about':  str, 'useOAuth': bool, 'useWebhooks': bool})
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
            member = TeamMemberData.get_member_state(team_id, user_id)
            if not member:
                admin_state, error = RequestPreCheck.check_admin(session)
                if not admin_state:
                    return APIConstants.badEnd(error)

        app_data = ValidatedDict({})
        oauth_enable = data.get_bool('useOAuth')
        intent_bits = None
        if oauth_enable:
            callback_uri = data.get_str('callbackUri')
            if not len(callback_uri):
                return APIConstants.badEnd('no callbackUri provided')
            
            if not RequestPreCheck.is_valid_url(callback_uri):
                return APIConstants.badEnd('callbackUri provided isn\'t valid' )
            app_data.replace_str('callbackUri', callback_uri)

            req_intents = data.get('intents', None)
            if req_intents:
                valid, error = RequestPreCheck.validate_intents(req_intents)
                if not valid:
                    return APIConstants.badEnd(error)
                intent_bits = AppIntents.build_intents_bitmask(req_intents)

        result = ApplicationData.new_app(
            team_id,
            data.get_str('name'),
            data.get_str('about'),
            oauth_enable,
            intent_bits,
            app_data,
        )
        if not result:
            return APIConstants.badEnd('Failed to save app!')

        client_secret = None
        app_id = result
        try:
            app_id, client_secret = result
            client_secret = UserSession.AES.encrypt(client_secret)
        except:
            pass

        return APIConstants.goodEnd({
            'appId': app_id,
            'clientSecret': client_secret,
        })
    
class ApplicationImage(Resource):
    def post(self, team_id, app_id):
        session_state, session = RequestPreCheck.get_session()
        if not session_state:
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
                
        app = ApplicationData.get_app(team_id, app_id)
        if not app:
            return APIConstants.badEnd('failed to find application')
        app_data = app.get_dict('data')
                
        if 'file' not in request.files:
            return APIConstants.badEnd('failed to find image')
        
        file = request.files['file']
        if file.filename == '':
            return APIConstants.badEnd('failed to read image name')
        
        if file and UploadData.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_bytes = file.read()

            b2_path = f"app-image-upload/{team_id}_{app_id}_{filename}"
            upload_status = BackBlazeCDN().upload(file_bytes, b2_path)
            if not upload_status:
                return APIConstants.badEnd('Failed to upload')
            
            app_data.replace_str('img', b2_path)
            ApplicationData.update_app(team_id, app_id, app_data=app_data)
            return APIConstants.goodEnd({'path': b2_path})

        return APIConstants.badEnd("Failed to upload the file!")