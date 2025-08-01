
# Shopping Analytics Project

## Backend
- Built with FastAPI.
- Accepts POST requests from browser extensions to log analytics events.
- Serves data for dashboard analytics.

## Analyst Dashboard
- Simple Python Tkinter-based app.
- Loads and plots analytics data from CSV.
- Supports future expansion.

## How to Run
1. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

2. Start backend:
```bash
uvicorn new-backend.main:app --reload
```


