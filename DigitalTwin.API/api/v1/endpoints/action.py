import os
import urllib.parse
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import List, Dict, Any, Optional
from core.dependencies import get_current_user
from agents.action.agent import ActionAgent
from agents.action.schema import (
    ActionIntent,
    ExecuteRequest,
    EmailDraftRequest,
    EmailSendRequest,
    EmailSendEnhancedRequest,
    CalendarEventCreate,
    CalendarEventUpdate,
    StyleProfileSchema,
    NotificationCreate
)

class LazyActionAgent:
    def __init__(self):
        self._agent = None

    @property
    def agent(self):
        if self._agent is None:
            self._agent = ActionAgent()
        return self._agent

    def __getattr__(self, name):
        return getattr(self.agent, name)

router = APIRouter(prefix="/action", tags=["Action Agent"])
action_agent = LazyActionAgent()
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
print(f"Google Redirect URI: {GOOGLE_REDIRECT_URI}")
# ==========================================
# DYNAMIC EXECUTION
# ==========================================

@router.post("/execute", status_code=status.HTTP_200_OK)
async def execute_natural_language(
    payload: ExecuteRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Execute an action using natural language query.
    Calculates time context automatically and maps query to email, calendar, or notifications tools.
    Results are dispatched to the relevant tool (email, calendar, or notifications) — each tool persists data in MongoDB.
    """
    user_id = current_user["user_id"]
    try:
        return await action_agent.parse_and_run(user_id, payload.query)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution error: {str(e)}"
        )

@router.post("/execute-intent", status_code=status.HTTP_200_OK)
async def execute_structured_intent(
    intent: ActionIntent,
    current_user: dict = Depends(get_current_user)
):
    """
    Execute a fully-structured ActionIntent.
    Useful for executing tasks planned by the Planner Agent.
    Results are dispatched to the relevant tool — each tool persists data in MongoDB.
    """
    user_id = current_user["user_id"]
    try:
        res = await action_agent.run(user_id, intent.dict())
        return {"status": "success", "result": res}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution error: {str(e)}"
        )

# ==========================================
# EMAILS
# ==========================================

@router.get("/emails/inbox", status_code=status.HTTP_200_OK)
async def get_email_inbox(
    query: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Fetch the user's email inbox, optionally filtered by subject/body keywords.
    Emails are fetched from the user's real Gmail account via Google API (requires Google OAuth).
    """
    try:
        user_id = current_user["user_id"]
        emails = await action_agent.impl.email_tool.read_inbox(user_id, query)
        summary = action_agent.impl.email_tool.summarize_emails(emails)
        return {"emails": emails, "summary": summary}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/emails/draft", status_code=status.HTTP_201_CREATED)
async def create_email_draft(
    payload: EmailDraftRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a personalized email draft using the user's style profile and an LLM model.
    The draft email is saved in MongoDB (not in Google Draft) — collection: ACTION_EMAIL_DRAFTS.
    """
    user_id = current_user["user_id"]
    try:
        draft = await action_agent.impl.email_tool.draft_email(
            user_id=user_id,
            to=payload.to,
            topic=payload.topic,
            message_details=payload.message_details,
            style_profile_override=payload.style_profile_override,
            style_name=payload.style_name
        )
        return draft
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/emails/drafts", status_code=status.HTTP_200_OK)
async def list_email_drafts(
    current_user: dict = Depends(get_current_user)
):
    """
    List all saved email drafts for the authenticated user.
    Drafts are retrieved from MongoDB — collection: ACTION_EMAIL_DRAFTS.
    """
    user_id = current_user["user_id"]
    try:
        drafts = await action_agent.impl.email_tool.list_drafts(user_id)
        return {"drafts": drafts}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/emails/drafts/{draft_id}", status_code=status.HTTP_200_OK)
async def get_email_draft(
    draft_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve a specific email draft by its draft_id.
    Draft is fetched from MongoDB — collection: ACTION_EMAIL_DRAFTS.
    """
    user_id = current_user["user_id"]
    draft = await action_agent.impl.action_repo.get_email_draft(user_id, draft_id)
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    return draft

@router.put("/emails/drafts/{draft_id}", status_code=status.HTTP_200_OK)
async def update_email_draft(
    draft_id: str,
    updates: EmailSendRequest,  # Reuse model for updating to, subject, body
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing email draft (to, subject, body fields).
    Draft is updated in MongoDB — collection: ACTION_EMAIL_DRAFTS.
    """
    user_id = current_user["user_id"]
    res = await action_agent.impl.action_repo.update_email_draft(user_id, draft_id, updates.dict())
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    return res

@router.delete("/emails/drafts/{draft_id}", status_code=status.HTTP_200_OK)
async def delete_email_draft(
    draft_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an email draft permanently.
    Draft is removed from MongoDB — collection: ACTION_EMAIL_DRAFTS.
    """
    user_id = current_user["user_id"]
    success = await action_agent.impl.action_repo.delete_email_draft(user_id, draft_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    return {"status": "deleted", "message": "Draft deleted successfully"}

@router.post("/emails/send", status_code=status.HTTP_200_OK)
async def send_email(
    payload: EmailSendRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send an email via Gmail (Google API). Requires Google OAuth to be connected.
    A log of the sent email is saved in MongoDB — collection: ACTION_SENT_EMAILS.
    """
    user_id = current_user["user_id"]
    try:
        return await action_agent.impl.email_tool.send_email(
            user_id=user_id,
            to=payload.to,
            subject=payload.subject,
            body=payload.body
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/emails/send-enhanced", status_code=status.HTTP_200_OK)
async def send_email_enhanced(
    payload: EmailSendEnhancedRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send an email via Gmail (Google API) after enhancing it using an LLM.
    The LLM will correct grammar and apply the user's style profile.
    A log of the sent email is saved in MongoDB — collection: ACTION_SENT_EMAILS.
    """
    user_id = current_user["user_id"]
    try:
        return await action_agent.impl.email_tool.send_email_enhanced(
            user_id=user_id,
            to=payload.to,
            subject=payload.subject,
            body=payload.body,
            query_request=payload.query_request,
            style_name=payload.style_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/emails/sent", status_code=status.HTTP_200_OK)
async def list_sent_emails(
    current_user: dict = Depends(get_current_user)
):
    """
    List sent email logs for the authenticated user.
    Sent emails are retrieved from MongoDB — collection: ACTION_SENT_EMAILS.
    """
    user_id = current_user["user_id"]
    try:
        sent = await action_agent.impl.email_tool.list_sent(user_id)
        return {"sent_emails": sent}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# CALENDAR
# ==========================================

@router.get("/calendar/events", status_code=status.HTTP_200_OK)
async def get_calendar_events(
    current_user: dict = Depends(get_current_user),
    startTime: Optional[str] = None,
    endTime: Optional[str] = None
):
    """
    List all calendar events for the user within an optional time range.
    Events are fetched from Google Calendar via Google API (requires Google OAuth).
    """
    user_id = current_user["user_id"]
    try:
        events = await action_agent.impl.calendar_tool.list_events(user_id, startTime, endTime)
        return {"events": events}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/calendar/events", status_code=status.HTTP_201_CREATED)
async def create_calendar_event(
    payload: CalendarEventCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new event in the user's Google Calendar.
    Event is saved directly to Google Calendar via Google API (requires Google OAuth) — not stored in MongoDB.
    """
    user_id = current_user["user_id"]
    try:
        return await action_agent.impl.calendar_tool.create_event(
            user_id=user_id,
            title=payload.title,
            start=payload.start,
            end=payload.end,
            description=payload.description
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/calendar/events/{event_id}", status_code=status.HTTP_200_OK)
async def update_calendar_event(
    event_id: str,
    payload: CalendarEventUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update / Reschedule an existing calendar event by event_id.
    Changes are applied directly in Google Calendar via Google API (requires Google OAuth) — not stored in MongoDB.
    """
    user_id = current_user["user_id"]
    try:
        res = await action_agent.impl.calendar_tool.update_event(
            user_id=user_id,
            event_id=event_id,
            updates=payload.dict(exclude_none=True)
        )
        if res["status"] == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/calendar/events/{event_id}", status_code=status.HTTP_200_OK)
async def delete_calendar_event(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an event from the user's Google Calendar by event_id.
    Event is removed directly from Google Calendar via Google API (requires Google OAuth) — not stored in MongoDB.
    """
    user_id = current_user["user_id"]
    try:
        res = await action_agent.impl.calendar_tool.delete_event(user_id, event_id)
        if res["status"] == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# STYLE PROFILE
# ==========================================

@router.get("/style-profile", status_code=status.HTTP_200_OK)
async def get_user_style_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    Fetch the user's manually-defined email writing style profile (tone, signature, formatting).
    Profile is retrieved from MongoDB — collection: ACTION_STYLE_PROFILE.
    Returns a default neutral profile if none exists yet.
    """
    user_id = current_user["user_id"]
    try:
        profile = await action_agent.impl.action_repo.get_style_profile(user_id)
        if not profile:
            # Return empty/default template rather than 404 so UI can display it
            return {
                "tone": "neutral",
                "signature": "",
                "formatting": "paragraphs",
                "recurring_phrases": ["kind Regards,\n Abbas Hammoud"]
            }
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/style-profile", status_code=status.HTTP_200_OK)
async def save_user_style_profile(
    payload: StyleProfileSchema,
    current_user: dict = Depends(get_current_user)
):
    """
    Save or update the user's manually-defined email writing style profile (tone, signature, formatting preferences).
    Profile is upserted in MongoDB — collection: ACTION_STYLE_PROFILE.
    """
    user_id = current_user["user_id"]
    try:
        return await action_agent.impl.action_repo.save_style_profile(user_id, payload.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# NOTIFICATIONS
# ==========================================

@router.get("/notifications", status_code=status.HTTP_200_OK)
async def get_notifications(
    current_user: dict = Depends(get_current_user)
):
    """
    List all system notifications / reminders dispatched to the user.
    Notifications are retrieved from MongoDB — collection: ACTION_NOTIFICATIONS.
    """
    user_id = current_user["user_id"]
    try:
        notifications = await action_agent.impl.notification_tool.list_notifications(user_id)
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/notifications", status_code=status.HTTP_201_CREATED)
async def create_notification(
    payload: NotificationCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Directly dispatch a custom notification/reminder for the user.
    Notification is saved in MongoDB — collection: ACTION_NOTIFICATIONS.
    """
    user_id = current_user["user_id"]
    try:
        return await action_agent.impl.notification_tool.send_alert(
            user_id=user_id,
            message=payload.message,
            level=payload.level
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# PROACTIVE RECOMMENDATIONS
# ==========================================

@router.get("/proactive/recommendations", status_code=status.HTTP_200_OK)
async def get_proactive_recommendations(
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze user health history & alerts using an LLM to dynamically generate recommended actions.
    Reads health data from MongoDB and returns LLM-generated recommendations — no new data is persisted by this endpoint.
    """
    user_id = current_user["user_id"]
    try:
        return await action_agent.impl.handle_proactive(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ==========================================
# GOOGLE OAUTH
# ==========================================

@router.get("/google/connect", status_code=status.HTTP_200_OK)
def connect_google(
    redirect_url: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate the Google OAuth Consent Page URL for Gmail + Calendar access.
    The frontend should redirect the user to the returned URL.
    No data is saved at this step — credentials are stored after the OAuth callback completes.
    """
    user_id = current_user["user_id"]
    state = f"{user_id}:{redirect_url}" if redirect_url else user_id
    url = action_agent.impl.email_tool.oauth_service.get_authorization_url(state, GOOGLE_REDIRECT_URI)
    return {"authorization_url": url}

@router.get("/google/callback", status_code=status.HTTP_200_OK)
async def google_callback(
    code: str,
    state: str # contains the user_id and optional return path
):
    """
    Callback URL where Google redirects after OAuth consent.
    Exchanges the authorization code for access/refresh tokens and links them to the user.
    """
    try:
        parts = state.split(":", 1)
        user_id = parts[0]
        redirect_url = parts[1] if len(parts) > 1 else "http://localhost:5173/settings"

        creds = await action_agent.impl.email_tool.oauth_service.exchange_code_for_tokens(
            user_id=user_id,
            code=code,
            redirect_uri=GOOGLE_REDIRECT_URI
        )
        if not creds:
            raise HTTPException(
                status_code=500,
                detail="OAuth failed: credentials not returned"
            )
        return RedirectResponse(url=f"{redirect_url}?google_auth=success")
    except Exception as e:
        parts = state.split(":", 1)
        redirect_url = parts[1] if len(parts) > 1 else "http://localhost:5173/settings"
        return RedirectResponse(url=f"{redirect_url}?google_auth=error&detail={urllib.parse.quote(str(e))}")

@router.post("/google/disconnect", status_code=status.HTTP_200_OK)
async def disconnect_google(
    current_user: dict = Depends(get_current_user)
):
    """
    Disconnect Google integration, removing all stored credentials for the user.
    """
    user_id = current_user["user_id"]
    success = await action_agent.impl.email_tool.oauth_service.disconnect(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account not connected or already disconnected"
        )
    return {"status": "success", "message": "Google account disconnected successfully"}

@router.get("/google/status", status_code=status.HTTP_200_OK)
async def google_connection_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Check if Google OAuth is connected for the user.
    """
    user_id = current_user["user_id"]
    creds = await action_agent.impl.email_tool.oauth_service.get_valid_credentials(user_id)
    return {
        "connected": creds is not None,
       "is_mock": bool(creds and creds.get("is_mock")),
        "connected_at": creds.get("connected_at") if creds else None
    }

# ==========================================
# STYLE PROFILES (LEARNED WRITING STYLES)
# ==========================================

@router.post("/style/generate", status_code=status.HTTP_200_OK)
async def generate_user_style_profiles(
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze the user's sent emails using an LLM to generate distinct writing style profiles.
    Reads sent emails from MongoDB (collection: ACTION_SENT_EMAILS), runs LLM analysis,
    and saves the resulting profiles to MongoDB — collection: ACTION_STYLE_PROFILES.
    Falls back to a default set of profiles if no sent emails exist.
    """
    user_id = current_user["user_id"]
    try:
        profiles = await action_agent.impl.email_tool.generate_style_profiles_from_sent(user_id)
        return {
            "status": "success",
            "message": f"Successfully generated {len(profiles)} style profile(s) for the user",
            "profiles": profiles
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate style profiles: {str(e)}"
        )

@router.get("/style/profiles", status_code=status.HTTP_200_OK)
async def get_all_style_profiles(
    current_user: dict = Depends(get_current_user)
):
    """
    List all LLM-generated writing style profiles for the user.
    Profiles are retrieved from MongoDB — collection: ACTION_STYLE_PROFILES.
    """
    user_id = current_user["user_id"]
    try:
        profiles = await action_agent.impl.action_repo.list_style_profiles(user_id)
        return {"profiles": profiles}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/style/profiles/{style_name}", status_code=status.HTTP_200_OK)
async def get_specific_style_profile(
    style_name: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve a specific LLM-generated writing style profile by name.
    Profile is fetched from MongoDB — collection: ACTION_STYLE_PROFILES.
    """
    user_id = current_user["user_id"]
    profile = await action_agent.impl.action_repo.get_style_profile(user_id, style_name)
    if not profile or profile.get("style_name") != style_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Style profile '{style_name}' not found"
        )
    return profile

@router.delete("/style/profiles/{style_name}", status_code=status.HTTP_200_OK)
async def delete_specific_style_profile(
    style_name: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a specific LLM-generated writing style profile by name.
    Profile is removed from MongoDB — collection: ACTION_STYLE_PROFILES.
    """
    user_id = current_user["user_id"]
    success = await action_agent.impl.action_repo.delete_style_profile(user_id, style_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Style profile '{style_name}' not found or could not be deleted"
        )
    return {"status": "success", "message": f"Style profile '{style_name}' deleted successfully"}