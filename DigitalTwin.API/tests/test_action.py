import pytest
import asyncio
from database.mongo.connection import mongo
from database.mongo.collections import Collections
from database.mongo.repositories.action_repo import ActionRepository
from tools.email_tool import EmailTool
from tools.calendar_tool import CalendarTool
from tools.notification_tool import NotificationTool
from agents.action.agent import ActionAgent
from agents.action.schema import ActionIntent
from services.google.oauth_service import GoogleOAuthService
from dotenv import load_dotenv

# Load env variables (required for MongoDB and LLM API keys)
load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Ensure MongoDB client is connected for the async tests."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(mongo.connect())
    yield
    mongo.close()


def test_action_repo_crud():
    """Test CRUD operations on ActionRepository."""
    async def run_test():
        repo = ActionRepository()
        user_id = "test_user_123"

        # 1. Test Style Profile
        style = {
            "tone": "enthusiastic",
            "signature": "\nCheers,\nTester",
            "formatting": "bullet points",
            "recurring_phrases": ["Let's do this!", "Awesome work"]
        }
        saved_profile = await repo.save_style_profile(user_id, style)
        assert saved_profile["tone"] == "enthusiastic"
        assert saved_profile["signature"] == "\nCheers,\nTester"

        loaded_profile = await repo.get_style_profile(user_id)
        assert loaded_profile["tone"] == "enthusiastic"

        # 2. Test Calendar Events
        event = {
            "title": "Unit Test Event",
            "start": "2026-06-08T10:00:00",
            "end": "2026-06-08T11:00:00",
            "description": "Created during pytest execution"
        }
        saved_event = await repo.save_calendar_event(user_id, event)
        assert saved_event["_id"] is not None
        assert saved_event["title"] == "Unit Test Event"
        event_id = saved_event["_id"]

        events = await repo.list_calendar_events(user_id)
        assert len(events) >= 1
        assert any(e["_id"] == event_id for e in events)

        # Update Event
        updates = {"title": "Updated Test Event"}
        updated_event = await repo.update_calendar_event(user_id, event_id, updates)
        assert updated_event["title"] == "Updated Test Event"

        # Delete Event
        deleted = await repo.delete_calendar_event(user_id, event_id)
        assert deleted is True

        # 3. Test Email Drafts
        draft = {
            "to": "test@example.com",
            "subject": "Test Draft",
            "body": "Hello world",
            "context": {"topic": "tests"}
        }
        saved_draft = await repo.save_email_draft(user_id, draft)
        assert saved_draft["_id"] is not None
        draft_id = saved_draft["_id"]

        drafts = await repo.list_email_drafts(user_id)
        assert len(drafts) >= 1

        loaded_draft = await repo.get_email_draft(user_id, draft_id)
        assert loaded_draft["subject"] == "Test Draft"

        # Delete Draft
        deleted_draft = await repo.delete_email_draft(user_id, draft_id)
        assert deleted_draft is True

        # 4. Test Notifications
        notif = {"message": "Low battery reminder", "level": "warning"}
        saved_notif = await repo.save_notification(user_id, notif)
        assert saved_notif["_id"] is not None
        assert saved_notif["level"] == "warning"

        notifications = await repo.list_notifications(user_id)
        assert len(notifications) >= 1

    asyncio.run(run_test())


def test_email_tool_drafting():
    """Test EmailTool drafting using LLM and style profiles."""
    async def run_test():
        user_id = "test_user_123"
        repo = ActionRepository()
        
        # Save a custom style profile
        style = {
            "tone": "casual and friendly",
            "signature": "\nCatch you later,\nBob",
            "formatting": "paragraphs",
            "recurring_phrases": ["no worries", "totally cool"]
        }
        await repo.save_style_profile(user_id, style)

        email_tool = EmailTool(repo)
        draft = await email_tool.draft_email(
            user_id=user_id,
            to="friend@example.com",
            topic="catching up",
            message_details="ask if they want to play tennis this Saturday morning"
        )

        assert draft["_id"] is not None
        assert draft["to"] == "friend@example.com"
        assert draft["subject"] is not None
        assert "Bob" in draft["body"]
        
        # Cleanup draft
        await repo.delete_email_draft(user_id, draft["_id"])

    asyncio.run(run_test())


