from typing import Dict, Any
import random
import time

from api.constants import ValidatedDict
from api.data.aes import AESCipher
from api.data.connection import SQLConnection
from database.models.types import Session

class UserSession():
    AES = None
    SECURE_COOKIE = True

    @staticmethod
    def update_config(flaskConfig: Dict[str, Any]) -> None:
        secure_cookie = flaskConfig.get('secure_cookie', None)
        if secure_cookie == None:
            raise Exception("Failed to initialize auth config.")
        
        UserSession.SECURE_COOKIE = secure_cookie

    @staticmethod
    def update_crypto_config(cryptoConfig: Dict[str, Any]) -> None:
        key = cryptoConfig.get('cookie_key', None)
        if key == None:
            raise Exception("Failed to initialize crypto config.")
        
        UserSession.AES = AESCipher(key)

    @staticmethod
    def create_session(user_id: int, access_token: str, expiration: int=(30 * 86400)):
        session_token = ''.join(random.choice('0123456789ABCDEF') for _ in range(32))
        expiration_time = int(time.time() + expiration)

        with SQLConnection.SessionLocal() as session:
            try:
                while session.query(Session).filter(Session.session_token == session_token).first():
                    session_token = ''.join(random.choice('0123456789ABCDEF') for _ in range(32))
                
                new_session = Session(user_id=user_id, session_token=session_token, access_token=access_token, data={}, expiration=expiration_time)
                session.add(new_session)
                session.commit()
                return session_token

            except Exception as e:
                session.rollback()
                return None
            
    @staticmethod
    def check_session(token: str) -> ValidatedDict:
        token_dec: str = None
        try:
            token_dec = UserSession.AES.decrypt(token)
        except Exception as e:
            print(e)
            return ValidatedDict({
                'active': False,
                'id': None 
            })

        with SQLConnection.SessionLocal() as session:
            user_session = session.query(Session).filter(Session.session_token == token_dec).first()
            if user_session != None:
                return ValidatedDict({
                    'active': True,
                    'id': int(user_session.user_id),
                    'access_token': str(user_session.access_token)
                })
            else:
                return ValidatedDict({
                    'active': False,
                    'id': None 
                })
            
    @staticmethod
    def delete_session(token: str) -> None:
        token_dec: str = None
        try:
            token_dec = UserSession.AES.decrypt(token)
        except Exception as e:
            print(e)
            return False
        with SQLConnection.SessionLocal() as session:
            session.query(Session).filter(Session.session_token == token_dec).delete()
            session.commit()