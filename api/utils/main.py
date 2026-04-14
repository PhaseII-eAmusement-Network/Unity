from flask import Flask
from flask_restful import Api
from flask_cors import CORS # type: ignore
from typing import Any, Dict
import argparse
import yaml

from api.constants import APIConstants

from api.data.connection import SQLConnection
from api.data.upload import UploadData
from api.data.endpoints.session import UserSession

from api.services.auth import OAuthCallback, AuthSession
from api.services.user import UserAccount
from api.services.team import Team, NewTeam
from api.services.team_member import TeamMember
from api.services.application import Application, NewApplication, ApplicationImage

from external.restfulsleep import RestfulSleepAPI
from external.backblaze import BackBlazeCDN

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.update(
    SESSION_COOKIE_HTTPONLY = True,
    SESSION_COOKIE_SAMESITE = 'None',
)

api = Api(app)
config: Dict[str, Any] = {}

uri_prefix = '/v1'

@app.route('/')
def root():
    return "Unity is running!"

api.add_resource(OAuthCallback, f'{uri_prefix}/oauth/callback')
api.add_resource(AuthSession, f'{uri_prefix}/auth/session')
api.add_resource(UserAccount, f'{uri_prefix}/user')
api.add_resource(Team, f'{uri_prefix}/team/<team_id>')
api.add_resource(NewTeam, f'{uri_prefix}/team')
api.add_resource(TeamMember, f'{uri_prefix}/team/<team_id>/member')
api.add_resource(Application, f'{uri_prefix}/team/<team_id>/application/<app_id>')
api.add_resource(ApplicationImage, f'{uri_prefix}/team/<team_id>/application/<app_id>/image')
api.add_resource(NewApplication, f'{uri_prefix}/team/<team_id>/application')

def load_configs(filename: str) -> None:
    global config

    with open(filename, 'r') as file:
        config.update(yaml.safe_load(file))
    print(f"Unity: Loaded {len(config.values())} params from {filename}")

    flaskConfig = config.get('flask', {})
    secret_key = flaskConfig.get('secret_key')
    if not secret_key:
        raise ValueError("Missing 'flask.secret_key' in config file. Required for secure HTTP-only cookies.")
    app.secret_key = secret_key
    app.config.update(
        SESSION_COOKIE_SECURE = flaskConfig.get('secure_cookie', True),
    )

    config_map = {
        'database': SQLConnection.update_config,
        'restfulsleep': RestfulSleepAPI.update_config,
        'flask': UserSession.update_config,
        'crypto': UserSession.update_crypto_config,
        'unity': APIConstants.update_config,
        'backblaze': BackBlazeCDN.update_config,
        'upload': UploadData.update_config,
    }

    for key, updater in config_map.items():
        section = config.get(key, {})
        if section:
            updater(section)

def main() -> None:
    parser = argparse.ArgumentParser(epilog="Unity, the PhaseII developer network.\nThis server handles all developer integrations and serves WebHooks.", description="Starts the Unity API")
    parser.add_argument("-p", "--port", help="Port to listen on. Defaults to 2581", type=int, default=2581)
    parser.add_argument("-c", "--config", help="Path to configuration file. Defaults to 'config.yaml'", type=str, default='config.yaml')
    args = parser.parse_args()

    print("Starting Unity")
    load_configs(args.config)

    if APIConstants.BYPASS_CALLBACK_VALIDATION:
        print("\n\nUnity config warning!!!\n`bypass_callback_validation` has been enabled in your config.\nDO NOT RUN THIS IN PRODUCTION!")

    app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == '__main__':
    main()