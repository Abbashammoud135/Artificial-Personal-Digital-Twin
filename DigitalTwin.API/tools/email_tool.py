import datetime
from database.mongo.repositories.action_repo import ActionRepository
from core.llm.groq_llama_client import get_llm
from agents.action.prompts import EMAIL_DRAFTING_PROMPT
from services.google.oauth_service import GoogleOAuthService
from services.google.gmail_service import GoogleGmailService

class EmailTool:
    def __init__(self, action_repo: ActionRepository = None):
        self.repo = action_repo or ActionRepository()
        self.llm = get_llm()
        self.oauth_service = GoogleOAuthService()
        self.google_gmail_service = GoogleGmailService()
        
        # Keep a rich mock inbox for read_inbox fallback
        self.mock_inbox = [
            {
                "id": "inbox_1",
                "from": "professor@university.com",
                "subject": "Assignment Deadline Extension",
                "body": "Hi student, just letting you know the deadline for the final project has been extended to next Monday at midnight. Let me know if you have any questions.",
                "date": str(datetime.datetime.now() - datetime.timedelta(hours=2))
            },
            {
                "id": "inbox_2",
                "from": "bank@system.com",
                "subject": "Monthly Statement Updated",
                "body": "Your bank account statement for May 2026 is now available. Log in to your online banking app to view it. Please note your balance has been updated.",
                "date": str(datetime.datetime.now() - datetime.timedelta(days=1))
            },
            {
                "id": "inbox_3",
                "from": "dr.smith@clinic.com",
                "subject": "Lab Results Review",
                "body": "Dear patient, your latest laboratory tests look great. However, your vitamin D is slightly low. I recommend taking a daily supplement of 2000 IU. Let's discuss this next visit.",
                "date": str(datetime.datetime.now() - datetime.timedelta(days=2))
            }
        ]

    # -------------------------
    # READ INBOX
    # -------------------------
    async def read_inbox(self, user_id: str, query: str = None) -> list:
        creds = await self.oauth_service.get_valid_credentials(user_id)
        if creds:
            # Route to real Google Gmail API
            return await self.google_gmail_service.list_messages(creds["access_token"], query)

        # Local mock fallback
        if query:
            return [
                email for email in self.mock_inbox
                if query.lower() in email["subject"].lower()
                or query.lower() in email["body"].lower()
            ]
        return self.mock_inbox

    # -------------------------
    # SUMMARIZE INBOX
    # -------------------------
    def summarize_emails(self, emails):
        return {
            "count": len(emails),
            "summary": [
                {
                    "from": e["from"],
                    "subject": e["subject"],
                    "date": e["date"]
                }
                for e in emails
            ]
        }

    # -------------------------
    # DRAFT EMAIL (LLM-BASED WITH STYLE SIMULATION)
    # -------------------------
    async def draft_email(self, user_id: str, to: str, topic: str, message_details: str, style_profile_override: dict = None, style_name: str = None) -> dict:
        # 1. Fetch style profile
        profile = style_profile_override
        if not profile:
            profile = await self.repo.get_style_profile(user_id, style_name)
        if not profile:
            # Fallback default profile
            profile = {
                "tone": style_name or "neutral",
                "signature": "\nBest regards,\nAbbas Hammoud",
                "formatting": "paragraphs",
                "recurring_phrases": []
            }

        # 2. Render prompt
        prompt = EMAIL_DRAFTING_PROMPT.format(
            tone=profile.get("tone", "neutral"),
            signature=profile.get("signature", ""),
            formatting=profile.get("formatting", "paragraphs"),
            recurring_phrases=", ".join(profile.get("recurring_phrases", [])),
            to=to,
            topic=topic,
            message_details=message_details
        )

        # 3. Call LLM
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)

        # 4. Parse response into subject & body
        subject, body = self._parse_draft_response(response_text, topic)

        # 5. Save draft to MongoDB
        draft_dict = {
            "to": to,
            "subject": subject,
            "body": body,
            "context": {
                "topic": topic,
                "message_details": message_details
            }
        }
        saved_draft = await self.repo.save_email_draft(user_id, draft_dict)
        return saved_draft

    def _parse_draft_response(self, text: str, default_topic: str) -> tuple:
        subject = f"Regarding {default_topic}"
        body = text.strip()

        # Remove markdown block if model output code blocks
        if "```" in text:
            import re
            text = re.sub(r"```[a-zA-Z]*|```", "", text).strip()

        lines = text.split("\n")
        
        # Check for Subject lines
        subject_line_idx = -1
        body_start_idx = -1
        
        for idx, line in enumerate(lines):
            if line.lower().startswith("subject:"):
                subject_line_idx = idx
            elif line.lower().startswith("body:"):
                body_start_idx = idx
                
        if subject_line_idx != -1:
            subject = lines[subject_line_idx].split(":", 1)[1].strip()
            
        if body_start_idx != -1:
            body = "\n".join(lines[body_start_idx+1:]).strip()
        elif subject_line_idx != -1:
            # If Subject was found but no "Body:" label, body is everything after subject
            body = "\n".join(lines[subject_line_idx+1:]).strip()
            
        return subject, body

    # -------------------------
    # SEND EMAIL (MOCK TRANSMISSION OR REAL GMAIL API)
    # -------------------------
    async def send_email(self, user_id: str, to: str, subject: str, body: str) -> dict:
        creds = await self.oauth_service.get_valid_credentials(user_id)
        
        if creds:
            # Send using real Google Gmail API
            res = await self.google_gmail_service.send_message(creds["access_token"], to, subject, body)
            email_log = {
                "to": to,
                "subject": subject,
                "body": body,
                "google_message_id": res.get("id"),
                "status": "sent"
            }
            db_res = await self.repo.save_sent_email(user_id, email_log)
            return {
                "status": "success",
                "source": "google_gmail",
                "email": db_res
            }

        # Local storage / mock fallback
        email = {
            "to": to,
            "subject": subject,
            "body": body,
            "status": "sent"
        }
        res = await self.repo.save_sent_email(user_id, email)
        return {
            "status": "success",
            "source": "local_database",
            "message": "Email sent successfully (mock transmission, fully logged)",
            "email": res
        }

    async def send_email_enhanced(
        self,
        user_id: str,
        to: str,
        subject: str,
        body: str,
        query_request: str = None,
        style_name: str = None
    ) -> dict:
        # 1. Fetch style profile
        profile = await self.repo.get_style_profile(user_id, style_name)
        if not profile:
            profile = {
                "tone": style_name or "neutral",
                "signature": "\nBest regards,\nAbbas Hammoud",
                "formatting": "paragraphs",
                "recurring_phrases": []
            }
        print(f"to:{to}, subject:{subject}, body:{body}, style_name:{style_name}")

        # 2. Render prompt
        from agents.action.prompts import EMAIL_ENHANCEMENT_PROMPT
        prompt = EMAIL_ENHANCEMENT_PROMPT.format(
            tone=profile.get("tone", "neutral"),
            signature=profile.get("signature", ""),
            formatting=profile.get("formatting", "paragraphs"),
            recurring_phrases=", ".join(profile.get("recurring_phrases", [])),
            query_request=query_request or "Fix grammar and match user style",
            subject=subject,
            body=body
        )

        # 3. Call LLM
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        # print("LLM Email Enhancement Response:", response_text)

        # 4. Parse response into subject & body
        enhanced_subject, enhanced_body = self._parse_draft_response(response_text, subject)

        # 5. Send enhanced email
        return await self.send_email(user_id, to, enhanced_subject, enhanced_body)

    async def list_sent(self, user_id: str) -> list:
        return await self.repo.list_sent_emails(user_id)

    async def list_drafts(self, user_id: str) -> list:
        return await self.repo.list_email_drafts(user_id)

    async def generate_style_profiles_from_sent(self, user_id: str) -> list:
        # 1. Fetch sent emails
        sent_emails = await self.repo.list_sent_emails(user_id)
        
        # 2. Check if we have emails to analyze
        if not sent_emails:
            # Fallback default style profiles
            default_profiles = [
                {
                    "style_name": "professional",
                    "tone": "formal, professional and polite",
                    "signature": "\nBest regards,\nAbbas Hammoud",
                    "formatting": "paragraphs",
                    "recurring_phrases": ["Please find attached", "Let me know if you need anything else", "Thank you for your time"]
                },
                {
                    "style_name": "casual",
                    "tone": "friendly, warm and casual",
                    "signature": "\nCheers,\nAbbas Hammoud",
                    "formatting": "paragraphs",
                    "recurring_phrases": ["hope you're doing well", "talk soon", "catch you later"]
                },
                {
                    "style_name": "concise",
                    "tone": "brief, direct and urgent",
                    "signature": "",
                    "formatting": "one-liners or short paragraphs",
                    "recurring_phrases": ["urgent", "quick update", "FYI"]
                }
            ]
            # Save these defaults to database
            for p in default_profiles:
                await self.repo.save_style_profile(user_id, p)
            return default_profiles

        # 3. Format sent emails for prompt
        emails_text_list = []
        for idx, email in enumerate(sent_emails[:15]): # analyze up to 15 latest sent emails
            emails_text_list.append(
                f"Email {idx+1}:\nTo: {email.get('to')}\nSubject: {email.get('subject')}\nBody:\n{email.get('body')}\n---"
            )
        sent_emails_text = "\n\n".join(emails_text_list)

        # 4. Render prompt
        from agents.action.prompts import STYLE_ANALYSIS_PROMPT
        prompt = STYLE_ANALYSIS_PROMPT.format(sent_emails_text=sent_emails_text)

        # 5. Call LLM
        response = self.llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)

        # 6. Parse response
        import re
        import json
        
        # Extract JSON
        if "```json" in response_text:
            match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
            if match:
                response_text = match.group(1).strip()
        elif "```" in response_text:
            match = re.search(r"```\s*(.*?)\s*```", response_text, re.DOTALL)
            if match:
                response_text = match.group(1).strip()
        
        # Fallback to direct brackets match
        match = re.search(r"(\[.*\])", response_text, re.DOTALL)
        if match:
            response_text = match.group(0).strip()
            
        try:
            profiles = json.loads(response_text)
            if not isinstance(profiles, list):
                profiles = [profiles]
        except Exception:
            # Fallback if parsing fails
            profiles = [
                {
                    "style_name": "learned_style",
                    "tone": "neutral and direct",
                    "signature": "\nBest regards,\nAbbas Hammoud",
                    "formatting": "paragraphs",
                    "recurring_phrases": []
                }
            ]

        # 7. Save each style profile to MongoDB
        saved_profiles = []
        for profile in profiles:
            saved = await self.repo.save_style_profile(user_id, profile)
            saved_profiles.append(saved)
            
        return saved_profiles