# main.py

from typing import List, Optional
import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

import database  # our database.py


# ---------- Pydantic Models ----------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    skills: Optional[str] = None  # e.g. "tutoring, carpentry"


class User(UserCreate):
    id: int


class RequestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    required_skills: Optional[str] = None
    requester_name: str


class Request(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    required_skills: Optional[str] = None
    requester_name: str


# ---------- FastAPI App ----------

app = FastAPI(title="SkillBridge API - Minimal Demo")


@app.on_event("startup")
def on_startup():
    # Create tables when the API starts
    database.init_db()


# ---------- User Endpoints ----------

@app.post("/users", response_model=User)
def create_user(user: UserCreate):
    conn = database.get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, email, skills) VALUES (?, ?, ?)",
            (user.name, user.email, user.skills),
        )
        conn.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered.")
    conn.close()
    return User(id=user_id, **user.dict())


@app.get("/users", response_model=List[User])
def list_users():
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, skills FROM users")
    rows = conn.cursor().fetchall() if False else cur.fetchall()  # just to be explicit
    conn.close()

    users = [
        User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            skills=row["skills"],
        )
        for row in rows
    ]
    return users


# ---------- Request Endpoints ----------

@app.post("/requests", response_model=Request)
def create_request(req: RequestCreate):
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO requests (title, description, required_skills, requester_name)
        VALUES (?, ?, ?, ?)
        """,
        (req.title, req.description, req.required_skills, req.requester_name),
    )
    conn.commit()
    request_id = cur.lastrowid
    conn.close()

    return Request(id=request_id, **req.dict())


@app.get("/requests", response_model=List[Request])
def list_requests():
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, title, description, required_skills, requester_name
        FROM requests
        """
    )
    rows = cur.fetchall()
    conn.close()

    requests = [
        Request(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            required_skills=row["required_skills"],
            requester_name=row["requester_name"],
        )
        for row in rows
    ]
    return requests
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
