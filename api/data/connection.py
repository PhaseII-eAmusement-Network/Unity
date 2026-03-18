from typing import Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class SQLConnection:
    engine: Engine = None
    SessionLocal = None

    @staticmethod
    def update_config(db_config: Dict[str, Any]) -> None:
        user = db_config.get('user', '')
        password = db_config.get('pass', '')
        host = db_config.get('host', 'localhost')
        database = db_config.get('db', '')

        connection_string = f'postgresql+psycopg2://{user}:{password}@{host}/{database}'

        try:
            engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=1800,
                pool_size=10,
                max_overflow=20
            )

            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            SQLConnection.engine = engine
            SQLConnection.SessionLocal = sessionmaker(bind=engine)

            Base.metadata.create_all(engine)
            print("Unity: Database connection successful")

        except SQLAlchemyError as e:
            print(f"Database connection failed: {e}")
            SQLConnection.engine = None
            SQLConnection.SessionLocal = None
            raise

if SQLConnection.engine:
    Base.metadata.create_all(SQLConnection.engine)
