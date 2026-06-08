from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal, List

class ActionIntent(BaseModel):
    type: Literal[
        "draft_email",
        "send_email",
        "send_email_direct",
        "summarize_inbox",
        "create_event",
        "reschedule_event",
        "delete_event",
        "list_calendar",
        "list_inbox",
        "get_recommendations",
        "proactive_action"
    ]

    context: Optional[Dict[str, Any]] = None

    # Email fields
    to: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None

    # Calendar fields
    event_id: Optional[str] = None
    title: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None

    style_profile: Optional[Dict[str, Any]] = None

# ==========================================
# API Payload Schemas
# ==========================================

class ExecuteRequest(BaseModel):
    query: str

class EmailDraftRequest(BaseModel):
    to: str
    topic: str
    message_details: str
    style_profile_override: Optional[Dict[str, Any]] = None
    style_name: Optional[str] = None

class EmailSendRequest(BaseModel):
    to: str
    subject: str
    body: str

class EmailSendEnhancedRequest(BaseModel):
    to: str
    subject: str
    body: str
    query_request: Optional[str] = None
    style_name: Optional[str] = None

class CalendarEventCreate(BaseModel):
    title: str
    start: str  # ISO Format preferred
    end: str    # ISO Format preferred
    description: Optional[str] = None

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    description: Optional[str] = None

class StyleProfileSchema(BaseModel):
    tone: Optional[str] = "neutral"
    signature: Optional[str] = ""
    formatting: Optional[str] = "paragraphs"
    recurring_phrases: Optional[List[str]] = Field(default_factory=list)

class NotificationCreate(BaseModel):
    message: str
    level: Optional[Literal["info", "warning", "critical"]] = "info"