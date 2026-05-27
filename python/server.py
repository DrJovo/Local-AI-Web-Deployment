from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from . import AICore
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

# AI response endpoint
@app.post("/api/respond")
async def respond(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    response = AICore.Response(prompt)
    return {
        "response": response
    }