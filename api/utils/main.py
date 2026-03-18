from flask import Flask
from flask_restful import Api
import argparse

app = Flask(__name__)
api = Api(app)

uriPrefix = '/api/v1'

@app.route('/')
def root():
    return "Unity is running!"

# api.add_resource(someApiFunction, f'{uriPrefix}/')

def main() -> None:
    parser = argparse.ArgumentParser(epilog="Unity, the PhaseII developer network.\nThis server handles all developer integrations and serves WebHooks.", description="Starts the Unity API")
    parser.add_argument("-p", "--port", help="Port to listen on. Defaults to 2581", type=int, default=2581)
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == '__main__':
    main()