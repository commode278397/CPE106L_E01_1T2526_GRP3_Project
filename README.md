# SkillBridge

A minimal FastAPI + SQLite backend with two frontends:
- Browser UI (index.html served by FastAPI)
- Flet desktop/web app (ui.py)

It lets you:
- Register volunteers
- Offer skills
- Create help requests
- Accept a request (match a volunteer)
- Cancel a request

SQLite is used for persistence (SkillBridge.db in the project folder).

## Quick Start

1) Install dependencies
```
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

2) Run the API
```
uvicorn main:app --reload
```

3) Open the web UI
- Visit http://127.0.0.1:8000/ in your browser.
- Alternatively, run the Flet UI:
  ```
  python ui.py
  ```
  This opens a Flet app that calls the same API.

Notes:
- The database file SkillBridge.db is created automatically.
- To reset data, stop the server and delete SkillBridge.db.

## API Overview

Base URL: http://127.0.0.1:8000

- Health
  - GET /health → { "status": "ok" }

- Users
  - POST /users → Create user {name, email, skills?}
  - GET /users → List users

- Requests
  - POST /requests → Create request {title, description?, required_skills?, requester_name, location}
  - GET /requests → List requests
  - POST /requests/{id}/accept → Accept/match a volunteer {volunteer_id}
  - POST /requests/{id}/cancel → Cancel request

- Volunteer Skills
  - POST /volunteers/{user_id}/skills → Offer a skill {skill}
  - GET /volunteers/{user_id}/skills → Combined skills from profile + offerings

- Extras (simple, optional)
  - GET /requests/{id}/recommendations?top_n=5 → naive volunteer suggestions based on skill overlap
  - GET /analytics/summary → counts and top skills

All endpoints return JSON and use standard HTTP error codes.

## Using the Web UI (index.html)

- Open http://127.0.0.1:8000/
- Use the navigation buttons:
  - Register Volunteer
  - Offer Skill
  - Create Request
  - Accept Request
  - Cancel Request
- Messages are shown inline under each form.

Tips:
- After registering a volunteer, note their ID for later actions.
- Only open requests can be matched; cancelling locks them.

## Using the Flet App (ui.py)

- With the API running: `python ui.py`
- The app opens in a browser window (or as a desktop window) and presents the same flows.
- It uses the same endpoints at http://127.0.0.1:8000

## Data Model (SQLite)

Tables:
- users(id, name, email UNIQUE, skills TEXT)
- requests(id, title, description, required_skills, requester_name, location, status ['open'|'matched'|'cancelled'])
- volunteer_skills(id, user_id → users.id, skill, created_at)
- request_assignments(id, request_id → requests.id, volunteer_id → users.id, status, accepted_at)

The table `requests` automatically gains `location` and `status` columns if missing (backward compatible schema migration).

## Minimal Matching and Analytics

To align with the project proposal (without heavy dependencies):
- GET /requests/{id}/recommendations ranks volunteers by overlap with the request’s `required_skills`.
- GET /analytics/summary summarizes counts and top volunteer skills from profile and offered skills.

These are simple baseline features suitable for a student project; you can extend them with distance-based scoring, scheduling, or completed-match history.

## Troubleshooting

- ImportError: email-validator is required for Pydantic EmailStr.
  - Ensure `pip install email-validator` (included in requirements.txt).

- CORS issues when opening index.html directly from your filesystem:
  - The API already enables permissive CORS, but opening the page from the API (http://127.0.0.1:8000/) is recommended.

- Database locked / in use:
  - Close any tools/browser tabs that may lock the SQLite file. Retry after stopping and restarting the server.

## Project Structure

```
.
├─ main.py           # FastAPI app (serves index.html)
├─ database.py       # SQLite schema and connection helpers
├─ ui.py             # Flet-based UI (optional)
├─ index.html        # Browser UI
├─ requirements.txt  # Python dependencies
└─ SkillBridge.db    # Created at runtime
```

## Stretch Ideas

- Use Google Maps or OpenStreetMap to geocode addresses and rank by proximity.
- Add “complete” and “rate” flows and track MatchHistory.
- Visualize trends with Matplotlib (e.g., skill demand, engagement).