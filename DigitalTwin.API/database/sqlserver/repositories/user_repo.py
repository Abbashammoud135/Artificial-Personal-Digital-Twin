from sqlalchemy.orm import Session
from sqlalchemy import func
from models.user import User


class UserRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str):
        """Get user by email"""
        return self.session.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int):
        """Get user by ID"""
        return self.session.query(User).filter(User.user_id == user_id).first()

    def create_user(self, user_data: dict):
        """Create a new user"""
        user = User(
            full_name=user_data["full_name"],
            email=user_data["email"],
            hashed_password=user_data["hashed_password"],
            role_id=user_data.get("role_id", 1),
            is_active=user_data.get("is_active", True),
            is_verified=user_data.get("is_verified", False)
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_last_login(self, email: str):
        """Update last login timestamp"""
        user = self.session.query(User).filter(User.email == email).first()
        if user:
            user.last_login = func.getdate()
            self.session.commit()
            self.session.refresh(user)
        return user

    def update_user(self, user_id: int, **kwargs):
        """Update user fields"""
        user = self.session.query(User).filter(User.user_id == user_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.session.commit()
            self.session.refresh(user)
        return user