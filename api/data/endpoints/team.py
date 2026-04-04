from typing import List
from api.data.connection import SQLConnection
from database.models.types import Team

class TeamData:
    def get_all_teams(owner_id: int = None) -> List[Team]:
        with SQLConnection.SessionLocal() as session:
            query = session.query(Team)
            if owner_id != None:
                query = query.filter(Team.owner == owner_id)

            data = query.all()
            teams = []
            for team in data:
                teams.append({
                    'id': team.id,
                    'name': team.name,
                    'owner': team.owner,
                    'data': team.data
                })
            return teams
        
    def get_team(team_id: int) -> dict:
        with SQLConnection.SessionLocal() as session:
            query = session.query(Team).filter(Team.id == team_id)

            data = query.first()
            team = None
            if data:
                team = {
                    'id': data.id,
                    'name': data.name,
                    'owner': data.owner,
                    'data': data.data
                }
            return team
        
    def new_team(name: str, owner: int, data: dict) -> int:
        with SQLConnection.SessionLocal() as session:
            try:
                team = Team()
                team.name = name
                team.owner = owner
                team.data = data

                session.add(team)
                session.commit()
                return team.id

            except Exception as e:
                session.rollback()
                return None
            
    def update_team(team_id: int, name: str, team_data: dict) -> bool:
        with SQLConnection.SessionLocal() as session:
            query = session.query(Team).filter(Team.id == team_id)
            data = query.first()
            if not data:
                return False
            
            try:
                data.name = name
                data.data = team_data
                session.commit()
                return True
            except:
                session.rollback()
                return False