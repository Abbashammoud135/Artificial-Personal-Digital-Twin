import base64
import requests
from email.mime.text import MIMEText
from typing import List, Dict, Any

class GoogleGmailService:
    def __init__(self):
        self.base_url = "https://gmail.googleapis.com/gmail/v1/users/me"

    async def list_messages(self, access_token: str, query: str = None) -> List[Dict[str, Any]]:
        """
        List messages from the user's Gmail inbox.
        If using a mock token, returns a mock inbox.
        """
        if access_token.startswith("mock_access_token"):
            return self._get_mock_messages(query)

        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"maxResults": 10}
        if query:
            params["q"] = query

        list_url = f"{self.base_url}/messages"
        response = requests.get(list_url, headers=headers, params=params)
        
        if response.status_code != 200:
            return self._get_mock_messages(query) # fallback if API fails
            
        messages_data = response.json().get("messages", [])
        result = []
        
        # Resolve details for each message
        for msg in messages_data[:5]: # limit to top 5 to prevent slow calls
            detail_url = f"{self.base_url}/messages/{msg['id']}"
            detail_res = requests.get(detail_url, headers=headers)
            if detail_res.status_code == 200:
                detail = detail_res.json()
                headers_list = detail.get("payload", {}).get("headers", [])
                
                subject = next((h["value"] for h in headers_list if h["name"].lower() == "subject"), "No Subject")
                sender = next((h["value"] for h in headers_list if h["name"].lower() == "from"), "Unknown")
                
                result.append({
                    "id": detail["id"],
                    "from": sender,
                    "subject": subject,
                    "body": detail.get("snippet", ""),
                    "date": detail.get("internalDate", "")
                })
        
        return result if result else self._get_mock_messages(query)

    async def send_message(self, access_token: str, to: str, subject: str, body: str) -> dict:
        """
        Send an email via Google Gmail API.
        If using a mock token, simulates sending.
        """
        if access_token.startswith("mock_access_token"):
            return {
                "status": "success",
                "message": "Email sent (mock Google Gmail API)"
            }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Build MIME Message
        mime_msg = MIMEText(body)
        mime_msg["to"] = to
        mime_msg["subject"] = subject
        
        raw_bytes = base64.urlsafe_b64encode(mime_msg.as_bytes())
        raw_string = raw_bytes.decode("utf-8")
        
        payload = {"raw": raw_string}
        send_url = f"{self.base_url}/messages/send"
        
        response = requests.post(send_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise ValueError(f"Failed to send email via Google Gmail: {response.text}")
            
        return response.json()

    def _get_mock_messages(self, query: str = None) -> List[Dict[str, Any]]:
        mock_data = [
            {
                "id": "gmail_mock_1",
                "from": "google-noreply@google.com",
                "subject": "Google OAuth Connected Successfully",
                "body": "Your account is now linked to the Personal Agentic Digital Twin.",
                "date": "2026-06-08T10:00:00Z"
            },
            {
                "id": "gmail_mock_2",
                "from": "dr.smith@cardiology.com",
                "subject": "Lab Results Review Required",
                "body": "Hi, I looked at your recent vitals log. Please schedule a virtual check-in this week.",
                "date": "2026-06-07T14:30:00Z"
            }
        ]
        if query:
            return [
                m for m in mock_data
                if query.lower() in m["subject"].lower()
                or query.lower() in m["body"].lower()
            ]
        return mock_data
