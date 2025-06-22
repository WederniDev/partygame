from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import sqlite3
import string
import random




app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)

async def root():
    index_file = Path("static/index.html").read_text()
    return HTMLResponse(content=index_file, status_code=200)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

@app.post("/create_room")
async def create_room(request: Request):
    data = await request.json()
    host_name = data["name"]
    room_code = generate_room_code()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO rooms (room_code, host_name) VALUES (?, ?)", (room_code, host_name))
    cur.execute("INSERT INTO players (room_code, player_name) VALUES (?, ?)", (room_code, host_name))
    conn.commit()
    conn.close()

    return {"room_code": room_code}

@app.post("/join_room")
async def join_room(request: Request):
    data = await request.json()
    name = data["name"]
    room_code = data["room_code"]

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM rooms WHERE room_code = ?", (room_code,))
    if cur.fetchone() is None:
        conn.close()
        return {"error": "Room does not exist"}

    cur.execute("INSERT INTO players (room_code, player_name) VALUES (?, ?)", (room_code, name))
    conn.commit()
    conn.close()

    return {"joined": True}

@app.get("/players/{room_code}")
async def get_players(room_code: str):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT player_name FROM players WHERE room_code = ?", (room_code,))
    players = [row[0] for row in cur.fetchall()]
    conn.close()
    return {"players": players}
