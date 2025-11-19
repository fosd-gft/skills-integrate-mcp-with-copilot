"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize persistent storage (SQLite via SQLAlchemy)
from server import init_db, get_activities_dict, signup as db_signup, unregister as db_unregister

# Initialize the database (creates `data/app.db` by default)
init_db()



@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return get_activities_dict()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    try:
        return db_signup(activity_name, email)
    except KeyError:
        raise HTTPException(status_code=404, detail="Activity not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    try:
        return db_unregister(activity_name, email)
    except KeyError:
        raise HTTPException(status_code=404, detail="Activity not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
