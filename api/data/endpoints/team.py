from typing import List
from api.data.connection import SQLConnection
from database.models.types import Team

class TeamData:
    def get_all_teams() -> List[Team]:
        with SQLConnection.SessionLocal() as session:
            data = session.query(Team).all()

            teams = []
            for team in data:
                teams.append({
                    'id': team.id,
                    'name': team.name,
                    'owner': team.owner,
                    'data': team.data
                })
            return teams
        
    def new_team(name: str, owner: int, data: dict) -> bool:
        with SQLConnection.SessionLocal() as session:
            try:
                team = Team()
                team.name = name
                team.owner = owner
                team.data = data

                session.add(team)
                session.commit()
                return True

            except Exception as e:
                session.rollback()
                return False