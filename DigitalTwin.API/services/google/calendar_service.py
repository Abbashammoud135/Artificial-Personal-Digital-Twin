import requests
from typing import List, Dict, Any
from datetime import datetime

def safe_iso(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str).isoformat() + "Z"
    except:
        return None
class GoogleCalendarService:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

    def safe_iso(self,dt_str):
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str).isoformat() + "Z"
        except:
            return None
        
    async def list_events(self, access_token: str, startTime: str, endTime: str) -> List[Dict[str, Any]]:
        """
        List upcoming events from the user's primary calendar.
        If using a mock token, returns mock events.
        """
        if access_token.startswith("mock_access_token"):
            return self._get_mock_events()
        

        headers = {"Authorization": f"Bearer {access_token}"}
        # Get next 20 events
        params = {"maxResults": 20, "singleEvents": True, "orderBy": "startTime"}
        if startTime:
            startTime = safe_iso(startTime)
            if startTime:
                params["timeMin"] = startTime

        if endTime:
            endTime = safe_iso(endTime)
            if endTime:
                params["timeMax"] = endTime
        print(f"start time {startTime} end time {endTime}")
        response = requests.get(self.base_url, headers=headers, params=params)
        print(f"Google Calendar API response status: {response.status_code}")
        if response.status_code != 200:
            return self._get_mock_events()
            
        items = response.json().get("items", [])
        events = []
        for item in items:
            events.append({
                "id": item.get("id"),
                "title": item.get("summary", "No Title"),
                "start": item.get("start", {}).get("dateTime") or item.get("start", {}).get("date"),
                "end": item.get("end", {}).get("dateTime") or item.get("end", {}).get("date"),
                "description": item.get("description", "")
            })
        print(f"Fetched {len(events)} events from Google Calendar")
        return events

    async def create_event(self, access_token: str, title: str, start: str, end: str, description: str = None) -> dict:
        """
        Create a new calendar event.
        """
        if access_token.startswith("mock_access_token"):
            return {
                "id": "mock_event_created",
                "title": title,
                "start": start,
                "end": end,
                "description": description
            }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
        "summary": title,
        "description": description or "",
        "start": {
            "dateTime": start,
            "timeZone": "Asia/Beirut"
        },
        "end": {
            "dateTime": end,
            "timeZone": "Asia/Beirut"
          }
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise ValueError(f"Failed to create Google Calendar event: {response.text}")
            
        item = response.json()
        return {
            "id": item.get("id"),
            "title": item.get("summary"),
            "start": item.get("start", {}).get("dateTime"),
            "end": item.get("end", {}).get("dateTime"),
            "description": item.get("description")
        }

    async def update_event(self, access_token: str, event_id: str, updates: dict) -> dict:
        """
        Update / Reschedule a calendar event.
        """
        if access_token.startswith("mock_access_token") or event_id.startswith("mock"):
            return {
                "id": event_id,
                "title": updates.get("title", "Updated Event"),
                "start": updates.get("start"),
                "end": updates.get("end"),
                "description": updates.get("description")
            }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # 1. Fetch current event first to patch it
        event_url = f"{self.base_url}/{event_id}"
        get_res = requests.get(event_url, headers=headers)
        if get_res.status_code != 200:
            raise ValueError("Event not found on Google Calendar")
            
        event_payload = get_res.json()
        
        # 2. Patch updates
        if "title" in updates:
            event_payload["summary"] = updates["title"]
        if "description" in updates:
            event_payload["description"] = updates["description"]
        if "start" in updates:
            event_payload["start"] = {"dateTime": updates["start"], "timeZone": "Asia/Beirut"}
        if "end" in updates:
            event_payload["end"] = {"dateTime": updates["end"], "timeZone": "Asia/Beirut"}
            
        put_res = requests.put(event_url, headers=headers, json=event_payload)
        if put_res.status_code != 200:
            raise ValueError(f"Failed to update Google Calendar event: {put_res.text}")
            
        item = put_res.json()
        return {
            "id": item.get("id"),
            "title": item.get("summary"),
            "start": item.get("start", {}).get("dateTime"),
            "end": item.get("end", {}).get("dateTime"),
            "description": item.get("description")
        }

    async def delete_event(self, access_token: str, event_id: str) -> bool:
        """
        Delete a calendar event.
        """
        if access_token.startswith("mock_access_token") or event_id.startswith("mock"):
            return True

        headers = {"Authorization": f"Bearer {access_token}"}
        event_url = f"{self.base_url}/{event_id}"
        
        response = requests.delete(event_url, headers=headers)
        return response.status_code in [200, 204]

    def _get_mock_events(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "mock_event_1",
                "title": "Daily Health Check & Yoga",
                "start": "2026-06-08T09:00:00Z",
                "end": "2026-06-08T09:30:00Z",
                "description": "Block scheduled by Digital Twin"
            },
            {
                "id": "mock_event_2",
                "title": "Cardiology Appointment",
                "start": "2026-06-10T11:00:00Z",
                "end": "2026-06-10T12:00:00Z",
                "description": "Check-up with Dr. Smith regarding blood pressure trends"
            }
        ]
