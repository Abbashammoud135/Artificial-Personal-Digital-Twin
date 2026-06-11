# Digital Twin AI — Frontend Implementation Prompt

## Project Overview

**Digital Twin AI** is a personal AI-powered system that automates your digital life — health monitoring, email, calendar, notifications — all driven by LLMs. Think of it as an AI clone of yourself that acts, thinks, and manages tasks on your behalf.

**Backend**: FastAPI + Python | MongoDB + SQL Server + Redis | Groq LLaMA 3.1 | FAISS RAG | Google OAuth

**Base API URL**: `http://localhost:8000`  
**Auth**: JWT Bearer token in all protected requests (`Authorization: Bearer <token>`)

---

## Design Direction

**Theme**: Dark futuristic — deep navy/dark backgrounds, glowing blue/cyan accents, subtle particle or neural-network ambient animation. Glassmorphism cards. Smooth 3D-like transitions. The app should feel like you're interacting with a living intelligent entity.

**Palette**:
- Background: `#050D1A` (deep space dark)
- Surface cards: `rgba(255,255,255,0.04)` glassmorphism with `backdrop-filter: blur(20px)`
- Primary accent: `#00D4FF` (electric cyan)
- Secondary accent: `#7B61FF` (neural purple)
- Success: `#00F5A0` (neon green)
- Warning: `#FF8C00`
- Danger: `#FF4C6A`
- Text primary: `#E8F4FD`
- Text muted: `#6B8CAE`

**Typography**: Inter for UI, Space Grotesk for headings/display

**Animations**:
- Hero page: animated 3D rotating brain/neural network using Three.js or CSS 3D transforms
- Page transitions: fade + slide-up (150ms)
- Cards: subtle float on hover (translateY -4px, glow shadow)
- Data updates: number counters animating to final values
- Background: ambient floating particles or grid pulse (subtle, not distracting)
- Loading states: pulsing skeleton screens

**Signature element**: Animated "AI pulse" — a breathing glow ring that surrounds the AI command input, expanding when the AI is thinking

---

## Pages & Routes

### 1. `/` — Dashboard (Home)
The mission control of your digital twin.

**Layout**: Full-screen dark hero with animated neural network background (Three.js or SVG animated paths). Center: large greeting "Your Digital Twin is Active" with a pulsing status orb.

**Widgets** (glassmorphism cards in a responsive grid):
- **Health Snapshot**: Latest abnormal count, overall risk score, last report date → links to /health
- **Upcoming Events**: Next 3 calendar events from `/action/calendar/events`
- **Unread Notifications**: Count badge + latest 3 messages from `/action/notifications`
- **AI Command Shortcut**: Mini NL input → sends to `/action/execute`, shows result inline
- **Email Drafts**: Count of pending drafts from `/action/emails/drafts`
- **System Status**: Connected databases indicator (decorative)

---

### 2. `/command` — AI Command Center ⭐ (Main feature page)
The natural language interface to control everything.

**Design**: Fullscreen dark page. Center: large glowing input box with animated "AI pulse" ring around it. When typing, the ring breathes. When submitted, particles animate inward toward the input.

**Input**: Large textarea (placeholder: "Tell your twin what to do... e.g. 'Schedule gym tomorrow 7am' or 'Draft email to Dr. Smith about my results'")

**Submit** → `POST /action/execute` body: `{ "query": "..." }`

**Response display**:
- Animated card slides up showing the parsed intent type (badge: "📅 Calendar Event" / "📧 Email Draft" / etc.)
- Show result details (created event, draft preview, etc.)
- History list below: last 10 commands with results (stored in localStorage)

**Quick Action chips** (pre-filled suggestions):
- "List my inbox" → `POST /action/execute` `{ "query": "list my inbox" }`
- "What are my events today?"
- "Send me my health summary"
- "Draft email to my doctor"
- "Get proactive recommendations"

---

### 3. `/health` — Health Intelligence
Your AI-powered medical dashboard.

**Sections**:

**A) Upload & Analyze** (top)
- Drag-and-drop zone for PDF upload OR textarea for text note
- `POST /health-docs/upload` (multipart: `file` or `note` field)
- Then `POST /health-agent/analyze` for instant analysis
- Show animated progress: Extracting → Analyzing → Done
- Result card: summary, key_abnormalities list, recommendations, risk scores (animated circular progress bars for cardiovascular/metabolic/general 0–1)

**B) Ask Your Health Agent** 
- Input: "Ask anything about your health..."
- `POST /health-agent/ask` body: `{ "question": "..." }`
- Response shown in chat-bubble style

