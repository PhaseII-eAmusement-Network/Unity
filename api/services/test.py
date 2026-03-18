from flask_restful import Resource
from api.data.endpoints.team import TeamData

class TestEndpoint(Resource):
    def get(self):
        teams = TeamData.get_all_teams()
        print(teams)
        return "Good!"
    
    def put(self):
        TeamData.new_team("test team", 6, {
            'image': 'https://image.com'
        })
        return "Good!"