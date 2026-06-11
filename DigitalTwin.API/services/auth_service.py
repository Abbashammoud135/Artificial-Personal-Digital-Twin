from core.security import hash_password, verify_password, create_access_token
from datetime import datetime

class AuthService:

    def __init__(self, user_repo):
        self.user_repo = user_repo

    # 🟢 REGISTER
    def register(self, full_name, email, password):

        existing = self.user_repo.get_by_email(email)
        if existing:
            raise Exception("User already exists")

        user_data = {
            "full_name": full_name,
            "email": email,
            "hashed_password": hash_password(password),
            "role_id": 1
        }

        user = self.user_repo.create_user(user_data)

        return {"message": "User created", "user_id": user.user_id}

    # 🔵 LOGIN
    def login(self, email, password):

        user = self.user_repo.get_by_email(email)

        if not user:
            raise Exception("Invalid credentials")

        if not verify_password(password, user.hashed_password):
            raise Exception("Invalid credentials")

        token = create_access_token({
            "sub": str(user.user_id),
            "role_id": user.role_id,
            "email": user.email
        })

        self.user_repo.update_last_login(email)

        return token
    def get_user_fullname(self, user_id):
        user=self.user_repo.get_by_id(user_id)
        return user.full_name if user else "Unknown User"