**C) Lab Trends** (chart section)
- `GET /health-trends/` → render line charts per test using Chart.js or Recharts
- Trend badge: STABLE (blue) / INCREASING (red) / DECREASING (green)
- Show latest value, min, max, avg per test

**D) All Reports**
- `GET /health-docs/reports` → paginated cards
- Each card: file_type icon, upload date, status badge (analyzed/uploaded), click to expand analysis

**E) Health Profile**
- `GET /health-profile/` → editable form
- `PUT /health-profile/` on save
- Fields: birthdate, gender, height, weight, BMI (auto-calc), blood_type, chronic_conditions, lifestyle, stress_level (slider 1–10), sleep_hours

**F) Dashboard summary strip**
- `GET /health-docs/dashboard` → total_reports, analyzed_reports, anomaly_count, recent_insights

---

### 4. `/automate` — Automation Hub
All automation tools in one tabbed interface.

**Tabs**: Emails | Calendar | Notifications | Style Profiles | Recommendations

#### Tab: Emails
- **Inbox** button → `GET /action/emails/inbox` → list cards (from, subject, date)
- **Draft Email** form: to, topic, message_details, style_name (select) → `POST /action/emails/draft`
- **Drafts list** → `GET /action/emails/drafts` → cards with Edit / Delete / Send actions
  - Send draft → `POST /action/emails/send` with draft fields
  - Send Enhanced → `POST /action/emails/send-enhanced`
- **Sent log** → `GET /action/emails/sent`

#### Tab: Calendar
- **Events list** → `GET /action/calendar/events?startTime=...&endTime=...` → timeline view
- **Create Event** form: title, start, end (datetime pickers), description → `POST /action/calendar/events`
- Edit event → `PUT /action/calendar/events/{id}`
- Delete → `DELETE /action/calendar/events/{id}`

#### Tab: Notifications
- List → `GET /action/notifications` → cards with level badge (info/warning/critical)
- Create → `POST /action/notifications` body: `{ "message": "...", "level": "info" }`

#### Tab: Style Profiles
- List → `GET /action/style/profiles`
- Generate from sent emails → `POST /action/style/generate` (shows loading + result)
- Manual profile → `GET /action/style-profile` / `POST /action/style-profile`
- Each profile card shows: tone, signature preview, formatting, recurring phrases chips
- Delete → `DELETE /action/style/profiles/{name}`

#### Tab: Recommendations
- `GET /action/proactive/recommendations` → animated recommendation cards
- Each card: action_type badge, title, reason, payload preview
- "Execute this" button → `POST /action/execute-intent` with the recommendation's intent

---

### 5. `/settings` — Settings & Integrations

**Sections**:

**A) Google Integration**
- Status → `GET /action/google/status` → show Connected / Disconnected with badge
- Connect → `GET /action/google/connect` → redirect to returned authorization_url
- Disconnect → `POST /action/google/disconnect`

**B) Account**
- Display user info from JWT decode (email, role)
- Logout (clear token from localStorage)

**C) AI Command history** — clear localStorage history button

---

## Auth Pages

### `/login`
- `POST /auth/login` body: `{ "email": "...", "password": "..." }`
- On success: store `access_token` in localStorage, redirect to `/`

### `/register`
- `POST /auth/register` body: `{ "full_name": "...", "email": "...", "password": "..." }`
- On success: redirect to `/login`

---

## API Reference (All Endpoints Used)

### Auth
| Method | Endpoint | Body |
|--------|----------|------|
| POST | /auth/register | `{full_name, email, password}` |
| POST | /auth/login | `{email, password}` → returns `{access_token}` |

### Health Profile
| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | /health-profile/ | Returns profile object |
| POST | /health-profile/ | Create profile |
| PUT | /health-profile/ | Update profile |

### Health Data
| Method | Endpoint | Notes |
|--------|----------|-------|
| POST | /health-docs/upload | multipart: `file` (PDF) or `note` (text) |
| GET | /health-docs/reports | Returns array of documents |
| POST | /health-docs/analyze | multipart: `file` or `note` → returns analysis |
| GET | /health-docs/dashboard | Returns stats summary |
| GET | /health-trends/ | Returns trends per test name |
| POST | /health-agent/ask | `{question: string}` |
| POST | /health-agent/analyze | multipart: `file` or `note` |

### Planner
| Method | Endpoint | Notes |
|--------|----------|-------|
| POST | /api/v1/planner/plan | `{request: string}` → returns plan with tasks |

