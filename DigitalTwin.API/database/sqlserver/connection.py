import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.user import Base

load_dotenv()

class SQLDatabase:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def is_docker(self):
        return os.path.exists("/.dockerenv")
    def connect(self):
        host = os.getenv("DB_HOST")
        db_name = os.getenv("DB_NAME")
        db_auth = os.getenv("DB_AUTH", "windows")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        
        if self.is_docker():
            host = "sqlserver"
            # db_password="StrongPass123!"

        if db_auth.lower() == "sql" or (db_user and db_password):
            connection_string = (
                f"mssql+pymssql://{db_user}:{db_password}@{host}/{db_name}"
            )
        else:
            # Windows Authentication connection string
            connection_string = (
                f"mssql+pymssql://{db_user}:{db_password}@{host}/{db_name}"
            )

        self.engine = create_engine(connection_string, pool_pre_ping=True)

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

        print(f"✅ SQL Server connected to {db_name}")

    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()

    def get_db(self):
        """Dependency injection for FastAPI endpoints"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
            
sql_db = SQLDatabase()