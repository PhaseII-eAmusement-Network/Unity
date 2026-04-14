from typing import List
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
                    'intents': data.intents,
                    'data': data.data
                }
            return ValidatedDict(app)
        
    def new_app(team_id: int, name: str, about: str, oauthEnable: bool, intents: int = None, data: dict = {}) -> int:
        with SQLConnection.SessionLocal() as session:
            try:
                app = Application()
                app.team_id = team_id
                app.name = name
                app.description = about
                app.oauth_enable = oauthEnable
                app.data = data
                if intents:
                    app.intents = intents

                session.add(app)
                session.commit()
                return app.id

            except Exception as e:
                session.rollback()
                return None
            
    def update_app(
        team_id: int,
        app_id: int,
        name: str = None,
        about: str = None,
        oauthEnable: bool = None,
        intents: int = None,
        app_data: dict = None
    ) -> bool:
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

                if oauthEnable is not None:
                    data.oauth_enable = oauthEnable

                if app_data is not None:
                    data.data = app_data

                if intents is not None:
                    data.intents = intents

                session.commit()
                return True

            except Exception:
                session.rollback()
                return False