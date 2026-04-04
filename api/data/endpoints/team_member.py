from api.data.connection import SQLConnection
from database.models.types import TeamMember

class TeamMemberData:      
    def get_member_state(team_id: int, user_id: int) -> bool:
        with SQLConnection.SessionLocal() as session:
            query = session.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
            data = query.first()
            if data:
                return True
            else:
                return False
            
    def get_member_teams(user_id: int) -> list[int]:
         with SQLConnection.SessionLocal() as session:
            query = session.query(TeamMember).filter(TeamMember.user_id == user_id)
            data = query.all()
            team_list = []
            for team in data:
                team_list.append(team.team_id)
            return team_list
         
    def get_team_members(team_id: int) -> list[int]:
         with SQLConnection.SessionLocal() as session:
            query = session.query(TeamMember).filter(TeamMember.team_id == team_id)
            data = query.all()
            team_list = []
            for team in data:
                team_list.append(team.user_id)
            return team_list
        
    def put_member(team_id: int, user_id: int) -> bool:
        with SQLConnection.SessionLocal() as session:
            try:
                member = TeamMember()
                member.team_id = team_id
                member.user_id = user_id

                session.add(member)
                session.commit()
                return True

            except Exception as e:
                session.rollback()
                print(e)
                return False
            
    def remove_member(team_id: int, user_id: int) -> bool:
        with SQLConnection.SessionLocal() as session:
            query = session.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
            data = query.first()
            if data is None:
                return False

            session.delete(data)
            session.commit()
            return True