def test_action_agent_nlp_parsing():
    """Test ActionAgent parsing natural language to ActionIntents and executing."""
    async def run_test():
        user_id = "test_user_123"
        agent = ActionAgent()

        # Parse and execute email query
        res = await agent.parse_and_run(user_id, "Draft email to dentist asking for an appointment tomorrow morning")
        assert "intent" in res
        assert "result" in res
        assert res["intent"]["type"] == "draft_email"
        assert res["result"]["_id"] is not None
        
        # Cleanup
        await agent.impl.action_repo.delete_email_draft(user_id, res["result"]["_id"])

        # Parse and execute calendar query
        res_cal = await agent.parse_and_run(user_id, "Schedule gym workout tomorrow at 6 PM to 7 PM")
        assert "intent" in res_cal
        assert "result" in res_cal
        assert res_cal["intent"]["type"] == "create_event"
        assert res_cal["result"]["status"] == "success"
        assert res_cal["result"]["event"]["_id"] is not None

        # Cleanup
        await agent.impl.action_repo.delete_calendar_event(user_id, res_cal["result"]["event"]["_id"])

        # Parse and execute email sending (default: send_email with LLM enhancement)
        res_send = await agent.parse_and_run(user_id, "Send email to test@friend.com saying I will be there at 5pm, correct any grammar")
        assert "intent" in res_send
        assert "result" in res_send
        assert res_send["intent"]["type"] == "send_email"
        assert res_send["result"]["status"] == "success"

        # Parse and execute email sending direct (don't change the message)
        res_direct = await agent.parse_and_run(user_id, "Send email directly to test@friend.com: subject: Meeting, body: Please don't change this message")
        assert "intent" in res_direct
        assert "result" in res_direct
        assert res_direct["intent"]["type"] == "send_email_direct"
        assert res_direct["result"]["status"] == "success"

        # Cleanup sent emails
        db = mongo.get_db()
        await db[Collections.ACTION_SENT_EMAILS].delete_many({"user_id": user_id})

    asyncio.run(run_test())


def test_proactive_recommendations():
    """Test generating proactive recommendations."""
    async def run_test():
        user_id = "test_user_123"
        agent = ActionAgent()

        # Insert a mock health alert into MongoDB
        db = mongo.get_db()
        await db[Collections.HEALTH_ALERTS].insert_one({
            "user_id": user_id,
            "message": "Consistent high systolic blood pressure over 140 mmHg detected",
            "severity": "warning",
            "timestamp": "2026-06-08T08:00:00"
        })

        res = await agent.impl.handle_proactive(user_id)
        assert "health_context_analyzed" in res
        assert res["health_context_analyzed"] is True
        assert "recommendations" in res
        assert len(res["recommendations"]) >= 1
        
        # Verify recommendation structure
        rec = res["recommendations"][0]
        assert "action_type" in rec
        assert "title" in rec
        assert "reason" in rec

        # Cleanup alert
        await db[Collections.HEALTH_ALERTS].delete_many({"user_id": user_id})

    asyncio.run(run_test())


def test_google_oauth_and_services_flow():
    """Test Google OAuth flow integration, saving credentials and tool routing."""
    async def run_test():
        user_id = "test_user_123"
        oauth_service = GoogleOAuthService()

        # 1. Generate redirect URL
        auth_url = oauth_service.get_authorization_url(user_id, "http://localhost:8000/callback")
        assert auth_url is not None
        assert "test_user_123" in auth_url

        # 2. Exchange code (mock code)
        creds = await oauth_service.exchange_code_for_tokens(
            user_id=user_id,
            code="mock_code_for_test",
            redirect_uri="http://localhost:8000/callback"
        )
        assert creds["user_id"] == user_id
        assert creds["is_mock"] is True
        assert creds["access_token"] == f"mock_access_token_{user_id}"

        # 3. Verify tool routes through Google services when creds exist
        calendar_tool = CalendarTool()
        event_res = await calendar_tool.create_event(
            user_id=user_id,
            title="Meeting with Dr. Jones",
            start="2026-06-08T15:00:00",
            end="2026-06-08T15:30:00"
        )
        # Should be handled by Google mock Calendar since oauth creds exist
        assert event_res["source"] == "google_calendar"
        assert event_res["event"]["id"] == "mock_event_created"

        email_tool = EmailTool()
        email_res = await email_tool.send_email(
            user_id=user_id,
            to="doctor@gmail.com",
            subject="Status update",
            body="I am feeling better."
        )
        # Should be handled by Google mock Gmail since oauth creds exist
        assert email_res["source"] == "google_gmail"

        # 4. Clean up credentials
        success = await oauth_service.disconnect(user_id)
        assert success is True

        # 5. Verify tool falls back to local database when disconnected
        event_local = await calendar_tool.create_event(
            user_id=user_id,
            title="Local Meeting",
            start="2026-06-08T15:00:00",
            end="2026-06-08T15:30:00"
        )
        assert event_local["source"] == "local_database"
        
        # Clean up local event
        await calendar_tool.delete_event(user_id, event_local["event"]["_id"])

    asyncio.run(run_test())
