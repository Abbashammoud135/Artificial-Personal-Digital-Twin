from database.mongo.repositories.action_repo import ActionRepository

class NotificationTool:
    def __init__(self, action_repo: ActionRepository = None):
        self.repo = action_repo or ActionRepository()

    async def send_alert(self, user_id: str, message: str, level: str = "info") -> dict:
        """
        Create a notification alert and persist it in the database.
        """
        notification = {
            "message": message,
            "level": level
        }
        res = await self.repo.save_notification(user_id, notification)
        return {
            "status": "success",
            "notification": res
        }

    async def list_notifications(self, user_id: str) -> list:
        return await self.repo.list_notifications(user_id)
