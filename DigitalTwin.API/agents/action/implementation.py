import json
import re
from datetime import datetime
from database.mongo.repositories.action_repo import ActionRepository
from database.mongo.repositories.medical_repo import MedicalRepository
from database.mongo.collections import Collections
from tools.email_tool import EmailTool
from tools.calendar_tool import CalendarTool
from tools.notification_tool import NotificationTool
from agents.action.schema import ActionIntent
from core.llm.groq_llama_client import get_llm
from agents.action.prompts import SELECT_ACTION_TYPES_PROMPT, EXTRACT_ACTION_FIELDS_PROMPT, PROACTIVE_REACTION_PROMPT
from database.mongo.connection import mongo
from datetime import datetime, timedelta, timezone

ACTION_SCHEMAS = {
    "draft_email": {
        "fields_schema": """- to (string, optional): Recipient email address or name.
- context (object, optional): A dictionary containing:
  - topic (string): The topic/subject of the email.
  - message (string): The description/details of what to write.
  - style_name (string, optional): Selected style profile name.""",
        "examples": """Description: "draft email to Dr. Smith about my back pain"
JSON:
{
  "type": "draft_email",
  "to": "Dr. Smith",
  "context": {"topic": "Back pain update", "message": "Draft email describing my back pain and asking for a follow up appointment"}
}"""
    },
    "send_email": {
        "fields_schema": """- to (string): Recipient email address.
- subject (string): Email subject.
- body (string): Email content body.
- context (object, optional): A dictionary containing:
  - query_request (string, optional): Specific styling or content instructions (e.g. "make it polite", "fix grammar").
  - style_name (string, optional): Selected style profile name.""",
        "examples": """Description: "send email to friend@gmail.com with subject Hello and body How are you"
JSON:
{
  "type": "send_email",
  "to": "friend@gmail.com",
  "subject": "Hello",
  "body": "How are you"
}"""
    },
    "send_email_direct": {
        "fields_schema": """- to (string): Recipient email address.
- subject (string): Email subject.
- body (string): Email content body.""",
        "examples": """Description: "send exactly this email to friend@gmail.com with subject Hello and body How are you"
JSON:
{
  "type": "send_email_direct",
  "to": "friend@gmail.com",
  "subject": "Hello",
  "body": "How are you"
}"""
    },
    "summarize_inbox": {
        "fields_schema": "No extra fields needed. Return an empty dictionary or object with just the type.",
        "examples": """Description: "summarize my emails"
JSON:
{
  "type": "summarize_inbox"
}"""
    },
    "create_event": {
        "fields_schema": """- title (string): Title of the event.
- start (string): Start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
- end (string): End time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
- context (object, optional): A dictionary containing:
  - description (string, optional): Calendar event description.""",
        "examples": """Description: "schedule dental appointment tomorrow from 9 to 10 am"
Reference Time: 2026-06-08T08:00:00
JSON:
{
  "type": "create_event",
  "title": "Dental Appointment",
  "start": "2026-06-09T09:00:00",
  "end": "2026-06-09T10:00:00"
}"""
    },
    "reschedule_event": {
        "fields_schema": """- event_id (string): The ID of the event to reschedule.
- start (string): New start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS). mandatory to fill
- end (string): New end time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS). mandatory to fill""",
        "examples": """Description: "reschedule meeting event_123 to next Monday at 3 PM to 4 PM"
Reference Time: 2026-06-08T08:00:00
JSON:
{
  "type": "reschedule_event",
  "event_id": "event_123",
  "start": "2026-06-15T15:00:00",
  "end": "2026-06-15T16:00:00"
}"""
    },
    "delete_event": {
        "fields_schema": """- event_id (string): The ID of the event to delete.""",
        "examples": """Description: "delete calendar event event_456"
JSON:
{
  "type": "delete_event",
  "event_id": "event_456"
}"""
    },
    "list_calendar": {
        "fields_schema": """- start (string, optional): Start window in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
- end (string, optional): End window in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).""",
        "examples": """Description: "list my calendar events for tomorrow"
Reference Time: 2026-06-08T08:00:00
JSON:
{
  "type": "list_calendar",
  "start": "2026-06-09T00:00:00",
  "end": "2026-06-09T23:59:59"
}"""
    },
    "list_inbox": {
        "fields_schema": "No extra fields needed. Return an empty dictionary or object with just the type.",
        "examples": """Description: "list my inbox emails"
JSON:
{
  "type": "list_inbox"
}"""
    },
    "get_recommendations": {
        "fields_schema": "No extra fields needed. Return an empty dictionary or object with just the type.",
        "examples": """Description: "get recommendations"
JSON:
{
  "type": "get_recommendations"
}"""
    },
    "proactive_action": {
        "fields_schema": "No extra fields needed. Return an empty dictionary or object with just the type.",
        "examples": """Description: "run proactive action"
JSON:
{
  "type": "proactive_action"
}"""
    },
"save_notification": {
        "fields_schema": """- message (string): The alert message to save.
- level (string): The severity level of the alert, one of "info", "warning", or "critical".""",
        "examples": """Description: "save an alert with message 'Blood pressure high' and level 'warning'"
JSON:{
  "type": "save_notification",
    "message": "Blood pressure high",
    "level": "warning"
    }"""
}}

