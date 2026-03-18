from flask import Flask
from flask_restful import Api
from flask_cors import CORS # type: ignore
from typing import Any, Dict
import argparse
import yaml

from api.data.connection import SQLConnection

from api.services.test import TestEndpoint

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.update(
    SESSION_COOKIE_HTTPONLY = True,
    SESSION_COOKIE_SAMESITE = 'None',
)

api = Api(app)
config: Dict[str, Any] = {}

uri_prefix = '/api/v1'

@app.route('/')
def root():
    return "Unity is running!"

api.add_resource(TestEndpoint, f'{uri_prefix}/test')

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
    app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == '__main__':
    main()