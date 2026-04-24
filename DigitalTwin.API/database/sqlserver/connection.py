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

    def connect(self):
        host = os.getenv("DB_HOST")
        db_name = os.getenv("DB_NAME")

        # Windows Authentication connection string
        connection_string = (
            f"mssql+pyodbc://@{host}/{db_name}"
            "?driver=ODBC+Driver+17+for+SQL+Server"
            "&trusted_connection=yes"
            "&TrustServerCertificate=yes"
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