class ActionImplementation:
    def __init__(self, services: dict = None):
        self.action_repo = ActionRepository()
        self.medical_repo = MedicalRepository()
        self.email_tool = EmailTool(self.action_repo)
        self.calendar_tool = CalendarTool(self.action_repo)
        self.notification_tool = NotificationTool(self.action_repo)
        self.llm = get_llm()
    async def resolve_event_id(self, user_id: str, query: str, start: str = None, end: str = None) -> str | None:
        """
        Uses LLM to match a natural language query to a calendar event_id.
        """
        print(f"Query: {query}")
        print(f"ZZ start {start} end {end}")

        events = await self.calendar_tool.list_events(user_id, start, end)

        simplified_events = [
            {
                "event_id": e.get("id"),
                "title": e.get("title"),
                "start": e.get("start"),
                "end": e.get("end"),
                "description":e.get("description")
            }
            for e in events
        ]
        print(f"simplified events{simplified_events}")

        prompt = f"""
    You are a calendar event matcher.
    Reference time:{start}
    TASK:
    Find the best matching event_id for the user query.

    STRICT RULES:
    - Use ONLY the provided events
    - Do NOT guess or hallucinate event IDs
    - Match by title, time, or meaning
    - If no match, return null
    - Return ONLY JSON

    OUTPUT FORMAT:
    {{"event_id": "string or null"}}

    User Query:
    {query}

    Events:
    {json.dumps(simplified_events, indent=2)}
    """

        response = self.llm.invoke(prompt)
        print("llm reponse event id", response)
        text = response.content if hasattr(response, "content") else str(response)

        cleaned = self._extract_json(text)

        try:
            result = json.loads(cleaned)
            print(f"LLM resolved event_id: {result.get('event_id')}")
            return result.get("event_id")
        except Exception:
            return None
        
    async def execute(self, user_id: str, action: ActionIntent,query:str) -> dict:
        """
        Executes a pre-structured ActionIntent.
        """
        if action.type in ["reschedule_event", "delete_event"]:
            start = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            end = start + timedelta(days=7)
            action.event_id = await self.resolve_event_id(
                user_id=user_id,
                query=query,
                start = start.isoformat(),
                end = end.isoformat()
            )
            
        if action.type == "draft_email":
            topic = action.context.get("topic", "Update") if action.context else "Update"
            message_details = action.context.get("message", "") if action.context else ""
            style_name = action.context.get("style_name") if action.context else None
            if not style_name and action.style_profile:
                style_name = action.style_profile.get("style_name")
            return await self.email_tool.draft_email(
                user_id=user_id,
                to=action.to,
                topic=topic,
                message_details=message_details,
                style_profile_override=action.style_profile,
                style_name=style_name
            )

        elif action.type == "send_email":
            query_req = action.context.get("query_request") if action.context else None
            style_name = action.context.get("style_name") if action.context else None
            return await self.email_tool.send_email_enhanced(
                user_id=user_id,
                to=action.to,
                subject=action.subject,
                body=action.body,
                query_request=query_req,
                style_name=style_name
            )

        elif action.type == "send_email_direct":
            return await self.email_tool.send_email(
                user_id=user_id,
                to=action.to,
                subject=action.subject,
                body=action.body
            )

        elif action.type == "summarize_inbox":
            emails = await self.email_tool.read_inbox(user_id)
            return self.email_tool.summarize_emails(emails)

        elif action.type == "list_inbox":
            emails = await self.email_tool.read_inbox(user_id)
            return {"emails": emails}

        elif action.type == "create_event":
            desc = action.context.get("description") if action.context else None
            return await self.calendar_tool.create_event(
                user_id=user_id,
                title=action.title,
                start=action.start,
                end=action.end,
                description=desc
            )

        elif action.type == "reschedule_event":
            return await self.calendar_tool.reschedule_event(
                user_id=user_id,
                event_id=action.event_id,
                new_start=action.start,
                new_end=action.end
            )

        elif action.type == "delete_event":
            return await self.calendar_tool.delete_event(
                user_id=user_id,
                event_id=action.event_id
            )

        elif action.type == "list_calendar":
            events = await self.calendar_tool.list_events(user_id, action.start, action.end)
            return {"events": events}

        elif action.type in ["get_recommendations", "proactive_action"]:
            return await self.handle_proactive(user_id)
        elif action.type == "save_notification":
            return await self.notification_tool.save_notification(
                user_id=user_id,
                message=action.message,
                level=action.level
            )

        else:
            raise ValueError(f"Unknown action type: {action.type}")

    async def parse_and_execute(self, user_id: str, query: str) -> dict:
        """
        Parses a natural language instruction using LLM and then executes it.
        """
        current_time_str = datetime.now().isoformat()
        
        # Step 1: Select Action Types
        select_prompt = SELECT_ACTION_TYPES_PROMPT.format(
            current_time=current_time_str,
            user_request=query
        )
        select_response = self.llm.invoke(select_prompt)
        select_text = select_response.content if hasattr(select_response, 'content') else str(select_response)
        print("LLM Action Type Selection Response:", select_text)
        cleaned_select_json = self._extract_json(select_text)
        try:
            actions_to_extract = json.loads(cleaned_select_json)
            if not isinstance(actions_to_extract, list):
                actions_to_extract = [{"type": "draft_email", "description": query}]
        except Exception:
            actions_to_extract = [{"type": "draft_email", "description": query}]

        executed_actions = []
        
        # Step 2: Extract fields and run for each selected action type
        for act in actions_to_extract:
            action_type = act.get("type")
            action_desc = act.get("description", query)
            
            if not action_type or action_type not in ACTION_SCHEMAS:
                continue
                
            schema_info = ACTION_SCHEMAS[action_type]
            fields_schema = schema_info["fields_schema"]
            examples = schema_info["examples"]
            
            extract_prompt = EXTRACT_ACTION_FIELDS_PROMPT.format(
                current_time=current_time_str,
                action_type=action_type,
                action_description=action_desc,
                fields_schema=fields_schema,
                examples=examples
            )
            
            extract_response = self.llm.invoke(extract_prompt)
            extract_text = extract_response.content if hasattr(extract_response, 'content') else str(extract_response)
            cleaned_extract_json = self._extract_json(extract_text)
            
            try:
                intent_dict = json.loads(cleaned_extract_json)
                intent_dict["type"] = action_type
                intent = ActionIntent(**intent_dict)
            except Exception:
                if action_type == "draft_email":
                    intent = ActionIntent(
                        type="draft_email",
                        to="Recipient",
                        context={"topic": "Assistant Resolution", "message": action_desc}
                    )
                else:
                    intent = ActionIntent(type=action_type)
            
            try:
                result = await self.execute(user_id, intent,query)
                executed_actions.append((intent, result))
            except Exception as e:
                executed_actions.append((intent, {"status": "error", "message": str(e)}))

        if not executed_actions:
            fallback_intent = ActionIntent(
                type="draft_email",
                to="Recipient",
                context={"topic": "Assistant Resolution", "message": query}
            )
            fallback_result = await self.execute(user_id, fallback_intent,query)
            return {
                "intent": fallback_intent.dict(),
                "result": fallback_result,
                "actions": [{"intent": fallback_intent.dict(), "result": fallback_result}]
            }

        first_intent, first_result = executed_actions[0]
        return {
            "intent": first_intent.dict(),
            "result": first_result,
            "actions": [
                {"intent": intent.dict(), "result": res} for intent, res in executed_actions
            ]
        }

    async def handle_proactive(self, user_id: str) -> dict:
        """
        Generates proactive action recommendations by checking user health documents and alerts.
        """
        # 1. Fetch user medical documents
        reports = await self.medical_repo.get_user_reports(user_id)
        # with open("C:\\Users\\User\\OneDrive\\Desktop\\4th year\\Semester 8\\mini Project\\agentic project\\Artificial-Personal-Digital-Twin\\DigitalTwin.API\\data\\medical_reports_debug.json", "w", encoding="utf-8") as f:
        #     json.dump(reports, f, indent=2, default=str)       
        
        # 2. Fetch health alerts if any
        db = mongo.get_db()
        alert_cursor = db[Collections.HEALTH_ALERTS].find({"user_id": user_id})
        alerts = await alert_cursor.to_list(length=10)
        # print("Fetched health alerts:", alerts)
        # 3. Construct health context
        health_context = "No medical reports or active alerts found."
        context_parts = []
        if reports:
            context_parts.append("Latest Medical Reports:")
            for r in reports[:2]:
                title = r.get("file_name", "Report")
                analy = r.get("analysis", {})
                analysis=analy.get("analysis", "No analysis available.")
                # print(f"Report analysis for {title}:", analysis)
                summary = analysis.get("summary", "No summary available.") if isinstance(analysis, dict) else "No summary available."
                context_parts.append(f"- {title}: {summary} \n Important Lab results: {analysis.get('key_abnormalities', []) if isinstance(analysis, dict) else 'N/A'}")
                
        if alerts:
            context_parts.append("\nActive Health Alerts:")
            for a in alerts[:3]:
                msg = a.get("message", "Alert")
                severity = a.get("severity", "info")
                context_parts.append(f"- [{severity.upper()}] {msg}")
                
        if context_parts:
            health_context = "\n".join(context_parts)
        print("Constructed health context:", health_context)
        # 4. Invoke LLM to suggest actions
        prompt = PROACTIVE_REACTION_PROMPT.format(current_time=datetime.now().isoformat(), health_context=health_context)
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)

        # 5. Parse JSON list of recommendations
        cleaned_json = self._extract_json(response_text)
        try:
            recommendations = json.loads(cleaned_json)
        except Exception:
            # Fallback default recommendations
            recommendations = [
                {
                    "id": 1,
                    "action_type": "create_event",
                    "title": "Wellness Check & Daily Walk",
                    "reason": "Recommended to keep consistent light physical exercise.",
                    "payload": {
                        "title": "Wellness Walk",
                        "start": datetime.now().replace(hour=17, minute=0, second=0).isoformat(),
                        "end": datetime.now().replace(hour=17, minute=30, second=0).isoformat(),
                        "description": "Daily outdoor walking block."
                    }
                }
            ]

        return {
            "health_context_analyzed": len(reports) > 0 or len(alerts) > 0,
            "recommendations": recommendations
        }

    def _extract_json(self, text: str) -> str:
        """
        Helper to extract JSON substrings from LLM outputs.
        """
        if "```json" in text:
            match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                return match.group(1).strip()
        elif "```" in text:
            match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # Fallback to direct braces match
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if match:
            return match.group(0).strip()
            
        return text.strip()