from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from . import ai_core
from . import schemas
import os

# Directories
web_dir = os.path.join(os.path.dirname(__file__), "..", "web")
static_dir = os.path.join(web_dir, "static")

# App
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Root page
@app.get("/")
async def root():
    return FileResponse(os.path.join(web_dir, "index.html"))

# Create a new user account
@app.post("/api/register")
async def register():
    return

# Login a user the their account
@app.post("/api/login")
async def login():
    return

# Let a user log out of their account
@app.post("/api/logout")
async def logout():
    return

# Tells the page whether it’s signed in; call it on page load
@app.get("/api/me")
async def me():
    return

# List the user's chats on the sidebar
@app.get("/api/chats")
async def get_chats():
    return

# Create a new chat
@app.post("/api/chats")
async def create_chat():
    return

# Load chat history
@app.get("/api/chats/{id}")
async def get_messages():
    return

# Send a message to the AI, stream the response, save both to the database
@app.post("/api/chats/{id}/messages")
async def respond(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    model = data.get("model", "")
    thinking = data.get("thinking", "")

    # Get the AI response stream as generator object
    stream = ai_core.Response(data, model, thinking)
    return StreamingResponse(stream, media_type="application/x-ndjson")

# A guest method that sends the entire chat history and doesn't save anything to the database
@app.post("/api/guest/respond")
async def guest_respond(guest_request: schemas.GuestChatRequest):
    data = guest_request.messages
    history = [message.model_dump() for message in data]
    model = guest_request.model
    thinking = guest_request.thinking

    # Get the AI response stream as generator object
    stream = ai_core.Response(history, model, thinking)
    return StreamingResponse(stream, media_type="application/x-ndjson")