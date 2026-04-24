from datetime import datetime
from models.health_profile import HealthProfile


class HealthProfileService:

    def __init__(self, repo):
        self.repo = repo

    def get_profile(self, user_id):
        return self.repo.get_by_user(user_id)

    def create_profile(self, user_id, data):

        profile = HealthProfile(
            user_id=user_id,
            **data.dict(),
            last_updated=datetime.utcnow()
        )

        return self.repo.create(profile)

    def update_profile(self, user_id, data):

        profile = self.repo.get_by_user(user_id)

        if not profile:
            return None

        updates = data.dict(exclude_unset=True)
        updates["last_updated"] = datetime.utcnow()

        return self.repo.update(profile, updates)