### Memory
| Method | Endpoint | Notes |
|--------|----------|-------|
| POST | /memory/memory/query | `{query: string}` → NL answer from medical history |

### Action Agent
| Method | Endpoint | Notes |
|--------|----------|-------|
| POST | /action/execute | `{query: string}` → execute NL command |
| POST | /action/execute-intent | Full ActionIntent JSON |
| GET | /action/emails/inbox | Optional `?query=filter` |
| POST | /action/emails/draft | `{to, topic, message_details, style_name?}` |
| GET | /action/emails/drafts | Returns array |
| GET | /action/emails/drafts/{id} | Single draft |
| PUT | /action/emails/drafts/{id} | `{to, subject, body}` |
| DELETE | /action/emails/drafts/{id} | — |
| POST | /action/emails/send | `{to, subject, body}` |
| POST | /action/emails/send-enhanced | `{to, subject, body, query_request?, style_name?}` |
| GET | /action/emails/sent | Returns array |
| GET | /action/calendar/events | Optional `?startTime=&endTime=` |
| POST | /action/calendar/events | `{title, start, end, description?}` |
| PUT | /action/calendar/events/{id} | `{title?, start?, end?, description?}` |
| DELETE | /action/calendar/events/{id} | — |
| GET | /action/notifications | Returns array |
| POST | /action/notifications | `{message, level: info|warning|critical}` |
| GET | /action/style-profile | Manual style profile |
| POST | /action/style-profile | `{tone, signature, formatting, recurring_phrases[]}` |
| POST | /action/style/generate | Auto-generate from sent history |
| GET | /action/style/profiles | All AI-generated profiles |
| GET | /action/style/profiles/{name} | Single profile |
| DELETE | /action/style/profiles/{name} | — |
| GET | /action/proactive/recommendations | Returns recommendations array |
| GET | /action/google/connect | Returns `{authorization_url}` |
| GET | /action/google/callback | Handles OAuth redirect (backend) |
| POST | /action/google/disconnect | — |
| GET | /action/google/status | Returns `{connected, is_mock, connected_at}` |

---

## Key Data Shapes

### Analysis result (from /health-agent/analyze or /health-docs/analyze)
```json
{
  "file_id": "uuid",
  "user_id": "string",
  "file_type": "pdf|text",
  "status": "analyzed",
  "analysis": {
    "summary": "string",
    "cardiovascular_risk": "string",
    "metabolic_risk": "string",
    "key_abnormalities": ["string"],
    "recommendations": ["string"],
    "insights": ["string"],
    "rag_references": ["string"]
  }
}
```

### Trend (from /health-trends/)
```json
{
  "user_id": "string",
  "trends": {
    "testname": {
      "test_name": "string", "units": "string",
      "trend": "STABLE|INCREASING|DECREASING",
      "latest_value": 0, "min": 0, "max": 0, "avg": 0,
      "points": [{"date": "ISO", "value": 0, "status": "NORMAL|HIGH|LOW"}]
    }
  }
}
```

### Action execute result
```json
{
  "intent": { "type": "draft_email|create_event|...", "to": "...", ... },
  "result": { ... },
  "actions": [{ "intent": {...}, "result": {...} }]
}
```

### Calendar event
```json
{ "_id": "string", "title": "string", "start": "ISO", "end": "ISO", "description": "string" }
```

### Email draft
```json
{ "_id": "string", "to": "string", "subject": "string", "body": "string", "created_at": "ISO" }
```

### Style profile
```json
{ "style_name": "string", "tone": "string", "signature": "string", "formatting": "string", "recurring_phrases": ["string"] }
```

### Proactive recommendation
```json
{ "id": 1, "action_type": "create_event|draft_email|...", "title": "string", "reason": "string", "payload": {...} }
```

---

## Implementation Notes

- Store JWT in `localStorage` as `dt_token`. Attach as `Authorization: Bearer <token>` header on all protected calls.
- On 401 response → clear token and redirect to `/login`.
- Use React Router for navigation. Suggested stack: **React + Vite + Tailwind CSS + Framer Motion + Three.js (hero only) + Recharts (health charts)**.
- Sidebar navigation: icons + labels, collapsible on mobile.
- Nav items: Dashboard | Command Center | Health | Automate | Settings
- Show a global loading indicator when any API call is in-flight.
- Toast notifications for success/error feedback on all mutations.
- The `/command` page is the flagship — make the AI input feel alive and powerful.
