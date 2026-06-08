import os
from urllib import response
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional
from database.mongo.connection import mongo
import requests  # standard request library

class GoogleOAuthService:
    def __init__(self):
        self.db = mongo.get_db()
        self.collection_name = "google_credentials"
        
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.scopes = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar"
        ]

    def is_configured(self) -> bool:
        """Returns True if real Google API credentials are set up in environment."""
        return bool(self.client_id and self.client_secret)

    def get_authorization_url(self, user_id: str, redirect_uri: str) -> str:
        """
        Generates Google OAuth Consent Page URL.
        If real keys are missing, returns a mock redirect url.
        """
        if not self.is_configured():
            # Mock authorization URL
            params = {
                "state": user_id,
                "redirect_uri": redirect_uri,
                "mock": "true"
            }
            return f"{redirect_uri}?code=mock_code_for_{user_id}&state={user_id}"

        # Real Google Auth URL
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": user_id
        }
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

    async def exchange_code_for_tokens(self, user_id: str, code: str, redirect_uri: str) -> dict:
        """
        Exchanges code for credentials and saves them to MongoDB.
        """
        if not self.is_configured() or code.startswith("mock_code"):
            # Simulate token exchange
            creds = {
                "user_id": user_id,
                "access_token": f"mock_access_token_{user_id}",
                "refresh_token": f"mock_refresh_token_{user_id}",
                "expiry": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "scopes": self.scopes,
                "is_mock": True,
                "connected_at": datetime.utcnow()
            }
            await self._save_credentials(user_id, creds)
            return creds

        # Real token exchange
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        response = requests.post(token_url, data=data)
        
        print("GOOGLE STATUS:", response.status_code)
        print("GOOGLE RESPONSE:", response.text)
        
        if response.status_code != 200:
            raise ValueError(f"Failed to exchange Google OAuth code: {response.text}")
            
        try:
            token_data = response.json()
        except Exception:
            raise ValueError(f"Invalid Google response: {response.text}")

        if "access_token" not in token_data:
            raise ValueError(f"Missing access token: {token_data}")    
        expiry = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
                
        creds = {
            "user_id": user_id,
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),  # only present on first prompt
            "expiry": expiry.isoformat(),
            "scopes": token_data.get("scope", "").split(" ") or self.scopes,
            "is_mock": False,
            "connected_at": datetime.utcnow()
        }
        
        await self._save_credentials(user_id, creds)
        return creds

    async def get_valid_credentials(self, user_id: str) -> Optional[dict]:
        """
        Retrieves user credentials from MongoDB, refreshing access token if expired.
        """
        collection = self.db[self.collection_name]
        creds = await collection.find_one({"user_id": user_id})
        if not creds:
            return None

        # Check expiry
        expiry_str = creds.get("expiry")
        if not expiry_str:
            return creds

        expiry_time = datetime.fromisoformat(expiry_str)
        if expiry_time <= datetime.utcnow():
            # Refresh token
            creds = await self.refresh_credentials(user_id, creds)

        return creds

    async def refresh_credentials(self, user_id: str, creds: dict) -> dict:
        """
        Refreshes expired credentials using the refresh token.
        """
        if creds.get("is_mock"):
            # Update expiry for mock
            creds["expiry"] = (datetime.utcnow() + timedelta(hours=1)).isoformat()
            await self._save_credentials(user_id, creds)
            return creds

        refresh_token = creds.get("refresh_token")
        if not refresh_token:
            return creds  # cannot refresh without refresh token

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            # Refresh failed, remove creds or return existing
            return creds

        token_data = response.json()
        creds["access_token"] = token_data["access_token"]
        expiry = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
        creds["expiry"] = expiry.isoformat()

        await self._save_credentials(user_id, creds)
        return creds

    async def disconnect(self, user_id: str) -> bool:
        """Removes the Google connection for the user."""
        collection = self.db[self.collection_name]
        res = await collection.delete_one({"user_id": user_id})
        return res.deleted_count > 0

    async def _save_credentials(self, user_id: str, creds: dict):
        collection = self.db[self.collection_name]
        # Clean ID
        if "_id" in creds:
            del creds["_id"]
        await collection.replace_one({"user_id": user_id}, creds, upsert=True)
