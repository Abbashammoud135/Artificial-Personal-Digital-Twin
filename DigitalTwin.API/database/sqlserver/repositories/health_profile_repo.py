from sqlalchemy.orm import Session
from models.health_profile import HealthProfile
import uuid


class HealthProfileRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_user(self, user_id: uuid.UUID):
        return self.db.query(HealthProfile).filter(
            HealthProfile.user_id == user_id
        ).first()

    def create(self, profile: HealthProfile):
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, db_profile: HealthProfile, updates: dict):
        for key, value in updates.items():
            setattr(db_profile, key, value)

        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile