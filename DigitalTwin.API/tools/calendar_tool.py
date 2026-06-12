from database.mongo.repositories.action_repo import ActionRepository
from services.google.oauth_service import GoogleOAuthService
from services.google.calendar_service import GoogleCalendarService

class CalendarTool:
    def __init__(self, action_repo: ActionRepository = None):
        self.repo = action_repo or ActionRepository()
        self.oauth_service = GoogleOAuthService()
        self.google_calendar_service = GoogleCalendarService()

    async def create_event(self, user_id: str, title: str, start: str, end: str, description: str = None) -> dict:
        creds = await self.oauth_service.get_valid_credentials(user_id)
        if creds:
            # Route to real Google Calendar
            res = await self.google_calendar_service.create_event(
                access_token=creds["access_token"],
                title=title,
                start=start,
                end=end,
                description=description
            )
            return {
                "status": "success",
                "source": "google_calendar",
                "event": res
            }

        # Local storage / mock fallback
        event = {
            "title": title,
            "start": start,
            "end": end,
            "description": description
        }
        res = await self.repo.save_calendar_event(user_id, event)
        print("Saved calendar event to local database:", res)
        return {
            "status": "success",
            "source": "local_database",
            "event": res
        }

    async def list_events(self, user_id: str, startTime: str, endTime: str) -> list:
        creds = await self.oauth_service.get_valid_credentials(user_id)
        # print("I am inside list_events of CalendarTool")
        if creds:
            print("I am inside list_events of CalendarTool to get real google calendar events")
            # Route to real Google Calendar
            return await self.google_calendar_service.list_events(creds["access_token"], startTime, endTime)

        # Local storage / mock fallback
        return await self.repo.list_calendar_events(user_id)

    async def reschedule_event(self, user_id: str, event_id: str, new_start: str, new_end: str) -> dict:
        creds = await self.oauth_service.get_valid_credentials(user_id)
        if creds:
            # Route to real Google Calendar
            updates = {"start": new_start, "end": new_end}
            res = await self.google_calendar_service.update_event(creds["access_token"], event_id, updates)
            return {"status": "updated", "source": "google_calendar", "event": res}

        # Local storage / mock fallback
        updates = {
            "start": new_start,
            "end": new_end
        }
        res = await self.repo.update_calendar_event(user_id, event_id, updates)
        if res:
            return {"status": "updated", "source": "local_database", "event": res}
        return {"status": "not_found"}

    async def update_event(self, user_id: str, event_id: str, updates: dict) -> dict:
        creds = await self.oauth_service.get_valid_credentials(user_id)
        if creds:
            # Route to real Google Calendar
            res = await self.google_calendar_service.update_event(creds["access_token"], event_id, updates)
            return {"status": "updated", "source": "google_calendar", "event": res}

        # Local storage / mock fallback
        res = await self.repo.update_calendar_event(user_id, event_id, updates)
        if res:
            return {"status": "updated", "source": "local_database", "event": res}
        return {"status": "not_found"}

    async def delete_event(self, user_id: str, event_id: str) -> dict:
        creds = await self.oauth_service.get_valid_credentials(user_id)
        if creds:
            # Route to real Google Calendar
            success = await self.google_calendar_service.delete_event(creds["access_token"], event_id)
            if success:
                return {"status": "deleted", "source": "google_calendar", "message": "Event deleted successfully"}
            return {"status": "not_found"}

        # Local storage / mock fallback
        success = await self.repo.delete_calendar_event(user_id, event_id)
        if success:
            return {"status": "deleted", "source": "local_database", "message": "Event deleted successfully"}
        return {"status": "not_found"}