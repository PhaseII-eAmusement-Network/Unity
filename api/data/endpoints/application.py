import random
from typing import List
from passlib.hash import pbkdf2_sha512
from api.data.connection import SQLConnection
from api.constants import ValidatedDict
from database.models.types import Application

class ApplicationData:
    def get_all_apps(team_id: int = None) -> List[Application]:
        with SQLConnection.SessionLocal() as session:
            query = session.query(Application)
            if team_id != None:
                query = query.filter(Application.team_id == team_id)

            data = query.all()
            apps = []
            for app in data:
                apps.append(ValidatedDict({
                    'id': app.id,
                    'teamId': app.team_id,
                    'name': app.name,
                    'about': app.description,
                    'oauthEnable': app.oauth_enable,
                    'intents': app.intents,
                    'data': app.data
                }))
            return apps
        
    def get_app(team_id: int, app_id: int) -> ValidatedDict:
        with SQLConnection.SessionLocal() as session:
            query = session.query(Application).filter(Application.id == app_id, Application.team_id == team_id)

            data = query.first()
            app = None
            if data:
                app = {
                    'id': data.id,
                    'teamId': data.team_id,
                    'name': data.name,
                    'about': data.description,
                    'oauthEnable': data.oauth_enable,
                    'oauthId': data.oauth_id,
                    'intents': data.intents,
                    'data': data.data
                }
            return ValidatedDict(app)
        
    def get_app_from_oauth(oauth_id: str) -> ValidatedDict:
        with SQLConnection.SessionLocal() as session:
            query = session.query(Application).filter(Application.oauth_id == oauth_id)

            data = query.first()
            if data != None:
                app = {
                    'id': data.id,
                    'teamId': data.team_id,
                    'name': data.name,
                    'about': data.description,
                    'oauthEnable': data.oauth_enable,
                    'oauthId': data.oauth_id,
                    'intents': data.intents,
                    'data': data.data
                }
                return ValidatedDict(app)
            return None
        
    def verify_app_from_oauth(oauth_id: str, client_secret: str) -> bool:
        with SQLConnection.SessionLocal() as session:
            query = session.query(Application.client_secret).filter(Application.oauth_id == oauth_id)
            data = query.first()
            if data == None:
                return False

            try:
                return pbkdf2_sha512.verify(client_secret, data[0])
            except (ValueError, TypeError):
                return False
        
    def new_app(team_id: int, name: str, about: str, oauth_enable: bool, intents: int = None, data: dict = {}) -> int | tuple[int, str]:
        with SQLConnection.SessionLocal() as session:
            try:
                app = Application()
                app.team_id = team_id
                app.name = name
                app.description = about
                app.oauth_enable = oauth_enable
                app.data = data
                if intents:
                    app.intents = intents

                if oauth_enable:
                    oauth_id = ''.join(random.choice('0123456789ABCDEFabcdef') for _ in range(16))
                    while session.query(Application).filter(Application.oauth_id == oauth_id).first():
                        oauth_id = ''.join(random.choice('0123456789ABCDEFabcdef') for _ in range(16))

                    client_secret = ''.join(random.choice('0123456789ABCDEF') for _ in range(32))
                    hashed = pbkdf2_sha512.hash(client_secret)

                    app.oauth_id = oauth_id
                    app.client_secret = hashed

                session.add(app)
                session.commit()

                if client_secret:
                    return app.id, client_secret
                
                return app.id

            except Exception as e:
                print(e)
                session.rollback()
                return None
            
    def update_app(
        team_id: int,
        app_id: int,
        name: str = None,
        about: str = None,
        oauth_enable: bool = None,
        intents: int = None,
        app_data: dict = None
    ) -> bool | tuple[bool, str]:
        with SQLConnection.SessionLocal() as session:
            query = session.query(Application).filter(
                Application.id == app_id,
                Application.team_id == team_id
            )
            data = query.first()

            if not data:
                return False

            try:
                if name is not None:
                    data.name = name

                if about is not None:
                    data.description = about

                if oauth_enable is not None:
                    data.oauth_enable = oauth_enable

                client_secret = None
                if oauth_enable == True:
                    if not data.oauth_id:
                        oauth_id = ''.join(random.choice('0123456789ABCDEFabcdef') for _ in range(16))
                        while session.query(Application).filter(Application.oauth_id == oauth_id).first():
                            oauth_id = ''.join(random.choice('0123456789ABCDEFabcdef') for _ in range(16))
                        data.oauth_id = oauth_id

                    if not data.client_secret:
                        client_secret = ''.join(random.choice('0123456789ABCDEF') for _ in range(32))
                        hashed = pbkdf2_sha512.hash(client_secret)
                        data.client_secret = hashed
                elif oauth_enable == False:
                    data.oauth_id = None
                    data.client_secret = None

                if app_data is not None:
                    data.data = app_data

                if intents is not None:
                    data.intents = intents

                session.commit()

                if client_secret:
                    return True, client_secret
                return True

            except Exception:
                session.rollback()
                return False